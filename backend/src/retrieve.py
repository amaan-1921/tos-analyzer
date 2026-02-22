"""
Retrieval and RAG utilities for Terms of Service documents.
Combines vector DB retrieval and KG triples for context-aware LLM responses.
"""
import json
from typing import List, Dict
import re
from langchain_setup import driver, embedding_model, llm


def get_similar_chunks(query_text: str, k: int = 5) -> List[Dict]:
    """
    Perform vector similarity search to find relevant chunks.

    Args:
        query_text (str): User query.
        k (int): Number of top chunks to retrieve.

    Returns:
        List[Dict]: Retrieved chunks with text, score, and chunk_id.
    """
    try:
        # Encode query to vector
        query_embedding = embedding_model.encode(query_text, convert_to_numpy=True)

        with driver.session() as session:
            result = session.run(
                """
                CALL db.index.vector.queryNodes('chunk_embeddings', $k, $query_embedding)
                YIELD node AS found_chunk, score
                RETURN found_chunk.text AS text, found_chunk.id AS chunk_id, score
                """,
                k=k,
                query_embedding=query_embedding.tolist(),  # safer to convert to list for Neo4j
            )
            return [record.data() for record in result]

    except Exception as e:
        print(f"Error during vector search: {e}")
        return []



def generate_rag_response(query_text: str, retrieved_chunks: List[Dict], llm_model=None) -> str:
    """
    Generate LLM response grounded on retrieved chunks and KG triples.

    Args:
        query_text (str): User query.
        retrieved_chunks (List[Dict]): Chunks returned from vector search.
        llm_model: LLM instance to use. If None, uses global llm from langchain_setup.

    Returns:
        str: LLM response.
    """
    # Use provided LLM or fallback to global
    if llm_model is None:
        llm_model = llm
    
    enriched_context = []

    with driver.session() as session:
        for chunk in retrieved_chunks:
            chunk_text = chunk["text"] or ""
            chunk_id = chunk["chunk_id"]

            # Fetch triples linked to this chunk
            result = session.run(
                """
                MATCH (sub)-[rel]->(obj)-[:MENTIONED_IN]->(c:Chunk {id: $chunk_id})
                RETURN sub.name AS subject, type(rel) AS relation, obj.name AS object
                """,
                chunk_id=chunk_id
            )
            triples = [f"({r['subject']}, {r['relation']}, {r['object']})" for r in result]

            context_block = f"Chunk Text:\n{chunk_text}\nTriples:\n" + ("\n".join(triples) if triples else "None")
            enriched_context.append(context_block)

    context_str = "\n\n".join(enriched_context)

    prompt = f"""
You are a helpful assistant specialized in Terms of Service documents.

Use ONLY the provided context and triples to answer the user's query.
If the answer is not in the context, say you cannot answer.

**Context with Triples:**
{context_str}

**User Query:**
{query_text}

**Answer:**
"""
    try:
        response = llm_model.invoke(prompt)
        return getattr(response, "content", str(response))
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        return "An error occurred while generating a response"


def get_optimized_analysis_prompt(document_text: str) -> str:
    """
    Generate an optimized prompt for Mistral 7B and other capable models.
    Uses explicit reasoning requests and structured output format.
    """
    return f"""You are an expert legal document analyst specializing in Terms of Service agreements.

Your task: Identify the 3-5 MOST RISKY clauses that could harm users or limit their rights.

Instructions:
1. Focus on clauses that create LIABILITY, PRIVACY issues, TERMINATION rights, PAYMENT obligations, or UNFAIR CHANGES
2. Ignore routine legal language - find the CONCERNING clauses
3. For EACH risky clause, provide EXACTLY this format with your reasoning:

CLAUSE: [exact text from the ToS - keep it complete]
RISK: [number 1-10 where: 1-3=minimal risk, 4-6=moderate risk, 7-10=high risk]
CATEGORY: [choose: Privacy, Liability, Termination, Payments, or Changes]
REASON: [2-3 sentences explaining specifically why this is risky for users]

IMPORTANT:
- Leave ONE blank line between each clause
- Risk scores BELOW 7 are NOT truly risky (use 7-10 for actual risks)
- Be specific about WHO is harmed and HOW

Terms of Service:
{document_text}

Now identify the MOST RISKY clauses. Start with the highest risk items."""
    

