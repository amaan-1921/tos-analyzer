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
print(f"DEBUG: Loading .env from: {env_path}")
print(f"DEBUG: .env exists: {env_path.exists()}")
load_dotenv(dotenv_path=env_path)

nlp = spacy.load("en_core_web_sm")
embedding_model = SentenceTransformer("nlpaueb/legal-bert-small-uncased")  # Already cached locally

# Read API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print(f"DEBUG: GROQ_API_KEY loaded: {GROQ_API_KEY[:10] if GROQ_API_KEY else 'NOT SET'}...")
print(f"DEBUG: GOOGLE_API_KEY loaded: {GOOGLE_API_KEY[:10] if GOOGLE_API_KEY else 'NOT SET'}...")

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
    def __init__(self, model_name="mistral:7b", temperature=0.3):
        self.client = OllamaClient()
        self.model_name = model_name
        self.temperature = temperature

    def invoke(self, prompt: str):
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            options={"temperature": self.temperature}
        )
        class Resp: pass
        r = Resp()
        r.content = response['response'] #type:ignore
        return r


class GroqLLM:
    """Fast cloud-based LLM using Groq API (free tier)."""
    def __init__(self, model_name="llama-3.1-8b-instant", temperature=0.3):
        try:
            from groq import Groq
            self.client = Groq(api_key=GROQ_API_KEY)
            self.model_name = model_name
            self.temperature = temperature
            self.available = True
        except ImportError:
            print("⚠️  Groq not installed. Install with: pip install groq")
            self.available = False
        except Exception as e:
            print(f"⚠️  Groq initialization failed: {e}")
            self.available = False

    def invoke(self, prompt: str):
        if not self.available:
            raise RuntimeError("Groq is not available. Falling back to local LLM.")
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=2000
        )
        class Resp: pass
        r = Resp()
        r.content = response.choices[0].message.content
        return r


# Factory function to get LLM models based on user choice
def get_llm_models(use_cloud: bool = False):
    """
    Returns (llm_fast, llm) tuple based on processing mode.
    
    Args:
        use_cloud: True for cloud API (fast, privacy concerns), False for local (private, slower)
    
    Returns:
        (llm_fast, llm): Tuple of models for triple extraction and analysis
    """
    if use_cloud and GROQ_API_KEY:
        print("[CLOUD] Using Groq API (cloud, ultra-fast)")
        # Fast LLM for triple extraction
        llm_fast = GroqLLM(model_name="llama-3.1-8b-instant", temperature=0.2)
        # Smart LLM for analysis
        llm = GroqLLM(model_name="llama-3.1-8b-instant", temperature=0.3)
    else:
        print("[LOCAL] Using local Ollama models")
        # Fast LLM for triple extraction (speed critical, accuracy less important)
        llm_fast = LocalLLM(model_name="qwen2.5:1.5b", temperature=0.2)
        # Smart LLM for final analysis (accuracy critical)
        llm = LocalLLM(model_name="mistral:7b", temperature=0.3)
    
    return llm_fast, llm


# Default local models for backward compatibility
print("[LOCAL] Initializing default local Ollama models")
llm_fast = LocalLLM(model_name="qwen2.5:1.5b", temperature=0.2)
llm = LocalLLM(model_name="mistral:7b", temperature=0.3)


if __name__ == "__main__":
    print("Testing Neo4j connection...")
    test_neo4j_connection()

    print("Testing Local LLM...")
    response = llm.invoke("Explain what Neo4j is in one short sentence.")
    print("Local LLM says:", response.content) #type:ignore
