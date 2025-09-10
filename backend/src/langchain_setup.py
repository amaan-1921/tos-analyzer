import os
from neo4j import GraphDatabase

from config import ensure_google_api_key
ensure_google_api_key()

# LangChain imports
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI




def test_neo4j_connection():
    """Simple connection test"""
    with driver.session() as session:
        result = session.run("RETURN 'Neo4j connection OK' AS msg")
        print(result.single()["msg"])


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Use Gemini as LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",   # or "gemini-1.5-pro" for more accuracy
    temperature=0.2
)

NEO4J_URI = os.getenv("NEO4J_URL", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "test123")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

if __name__ == "__main__":
    print("Testing Neo4j connection...")
    test_neo4j_connection()
    
    # Quick LLM test
    response = llm.invoke("Explain what Neo4j is in one sentence.")
    print(response.content)