def parse_prefix_format(text: str) -> List[Dict]:
    """
    Parse prefix format: CLAUSE: ... RISK: ... CATEGORY: ... REASON: ...
    """
    clauses = []
    current_clause = {}
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('CLAUSE:'):
            if current_clause and 'clause_text' in current_clause:
                clauses.append(current_clause)
            current_clause = {'clause_text': line.replace('CLAUSE:', '').strip()}
        elif line.startswith('RISK:'):
            try:
                risk_val = int(re.search(r'\d+', line.replace('RISK:', '').strip()).group())
                current_clause['risk_score'] = min(10, max(1, risk_val))
            except:
                current_clause['risk_score'] = 5
        elif line.startswith('CATEGORY:'):
            current_clause['risk_category'] = line.replace('CATEGORY:', '').strip()
        elif line.startswith('REASON:'):
            current_clause['reasoning'] = line.replace('REASON:', '').strip()
    
    if current_clause and 'clause_text' in current_clause:
        clauses.append(current_clause)
    
    return clauses


def parse_numbered_format(text: str) -> List[Dict]:
    """
    Parse numbered format like:
    1. Clause text here
    Risk: 8
    Category: Privacy
    Reason: text
    """
    clauses = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Match numbered clause start
        match = re.match(r'^(\d+)[.\)]\s+(.+)', line)
        if match:
            current = {'clause_text': match.group(2)}
            
            # Look ahead for metadata on next lines
            j = i + 1
            while j < len(lines) and j < i + 10:
                next_line = lines[j].strip()
                
                if re.match(r'^(\d+)[.\)]', next_line):
                    break  # Next numbered item
                
                if next_line.lower().startswith('risk'):
                    try:
                        risk_val = int(re.search(r'\d+', next_line).group())
                        current['risk_score'] = min(10, max(1, risk_val))
                    except:
                        pass
                elif next_line.lower().startswith('category'):
                    current['risk_category'] = re.sub(r'^category\s*:?\s*', '', next_line, flags=re.I).strip()
                elif next_line.lower().startswith('reason'):
                    current['reasoning'] = re.sub(r'^reason\s*:?\s*', '', next_line, flags=re.I).strip()
                elif next_line and not any(next_line.lower().startswith(x) for x in ['risk', 'category', 'reason']):
                    # If it's not a known field and has content, treat as reasoning
                    if 'reasoning' not in current:
                        current['reasoning'] = next_line
                
                j += 1
            
            if current.get('clause_text'):
                clauses.append(current)
            i = j
        else:
            i += 1
    
    return clauses


def parse_markdown_format(text: str) -> List[Dict]:
    """
    Parse markdown/bold format like:
    **Clause 1:** Text here
    **Risk:** 8
    **Category:** Privacy
    **Reason:** text
    """
    clauses = []
    current_clause = {}
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Remove markdown bold markers
        clean_line = line.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
        
        if clean_line.lower().startswith('clause'):
            if current_clause and current_clause.get('clause_text'):
                clauses.append(current_clause)
            current_clause = {'clause_text': re.sub(r'^clause\s*:?\s*', '', clean_line, flags=re.I).strip()}
        elif clean_line.lower().startswith('risk'):
            try:
                risk_val = int(re.search(r'\d+', clean_line).group())
                current_clause['risk_score'] = min(10, max(1, risk_val))
            except:
                current_clause['risk_score'] = 5
        elif clean_line.lower().startswith('category'):
            current_clause['risk_category'] = re.sub(r'^category\s*:?\s*', '', clean_line, flags=re.I).strip()
        elif clean_line.lower().startswith('reason'):
            current_clause['reasoning'] = re.sub(r'^reason\s*:?\s*', '', clean_line, flags=re.I).strip()
    
    if current_clause and current_clause.get('clause_text'):
        clauses.append(current_clause)
    
    return clauses


