"""
"""

from typing import List, Dict
import json

from langchain_setup import driver, embedding_model, llm
from models import QueryOut

def get_similar_chunks(query_text: str, namespace: str, k: int = 5) -> List[Dict]:
    """
    Performs a vecotr similarity search to find relevant text chunks

    Args:
        query_text (str): The user's query or a predefined prompt text.

        namespace (str): The document ID to search within.

        k (int): The number of top chunks to retrieve

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary contains the `text` of a retrieved chunk and its `score`.

    """

    try:
        query_embedding = embedding_model.encode(query_text,convert_to_numpy=True)
        with driver.session() as sessison:
            result = sessison.run(
                    """
                    CALL db.index.vector.queryNodes('chunk_embeddings', $k, $query_embedding)
                YIELD node AS found_chunk, score
                WHERE found_chunk.doc_id = $namespace
                RETURN found_chunk.text AS text, score
                ORDER BY score DESC
                    """,
                k = k,
                query_embedding = query_embedding,
                namespace = namespace
            )

            return [record.data() for record in result]

    except Exception as e:
        print(f"Error during vector search: {e}")
        return []

def generate_rag_response(query_text: str, retrieved_chunks : List[Dict]) -> str:
    """
    Uses retrieved chunks to ground an LLM response for a conversational query.

    Args:
        query_text (str): The user's query

        retrieved_chunks (List[Dict]): Chunks returned from the vector search.

    Returns:
        str: The generated responsse form the LLM.

    """
    context = "\n".join([chunk["text"] for chunk in retrieved_chunks])

    prompt = f"""
             You are a helpful assistant that answers questions about
             a Terms of Service document. Use only the provided context
             to answer the user's query. If the answer is not in the
             context, state that you cannot answer the question.

            **Context:**
            {context}

            **User Query:**
            {query_text}

            **Answer:**
            """

    try:
        response = llm.invoke(prompt)
        return response.context
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        return "An error occurred while generating a response"


def generate_initial_analysis(retrieved_chunks: List[Dict]) -> str:
    """
    Generates a structured, JSON-formatted analysis of risky clauses.

    This function is for the initial, default query upon ingestion.
    It returns a JSON string that the front-end can parse.

    Args:
        retrieved_chunks (List[Dict]): All chunks from the document.

    Returns:
        str: A JSON string containing the structured analysis.
    """
    document_text = "\n".join([chunk["text"] for chunk in retrieved_chunks])

    prompt = f"""
You are a legal analyst specializing in consumer protection law. Your task is to review a Terms of Service document and identify clauses that are potentially unfair, disadvantageous, or risky for the user.

For each clause, you must:
1.  **Analyze the clause's text**.
2.  **Identify the potential risk**. Consider risks related to:
    * `Data & Privacy`: Broad data collection, lack of user control, data sharing.
    * `Liability & Disclaimers`: Unilateral limitation of liability, 'as-is' clauses.
    * `Dispute Resolution`: Mandatory arbitration, class action waivers, biased choice of law.
    * `Unilateral Changes`: Company can change terms without notice.
    * `Content & IP`: Company claims broad rights to user-generated content.
    * `Termination`: Company can terminate accounts for any reason.
3.  **Assign a label**: Use one of the following labels: `Risky: Data & Privacy`, `Risky: Liability`, `Risky: Dispute Resolution`, `Risky: Unilateral Changes`, `Risky: Content & IP`, `Risky: Termination`, `Neutral`, or `Fair`.
4.  **Provide a concise reasoning**: Summarize why you gave that label in a single sentence.

Here is the document text:
"{document_text}"

Return your response as a JSON array of objects. Each object must have the following keys:
`"clause_text"` (the original text), `"label"` (the assigned label), `"reasoning"` (the explanation), and `"risk_category"` (the specific risk).

Example of desired output format:
[
  {{
    "clause_text": "Company reserves the right to modify or terminate this Agreement at any time, for any reason, without notice.",
    "label": "Risky",
    "reasoning": "This clause allows the company to terminate a user's account without any clear justification or notice, which is highly disadvantageous.",
    "risk_category": "Termination"
  }}
]
"""
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error invoking LLM for initial analysis: {e}")
        return json.dumps({"error": "Failed to generate analysis"})

