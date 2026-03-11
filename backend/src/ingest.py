"""
Ingestion Utility for uploaded documents
"""
from langchain_setup import driver, get_llm_models
import json
import uuid
import re
import os
from typing import List, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from retrieve import generate_initial_analysis
import spacy
import text_processor as tp

nlp = spacy.load("en_core_web_sm")
TRIPLE_PATTERN = re.compile(r"^\(.+?,.+?,.+?\)$")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


ENABLE_ANALYSIS_CACHE = _env_bool("ENABLE_ANALYSIS_CACHE", True)
CLOUD_BATCH_SIZE = _env_int("CLOUD_BATCH_SIZE", 10)
CLOUD_MAX_WORKERS = _env_int("CLOUD_MAX_WORKERS", 4)
CLOUD_BATCH_PAUSE_SECONDS = _env_int("CLOUD_BATCH_PAUSE_SECONDS", 60)
LOCAL_MAX_WORKERS = _env_int("LOCAL_MAX_WORKERS", 16)
CHUNK_MAX_SIZE = _env_int("CHUNK_MAX_SIZE", 1000)

def store_chunks_in_neo4j(chunks: List[str], embeddings: List) -> List[str]:
    """
    Store chunks as Chunk nodes in Neo4j.

    Returns:
        List[str]: List of generated chunk IDs.
    """
    chunk_ids = []
    with driver.session() as session:
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            session.run(
                """
                CREATE (c:Chunk {id: $id, text: $text, embedding: $embedding})
                """,
                id=chunk_id,
                text=chunk,
                embedding=emb.tolist() if hasattr(emb, "tolist") else emb
            )
            chunk_ids.append(chunk_id)
    return chunk_ids


def sanitize_relation_name(rel: str) -> str:
    """
    Sanitize relation names to be Neo4j-safe.
    """
    if not rel:
        rel = "RELATED"
    rel = re.sub(r"[^A-Za-z0-9_]", "_", rel)
    return rel


def extract_triples_from_chunk(chunk_text: str, llm_model) -> List[Tuple[str, str, str]]:
    """
    Generate subject-relation-object triples from text using the provided LLM.
    
    Args:
        chunk_text: The text chunk to extract triples from
        llm_model: The LLM instance to use (LocalLLM or GroqLLM)
    """
    prompt = f"""
You are an information extraction system specialized in Terms of Service.

Your task: From the given text, extract all factual subject–relation–object triples.

Rules:
- Output ONLY in this exact format, one triple per line:
  (SUBJECT, RELATION, OBJECT)
- No explanations, bullet points, numbering, or extra words.
- Keep SUBJECT, RELATION, and OBJECT concise.
- If no valid triples exist, return nothing.

Examples:

Text:
"Marie Curie discovered radium and polonium."
Output:
(Marie Curie, discovered, radium)
(Marie Curie, discovered, polonium)

Text:
"Users cannot share their passwords with anyone."
Output:
(User, cannot_share, passwords)

Text:
"The User must provide accurate information during account registration."
Output:
(User, must_provide, accurate information)
(User, registers_for, Account)

Text:
"The Company may terminate your subscription at any time with notice."
Output:
(Company, may_terminate, subscription)
(Company, gives_notice, User)

Text:
"By using the Service, you agree to the Terms of Service and Privacy Policy."
Output:
(User, agrees_to, Terms of Service)
(User, agrees_to, Privacy Policy)

Text:
"If the User violates the rules, the Company may suspend the account."
Output:
(User, violates, rules)
(Company, may_suspend, account)

Now extract triples from this text:
\"\"\"{chunk_text}\"\"\"
"""
    response = llm_model.invoke(prompt)  # Use provided model
    text_out = response.content if isinstance(response.content, str) else str(response.content) #type:ignore
    triples: List[Tuple[str, str, str]] = []

    for line in text_out.splitlines():
        line = line.strip()
        if TRIPLE_PATTERN.match(line):
            parts = [x.strip() for x in line[1:-1].split(",")]
            if len(parts) == 3:
                s, r, o = parts
                if s and r and o:  # Skip empty parts
                    triples.append((s, r, o))
        elif line:
            print(f"Skipping line: {line}. Does not match pattern.")

    if not triples:
        print("No suitable triples found.")
    return triples


def store_triples(triples: List[Tuple[str, str, str]], chunk_id: str):
    """
    Store triples in Neo4j with chunk_id as a property and link them to Chunk node.
    """
    with driver.session() as session:
        for s, r, o in triples:
            # Skip empty entities
            if not s or not o:
                continue

            safe_rel = sanitize_relation_name(r)
            session.run(
                f"""
                MERGE (sub:Entity {{name: $subj}})
                MERGE (obj:Entity {{name: $obj}})
                MERGE (c:Chunk {{id: $chunk_id}})
                MERGE (sub)-[:`{safe_rel}` {{chunk_id: $chunk_id}}]->(obj)
                MERGE (sub)-[:MENTIONED_IN]->(c)
                MERGE (obj)-[:MENTIONED_IN]->(c)
                """,#type:ignore
                subj=s,
                obj=o,
                chunk_id=chunk_id
            )

def clear_neo4j():
    """
    Deletes all existing Chunk nodes, Entity nodes, and triples in the database.
    """
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

