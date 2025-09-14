import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase   # ← Disabled for now

# LangChain imports
# from langchain_community.embeddings import HuggingFaceEmbeddings  # optional for later
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env from parent folder
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Read API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

NEO4J_URI = os.getenv("NEO4J_URL", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your_password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def test_neo4j_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Neo4j connection OK' AS msg")
        record = result.single()
        if record is not None:
            print(record["msg"])
        else:
            print("No result returned")

# ───── Gemini test ─────
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2,
    api_key=GOOGLE_API_KEY
)

if __name__ == "__main__":
    print("Testing Neo4j connection...")
    test_neo4j_connection()

    print("Testing Gemini API...")
    response = llm.invoke("Explain what Neo4j is in one short sentence.")
    print("Gemini says:", response.content)
