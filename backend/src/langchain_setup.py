import os
import random
import threading
import time
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
print(f"DEBUG: GROQ_API_KEY loaded: {'YES' if GROQ_API_KEY else 'NO'}")
print(f"DEBUG: GOOGLE_API_KEY loaded: {GOOGLE_API_KEY[:10] if GOOGLE_API_KEY else 'NOT SET'}...")


def _parse_key_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [k.strip() for k in raw.split(",") if k and k.strip()]


class ApiKeyPool:
    def __init__(self, keys: list[str], name: str):
        self.keys = keys
        self.name = name
        self._index = 0
        self._lock = threading.Lock()

    def has_keys(self) -> bool:
        return len(self.keys) > 0

    def next_key(self) -> str | None:
        if not self.keys:
            return None
        with self._lock:
            key = self.keys[self._index % len(self.keys)]
            self._index += 1
            return key


GROQ_API_KEYS = _parse_key_list(os.getenv("GROQ_API_KEYS"))
if GROQ_API_KEY and GROQ_API_KEY not in GROQ_API_KEYS:
    GROQ_API_KEYS.insert(0, GROQ_API_KEY)

GROQ_CHAT_API_KEYS = _parse_key_list(os.getenv("GROQ_CHAT_API_KEYS"))
if not GROQ_CHAT_API_KEYS:
    chat_single = os.getenv("GROQ_CHAT_API_KEY")
    if chat_single:
        GROQ_CHAT_API_KEYS = [chat_single.strip()]

if not GROQ_CHAT_API_KEYS:
    GROQ_CHAT_API_KEYS = GROQ_API_KEYS.copy()

GROQ_MAX_RETRIES = int(os.getenv("GROQ_MAX_RETRIES", "5"))
GROQ_RETRY_BASE_SECONDS = float(os.getenv("GROQ_RETRY_BASE_SECONDS", "2.0"))
GROQ_RETRY_MAX_SECONDS = float(os.getenv("GROQ_RETRY_MAX_SECONDS", "30.0"))
GROQ_RETRY_JITTER_SECONDS = float(os.getenv("GROQ_RETRY_JITTER_SECONDS", "0.8"))

ANALYSIS_KEY_POOL = ApiKeyPool(GROQ_API_KEYS, "analysis")
CHAT_KEY_POOL = ApiKeyPool(GROQ_CHAT_API_KEYS, "chat")
print(f"DEBUG: GROQ analysis key count: {len(GROQ_API_KEYS)}")
print(f"DEBUG: GROQ chat key count: {len(GROQ_CHAT_API_KEYS)}")

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
    def __init__(self, model_name="llama-3.1-8b-instant", temperature=0.3, key_pool=None):
        try:
            from groq import Groq
            self._groq_class = Groq
            self.model_name = model_name
            self.temperature = temperature
            self.key_pool = key_pool or ANALYSIS_KEY_POOL
            self.available = True
        except ImportError:
            print("⚠️  Groq not installed. Install with: pip install groq")
            self.available = False
            self.key_pool = None
        except Exception as e:
            print(f"⚠️  Groq initialization failed: {e}")
            self.available = False
            self.key_pool = None

    @staticmethod
    def _should_retry(error: Exception) -> bool:
        msg = str(error).lower()
        retry_markers = [
            "429",
            "rate limit",
            "too many requests",
            "timeout",
            "connection",
            "temporarily",
            "service unavailable",
        ]
        return any(marker in msg for marker in retry_markers)

    @staticmethod
    def _retry_delay(attempt: int) -> float:
        base = GROQ_RETRY_BASE_SECONDS * (2 ** attempt)
        delay = min(base, GROQ_RETRY_MAX_SECONDS)
        return delay + random.uniform(0, GROQ_RETRY_JITTER_SECONDS)

    def invoke(self, prompt: str):
        if not self.available:
            raise RuntimeError("Groq is not available. Falling back to local LLM.")

        if self.key_pool is None or not self.key_pool.has_keys():
            raise RuntimeError("No Groq API keys configured for this operation.")

        last_error = None
        for attempt in range(GROQ_MAX_RETRIES + 1):
            api_key = self.key_pool.next_key()
            if not api_key:
                raise RuntimeError("No Groq API keys available in configured key pool.")

            try:
                client = self._groq_class(api_key=api_key)
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=2000,
                )
                class Resp: pass
                r = Resp()
                r.content = response.choices[0].message.content
                return r
            except Exception as e:
                last_error = e
                if attempt >= GROQ_MAX_RETRIES or not self._should_retry(e):
                    break
                wait_seconds = self._retry_delay(attempt)
                print(
                    f"[GROQ] Attempt {attempt + 1} failed ({self.key_pool.name} pool): {e}. "
                    f"Retrying in {wait_seconds:.1f}s..."
                )
                time.sleep(wait_seconds)

        raise RuntimeError(f"Groq invocation failed after retries: {last_error}")


# Factory function to get LLM models based on user choice
def get_llm_models(use_cloud: bool = False, for_chat: bool = False):
    """
    Returns (llm_fast, llm) tuple based on processing mode.
    
    Args:
        use_cloud: True for cloud API (fast, privacy concerns), False for local (private, slower)
    
    Returns:
        (llm_fast, llm): Tuple of models for triple extraction and analysis
    """
    if use_cloud and ANALYSIS_KEY_POOL.has_keys():
        print("[CLOUD] Using Groq API (cloud, ultra-fast)")
        # Fast LLM for triple extraction
        llm_fast = GroqLLM(model_name="llama-3.1-8b-instant", temperature=0.0, key_pool=ANALYSIS_KEY_POOL)
        # Smart LLM for analysis/chat
        if for_chat:
            llm = GroqLLM(model_name="llama-3.1-8b-instant", temperature=0.0, key_pool=CHAT_KEY_POOL)
        else:
            llm = GroqLLM(model_name="llama-3.1-8b-instant", temperature=0.0, key_pool=ANALYSIS_KEY_POOL)
    else:
        print("[LOCAL] Using local Ollama models")
        # Fast LLM for triple extraction (speed critical, accuracy less important)
        llm_fast = LocalLLM(model_name="qwen2.5:1.5b", temperature=0.0)
        # Smart LLM for final analysis (accuracy critical)
        llm = LocalLLM(model_name="mistral:7b", temperature=0.0)
    
    return llm_fast, llm


# Default local models for backward compatibility
print("[LOCAL] Initializing default local Ollama models")
llm_fast = LocalLLM(model_name="qwen2.5:1.5b", temperature=0.0)
llm = LocalLLM(model_name="mistral:7b", temperature=0.0)


if __name__ == "__main__":
    print("Testing Neo4j connection...")
    test_neo4j_connection()

    print("Testing Local LLM...")
    response = llm.invoke("Explain what Neo4j is in one short sentence.")
    print("Local LLM says:", response.content) #type:ignore