def extract_sentence_clauses(text: str) -> List[Dict]:
    """
    Fallback: Extract meaningful sentences as clauses if structured parsing fails.
    Heuristic: sentences containing risk-related keywords + sentence boundaries.
    """
    risk_keywords = ['may', 'liable', 'responsible', 'indemnif', 'waive', 'disclaim', 
                     'terminate', 'suspend', 'collect', 'process', 'share', 'delete',
                     'limit', 'modif', 'agree', 'oblig', 'subject']
    
    clauses = []
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 20 or len(sent) > 500:
            continue
        
        # Score based on keywords and length
        lower_sent = sent.lower()
        keyword_count = sum(1 for kw in risk_keywords if kw in lower_sent)
        
        if keyword_count > 0:
            risk_score = min(10, 3 + (keyword_count * 2))
            
            # Determine category
            if any(x in lower_sent for x in ['collect', 'process', 'share', 'data', 'information', 'personal']):
                category = 'Privacy'
            elif any(x in lower_sent for x in ['liable', 'indemnif', 'responsible', 'damage']):
                category = 'Liability'
            elif any(x in lower_sent for x in ['terminate', 'suspend', 'cancel']):
                category = 'Termination'
            elif any(x in lower_sent for x in ['payment', 'fee', 'price', 'charge', 'refund']):
                category = 'Payments'
            elif any(x in lower_sent for x in ['modif', 'change', 'update', 'amend']):
                category = 'Changes'
            else:
                category = 'General'
            
            clauses.append({
                'clause_text': sent,
                'risk_score': risk_score,
                'risk_category': category,
                'reasoning': f"Contains risk-related terms ({keyword_count} keywords found)"
            })
    
    # Sort by risk score and take top 5
    return sorted(clauses, key=lambda x: x['risk_score'], reverse=True)[:5]


def clean_and_validate_clauses(clauses: List[Dict]) -> List[Dict]:
    """
    Ensure all clauses have required fields and generate labels.
    """
    cleaned = []
    
    for idx, item in enumerate(clauses):
        try:
            if not item.get('clause_text') or len(item['clause_text']) < 10:
                continue
            
            # Set defaults
            if 'risk_score' not in item:
                item['risk_score'] = 5
            if 'reasoning' not in item:
                item['reasoning'] = 'Clause identified from ToS'
            if 'risk_category' not in item:
                item['risk_category'] = 'General'
            
            risk = int(item['risk_score']) if isinstance(item['risk_score'], (int, str)) else 5
            risk = min(10, max(1, risk))
            item['risk_score'] = risk
            
            # Generate label
            if risk >= 7:
                item['label'] = f"Risky: {item['risk_category']}"
            elif risk >= 4:
                item['label'] = 'Fair'
            else:
                item['label'] = 'Neutral'
            
            cleaned.append(item)
        except Exception as e:
            print(f"Error validating clause {idx}: {e}")
            continue
    
    return cleaned


