import os
import spacy
from sentence_transformers import SentenceTransformer
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase   # ← Disabled for now
from ollama import Client as OllamaClient  # ← NEW
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env from parent folder
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

nlp = spacy.load("en_core_web_sm")
embedding_model = SentenceTransformer("nlpaueb/legal-bert-small-uncased")

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

# # ───── Gemini test ─────
# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     temperature=0.2,
#     api_key=GOOGLE_API_KEY
# )

class LocalLLM:
    def __init__(self, model_name="llama2"):
        self.client = OllamaClient()
        self.model_name = model_name

    def invoke(self, prompt: str):
        response = self.client.generate(model=self.model_name, prompt=prompt)
        class Resp: pass
        r = Resp()
        r.content = response['response'] #type:ignore
        return r

llm = LocalLLM(model_name="llama2")


if __name__ == "__main__":
    print("Testing Neo4j connection...")
    test_neo4j_connection()

    print("Testing Local LLM...")
    response = llm.invoke("Explain what Neo4j is in one short sentence.")
    print("Local LLM says:", response.content) #type:ignore
