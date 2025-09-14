"""
Ingestion Utility for uploaded documents
"""
from langchain_setup import driver
import json
import uuid
import re
from typing import List, Tuple

import spacy
from langchain_setup import driver, llm
import text_processor as tp

nlp = spacy.load("en_core_web_sm")
TRIPLE_PATTERN = re.compile(r"^\(.+?,.+?,.+?\)$")


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


def extract_triples_from_chunk(chunk_text: str) -> List[Tuple[str, str, str]]:
    """
    Generate subject-relation-object triples from text using the LLM.
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
    response = llm.invoke(prompt)
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

def ingest(filepath: str):
    """
    Full ingestion pipeline:
    1. Clear Neo4j
    2. Load text
    3. Chunk text
    4. Generate embeddings
    5. Store chunks in Neo4j
    6. Extract triples and store in Neo4j
    """
    clear_neo4j()
    text = tp.load_text(filepath)
    chunks_list = tp.chunk_text_spacy(text)
    chunks = [item["chunk"] for item in chunks_list]
    embeddings = tp.embed_chunks(chunks)

    # Store chunks & get IDs
    chunk_ids = store_chunks_in_neo4j(chunks, embeddings)

    for chunk, chunk_id in zip(chunks_list, chunk_ids):
        chunk_text = chunk["chunk"]
        triples = extract_triples_from_chunk(chunk_text)
        store_triples(triples, chunk_id)
