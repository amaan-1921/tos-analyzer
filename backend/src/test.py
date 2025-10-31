from retrieve import get_similar_chunks, generate_rag_response

def test_rag_pipeline():
    # Simulate a user query about the document
    query = "Can the company terminate my account without notice?"

    print("=== Vector Similarity Search ===")
    similar_chunks = get_similar_chunks(query, k=3)

    if not similar_chunks:
        print("No chunks found.")
        return

    for i, chunk in enumerate(similar_chunks, start=1):
        print(f"\nChunk {i}:")
        print(f"  ID: {chunk['chunk_id']}")
        print(f"  Score: {chunk['score']}")
        print(f"  Text: {chunk['text'][:150]}...")

    print("\n=== RAG Response ===")
    answer = generate_rag_response(query, similar_chunks)
    print(answer)

if __name__ == "__main__":
    test_rag_pipeline()