def ingest(filepath: str, use_cloud: bool = False, doc_id: str = None, analysis_state: dict = None):
    """
    Full ingestion pipeline:
    1. Clear Neo4j
    2. Load text
    3. Chunk text
    4. Generate embeddings
    5. Store chunks in Neo4j
    6. Extract triples and store in Neo4j (with batching if cloud)
    7. Run analysis and cache result
    
    Args:
        filepath: Path to document file
        use_cloud: If True, use cloud API with batching. If False, use local LLM.
        doc_id: Document ID for progress tracking (optional)
        analysis_state: Global analysis state dict for progress updates (optional)
    """
    import hashlib
    
    # Get appropriate LLM models based on user choice
    llm_fast, llm = get_llm_models(use_cloud)
    logger.info(f"Using {'cloud' if use_cloud else 'local'} models for processing")
    
    # Generate hash of file content for caching
    with open(filepath, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    cache_file = filepath + f".analysis_{file_hash}.json"
    
    # Check if cached analysis exists
    if ENABLE_ANALYSIS_CACHE and os.path.exists(cache_file):
        logger.info(f"Using cached analysis for {filepath}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    clear_neo4j()
    text = tp.load_text(filepath)
    chunks_list = tp.chunk_text_spacy(text, max_chunk_size=CHUNK_MAX_SIZE)
    chunks = [item["chunk"] for item in chunks_list]
    embeddings = tp.embed_chunks(chunks)

    # Store chunks & get IDs
    chunk_ids = store_chunks_in_neo4j(chunks, embeddings)

    # Parallel triple extraction with optional batching for cloud rate limits
    logger.info(f"Extracting triples from {len(chunks_list)} chunks ({'cloud with batching' if use_cloud else 'local parallel'})...")
    total_chunks = len(chunks_list)
    chunks_processed = 0
    
    def extract_and_store(chunk_item, chunk_id):
        nonlocal chunks_processed
        try:
            chunk_text = chunk_item["chunk"]
            triples = extract_triples_from_chunk(chunk_text, llm_fast)  # Pass LLM model
            chunks_processed += 1
            # Update progress: 30-70% for triple extraction
            if doc_id and analysis_state and doc_id in analysis_state:
                progress = 30 + int((chunks_processed / total_chunks) * 40)
                analysis_state[doc_id]["progress"] = min(progress, 70)
                analysis_state[doc_id]["message"] = f"Extracting triples: {chunks_processed}/{total_chunks} chunks"
            return chunk_id, triples
        except Exception as e:
            logger.error(f"Error extracting triples for chunk {chunk_id}: {e}")
            chunks_processed += 1
            return chunk_id, []
    
    if use_cloud:
        # Cloud mode: Batch processing to respect rate limits.
        BATCH_SIZE = max(1, CLOUD_BATCH_SIZE)
        total_batches = (len(chunks_list) + BATCH_SIZE - 1) // BATCH_SIZE
        for batch_num, i in enumerate(range(0, len(chunks_list), BATCH_SIZE)):
            batch_chunks = chunks_list[i:i + BATCH_SIZE]
            batch_ids = chunk_ids[i:i + BATCH_SIZE]
            
            logger.info(f"Processing batch {batch_num + 1}/{total_batches}")
            if doc_id and analysis_state and doc_id in analysis_state:
                analysis_state[doc_id]["message"] = f"Processing batch {batch_num + 1}/{total_batches}..."
            
            with ThreadPoolExecutor(max_workers=max(1, CLOUD_MAX_WORKERS)) as executor:
                futures = {executor.submit(extract_and_store, chunk, cid): cid 
                           for chunk, cid in zip(batch_chunks, batch_ids)}
                
                for future in as_completed(futures):
                    chunk_id, triples = future.result()
                    if triples:
                        store_triples(triples, chunk_id)
            
            # Pause between batches if there are more batches (rate limit safety)
            if i + BATCH_SIZE < len(chunks_list):
                logger.info(f"Pausing {CLOUD_BATCH_PAUSE_SECONDS}s to respect API rate limits...")
                if doc_id and analysis_state and doc_id in analysis_state:
                    analysis_state[doc_id]["message"] = f"Rate limit pause (batch {batch_num + 1}/{total_batches})..."
                time.sleep(max(0, CLOUD_BATCH_PAUSE_SECONDS))
    else:
        # Local mode: Aggressive parallel processing (no rate limits)
        with ThreadPoolExecutor(max_workers=max(1, LOCAL_MAX_WORKERS)) as executor:
            futures = {executor.submit(extract_and_store, chunk, cid): cid 
                       for chunk, cid in zip(chunks_list, chunk_ids)}
            
            for future in as_completed(futures):
                chunk_id, triples = future.result()
                if triples:
                    store_triples(triples, chunk_id)
    
    logger.info(f"Ingestion Complete for {filepath}")

    # --- Fetch all chunks from Neo4j ---
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Chunk)
            RETURN c.id AS chunk_id, c.text AS text
            """
        )
        chunk_dicts = [record.data() for record in result]
    
    logger.info(f"Retrieved {len(chunk_dicts)} chunks from Neo4j for analysis")
    print(f"\nDEBUG: Retrieved {len(chunk_dicts)} chunks from Neo4j")
    if chunk_dicts:
        print(f"First chunk preview: {chunk_dicts[0]['text'][:100]}")

    # --- Run initial analysis with appropriate LLM ---
    if doc_id and analysis_state and doc_id in analysis_state:
        analysis_state[doc_id]["progress"] = 75
        analysis_state[doc_id]["message"] = "Running LLM analysis..."
    
    analysis_json = generate_initial_analysis(chunk_dicts, llm)
    logger.info(f"Initial Analysis Complete for {filepath}")
    
    # Cache the analysis result
    if ENABLE_ANALYSIS_CACHE:
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(analysis_json)
    
    if doc_id and analysis_state and doc_id in analysis_state:
        analysis_state[doc_id]["progress"] = 90
        analysis_state[doc_id]["message"] = "Finalizing results..."
    
    return analysis_json
