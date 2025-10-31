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



def generate_rag_response(query_text: str, retrieved_chunks: List[Dict]) -> str:
    """
    Generate LLM response grounded on retrieved chunks and KG triples.

    Args:
        query_text (str): User query.
        retrieved_chunks (List[Dict]): Chunks returned from vector search.

    Returns:
        str: LLM response.
    """
    enriched_context = []

    with driver.session() as session:
        for chunk in retrieved_chunks:
            chunk_text = chunk["text"]
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
        response = llm.invoke(prompt)
        return getattr(response, "content", str(response))
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        return "An error occurred while generating a response"


def generate_initial_analysis(retrieved_chunks: List[Dict]) -> str:
    """
    Generate JSON-formatted analysis of risky clauses using KG and chunk context.

    Args:
        retrieved_chunks (List[Dict]): Chunks to analyze.

    Returns:
        str: JSON string with structured analysis.
    """
    enriched_text = []

    with driver.session() as session:
        for chunk in retrieved_chunks:
            chunk_text = chunk["text"]
            chunk_id = chunk["chunk_id"]

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

    prompt = f"""
You are a legal analyst specializing in consumer protection law.
Your task is to review a Terms of Service (ToS) document and identify clauses that are potentially unfair, disadvantageous, or risky for the user.

Your Step-by-Step Task

For each clause in the provided text:

Understand the clause: Break down what the clause is saying in plain language.

Assess its impact on the user.

Classify its fairness level:

"Risky: <category>" if it could harm or disadvantage the user.

"Neutral" if it is standard/legal boilerplate but not harmful.

"Fair" if it protects user rights or limits company power.

Identify the risk category if labeled "Risky". Choose exactly one:

Data & Privacy

Liability

Dispute Resolution

Unilateral Changes

Content & IP

Termination

Provide a concise explanation of why you labeled it that way.

Output Format

Return a valid JSON array where each item has:

[
{
"clause_text": "...",
"label": "Risky: <category> | Neutral | Fair",
"reasoning": "...",
"risk_category": "<one of the categories or empty if Neutral/Fair>"
}
]

Few-Shot Examples

Example 1
Clause:
"The Company may terminate your account at any time without notice."

Output:
{
"clause_text": "The Company may terminate your account at any time without notice.",
"label": "Risky: Termination",
"reasoning": "This gives the company absolute power to end the user's account at any time without warning, leaving the user without recourse or explanation.",
"risk_category": "Termination"
}

Example 2
Clause:
"All personal data collected will be shared with third-party advertisers and affiliates."

Output:
{
"clause_text": "All personal data collected will be shared with third-party advertisers and affiliates.",
"label": "Risky: Data & Privacy",
"reasoning": "This clause allows broad data sharing without user consent, risking misuse and privacy violations.",
"risk_category": "Data & Privacy"
}

Example 3
Clause:
"Users must be at least 18 years old to register."

Output:
{
"clause_text": "Users must be at least 18 years old to register.",
"label": "Neutral",
"reasoning": "This is a standard eligibility requirement and does not disadvantage the user.",
"risk_category": ""
}

Document to Analyze

Now analyze the following Terms of Service text:    

/"/"/"<insert document text here>/"/"/"
"""
    try:
        response = llm.invoke(prompt)
        raw = getattr(response, "content", str(response)).strip()

        if not raw:
            raise ValueError("LLM returned empty response")

        # Try to find all {...} blocks anywhere in the response
        objects = re.findall(r"\{.*?\}", raw, flags=re.DOTALL)

        if not objects:
            # No valid JSON objects found
            return json.dumps({"error": "No clauses found"})

        # Join all objects into one JSON array
        json_array = "[" + ",".join(objects) + "]"

        parsed = json.loads(json_array)

        if isinstance(parsed, dict):
            parsed = [parsed]

        return json.dumps(parsed, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error invoking LLM for initial analysis: {e}")
        return json.dumps({"error": "Failed to generate analysis"})