def generate_initial_analysis(retrieved_chunks: List[Dict], llm_model=None) -> str:
    """
    Generate JSON-formatted analysis of risky clauses using KG and chunk context.
    Includes risk scoring (1-10).
    
    Uses multiple parsing strategies to handle various LLM output formats.

    Args:
        retrieved_chunks (List[Dict]): Chunks to analyze.
        llm_model: LLM instance to use. If None, uses global llm from langchain_setup.

    Returns:
        str: JSON string with structured analysis.
    """
    # Use provided LLM or fallback to global
    if llm_model is None:
        from langchain_setup import llm as default_llm
        llm_model = default_llm
    
    print(f"\n=== ANALYSIS STARTED ===")
    print(f"Received {len(retrieved_chunks)} chunks to analyze")
    
    enriched_text = []

    with driver.session() as session:
        for i, chunk in enumerate(retrieved_chunks):
            chunk_text = chunk["text"]
            chunk_id = chunk["chunk_id"]
            
            print(f"Processing chunk {i+1}/{len(retrieved_chunks)}: {chunk_text[:50]}...")

            result = session.run(
                """
                MATCH (sub)-[rel]->(obj)-[:MENTIONED_IN]->(c:Chunk {id: $chunk_id})
                RETURN sub.name AS subject, type(rel) AS relation, obj.name AS object
                """,
                chunk_id=chunk_id
            )
            triples = [f"({r['subject']}, {r['relation']}, {r['object']})" for r in result]
            enriched_text.append(
                chunk_text + "\nTriples:\n" + ("\n".join(triples) if triples else "None")
            )

    document_text = "\n\n".join(enriched_text)
    print(f"Combined document length: {len(document_text)} characters")
    
    # For cloud APIs, limit context size to avoid token limits
    # Groq free tier: ~6000 tokens/min, assume ~4 chars/token
    # Reserve 1000 tokens for response, use max ~20,000 chars for prompt
    MAX_CLOUD_CHARS = 20000
    is_cloud_llm = llm_model.__class__.__name__ == 'GroqLLM'
    
    if is_cloud_llm and len(document_text) > MAX_CLOUD_CHARS:
        print(f"[CLOUD] Document too large ({len(document_text)} chars), truncating to {MAX_CLOUD_CHARS} chars")
        document_text = document_text[:MAX_CLOUD_CHARS] + "\n\n[... Document truncated due to cloud API limits ...]"
    
    print(f"======================\n")

    # Use optimized prompt for smaller LLM models
    prompt = get_optimized_analysis_prompt(document_text)
    
    try:
        response = llm_model.invoke(prompt)
        raw = getattr(response, "content", str(response)).strip()
        
        print(f"\n=== DEBUG: LLM Response ===")
        print(f"Full Response:\n{raw}")
        print(f"=========================\n")

        if not raw:
            raise ValueError("LLM returned empty response")

        # Try multiple parsing strategies
        parsed_clauses = []
        
        # Strategy 1: Prefix format (CLAUSE: ... RISK: ...)
        parsed_clauses = parse_prefix_format(raw)
        print(f"Strategy 1 (Prefix format): {len(parsed_clauses)} clauses")
        
        # Strategy 2: Numbered format if prefix parsing failed
        if len(parsed_clauses) == 0:
            parsed_clauses = parse_numbered_format(raw)
            print(f"Strategy 2 (Numbered format): {len(parsed_clauses)} clauses")
        
        # Strategy 3: Markdown/bold format
        if len(parsed_clauses) == 0:
            parsed_clauses = parse_markdown_format(raw)
            print(f"Strategy 3 (Markdown format): {len(parsed_clauses)} clauses")
        
        # Strategy 4: Fallback to sentence extraction
        if len(parsed_clauses) == 0:
            print("All structured parsing failed, using fallback heuristic extraction...")
            parsed_clauses = extract_sentence_clauses(raw)
            print(f"Strategy 4 (Heuristic extraction): {len(parsed_clauses)} clauses")
        
        # Clean and validate
        cleaned = clean_and_validate_clauses(parsed_clauses)
        
        if len(cleaned) == 0:
            print("WARNING: No valid clauses extracted even after fallback")
            # Last resort: return raw text as a clause
            return json.dumps([{
                "clause_text": raw[:500] if len(raw) > 500 else raw,
                "label": "Analysis",
                "reasoning": "Unable to parse structured format, returning raw analysis",
                "risk_category": "Unknown",
                "risk_score": 5
            }])

        # Sort by risk_score descending (risky first)
        cleaned = sorted(cleaned, key=lambda x: int(x.get("risk_score", 0)) if isinstance(x.get("risk_score"), (int, str)) else 0, reverse=True)
        
        print(f"Returning {len(cleaned)} sorted clauses")
        return json.dumps(cleaned, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error invoking LLM for initial analysis: {e}")
        import traceback
        traceback.print_exc()
        return json.dumps([{"clause_text": "Error during analysis", "label": "Error", "reasoning": str(e), "risk_category": "", "risk_score": 0}])
