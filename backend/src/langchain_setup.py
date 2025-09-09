import os
from neo4j import GraphDatabase

# LangChain imports
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline

def test_neo4j_connection():
    """Simple connection test"""
    with driver.session() as session:
        result = session.run("RETURN 'Neo4j connection OK' AS msg")
        print(result.single()["msg"])


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


hf_pipeline = pipeline(
    "text-generation",
    model="gpt2",
    device=-1,  # -1 = CPU, 0 = first GPU
    max_new_tokens=100
)

llm = HuggingFacePipeline(pipeline=hf_pipeline)

NEO4J_URI = os.getenv("NEO4J_URL", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "test123")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

if __name__ == "__main__":
    print("Testing Neo4j connection...")
    test_neo4j_connection()
