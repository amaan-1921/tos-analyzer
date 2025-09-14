"""
Retrieval and RAG utilities for Terms of Service documents.
Combines vector DB retrieval and KG triples for context-aware LLM responses.
"""
import json
from typing import List, Dict

from langchain_setup import driver, embedding_model, llm


def get_similar_chunks(query_text: str, namespace: str, k: int = 5) -> List[Dict]:
    """
    Perform vector similarity search to find relevant chunks.

    Args:
        query_text (str): User query.
        namespace (str): Document ID or namespace.
        k (int): Number of top chunks to retrieve.

    Returns:
        List[Dict]: Retrieved chunks with text, score, and chunk_id.
    """
    try:
        query_embedding = embedding_model.encode(query_text, convert_to_numpy=True)
        with driver.session() as session:
            result = session.run(
                """
                CALL db.index.vector.queryNodes('chunk_embeddings', $k, $query_embedding)
                YIELD node AS found_chunk, score
                WHERE found_chunk.doc_id = $namespace
                RETURN found_chunk.text AS text, found_chunk.id AS chunk_id, score
                ORDER BY score DESC
                """,
                k=k,
                query_embedding=query_embedding,
                namespace=namespace
            )
            return [record.data() for record in result]
    except Exception as e:
        print(f"Error during vector search: {e}")
        return []


# def generate_rag_response(query_text: str, retrieved_chunks: List[Dict]) -> str:
#     """
#     Generate LLM response grounded on retrieved chunks and KG triples.

#     Args:
#         query_text (str): User query.
#         retrieved_chunks (List[Dict]): Chunks returned from vector search.

#     Returns:
#         str: LLM response.
#     """
#     enriched_context = []

#     with driver.session() as session:
#         for chunk in retrieved_chunks:
#             chunk_text = chunk["text"]
#             chunk_id = chunk["chunk_id"]

#             # Fetch triples linked to this chunk
#             result = session.run(
#                 """
#                 MATCH (sub)-[rel]->(obj)-[:MENTIONED_IN]->(c:Chunk {id: $chunk_id})
#                 RETURN sub.name AS subject, type(rel) AS relation, obj.name AS object
#                 """,
#                 chunk_id=chunk_id
#             )
#             triples = [f"({r['subject']}, {r['relation']}, {r['object']})" for r in result]

#             context_block = f"Chunk Text:\n{chunk_text}\nTriples:\n" + ("\n".join(triples) if triples else "None")
#             enriched_context.append(context_block)

#     context_str = "\n\n".join(enriched_context)

#     prompt = f"""
# You are a helpful assistant specialized in Terms of Service documents.

# Use ONLY the provided context and triples to answer the user's query.
# If the answer is not in the context, say you cannot answer.

# **Context with Triples:**
# {context_str}

# **User Query:**
# {query_text}

# **Answer:**
# """
#     try:
#         response = llm.invoke(prompt)
#         return getattr(response, "content", str(response))
#     except Exception as e:
#         print(f"Error invoking LLM: {e}")
#         return "An error occurred while generating a response"


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
            enriched_text.append(chunk_text + "\nTriples:\n" + ("\n".join(triples) if triples else "None"))

    document_text = "\n\n".join(enriched_text)

    prompt = f"""
You are a legal analyst specializing in consumer protection law. Your task is to review a Terms of Service document and identify clauses that are potentially unfair, disadvantageous, or risky for the user.

For each clause, you must:
1. Analyze the clause's text.
2. Identify the potential risk (Data & Privacy, Liability, Dispute Resolution, Unilateral Changes, Content & IP, Termination).
3. Assign a label: Risky: <category>, Neutral, or Fair.
4. Provide concise reasoning.

Document Text:
"{document_text}"

Return response as JSON array of objects:
[
  {{
    "clause_text": "...",
    "label": "...",
    "reasoning": "...",
    "risk_category": "..."
  }}
]
"""
    try:
        response = llm.invoke(prompt)
        return getattr(response, "content", str(response))
    except Exception as e:
        print(f"Error invoking LLM for initial analysis: {e}")
        return json.dumps({"error": "Failed to generate analysis"})


# ----------------- TEST CASE -----------------
if __name__ == "__main__":
    # Simulate retrieved chunks
    test_chunks = [
        {"text": "The company may terminate accounts without notice.", "chunk_id": "chunk_test_1"},
        {"text": "User data may be shared with third parties.", "chunk_id": "chunk_test_2"}
    ]
    print("\n=== Initial Analysis Test ===")
    analysis = generate_initial_analysis(test_chunks)
    print(analysis)
