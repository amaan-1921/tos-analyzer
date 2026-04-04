# Terms and Conditions Risk Analyzer  

An AI-powered web application that detects potential risks and unfair clauses in Terms & Conditions and Privacy Policy documents using Large Language Models (LLMs) and Knowledge Graphs.  

---

## Overview  
The Terms and Conditions Risk Analyzer enhances user awareness by analyzing complex legal documents and highlighting clauses that may affect user rights.  
It leverages LangChain, Neo4j, and Retrieval-Augmented Generation (RAG) to detect and explain risky clauses through an interactive interface.

---

## Key Features  
- Multi-format document ingestion (text, PDF, DOCX)  
- Neo4j-based knowledge graph for entity and clause relationship mapping  
- RAG-based clause analysis using Ollama LLMs and Legal-BERT embeddings  
- Interactive chat interface for document exploration  
- Full-stack architecture with FastAPI (backend) and React + Tailwind CSS (frontend)  
- Analysis result caching and parallel processing for improved performance

---

## Tech Stack  
**Frontend:** React, Tailwind CSS  
**Backend:** Python, FastAPI, LangChain  
**Database:** Neo4j  
**Models:** Ollama (qwen2.5:1.5b / phi3:mini / tinyllama), Legal-BERT  
**Architecture:** Retrieval-Augmented Generation (RAG)

---

## System Architecture  
```text
Document Input → Preprocessing → Clause Extraction → Embedding (Ollama + Legal-BERT)
      ↓
Neo4j Knowledge Graph ←→ RAG Pipeline ←→ LangChain
      ↓
Frontend (React + Tailwind) → Chat-based Exploration Interface
```

---

## Prerequisites

- **Docker Desktop** (for Neo4j)
- **Python 3.11+** with virtual environment
- **Node.js 18+** and npm
- **Ollama** with a small model pulled (e.g., `qwen2.5:1.5b`, `phi3:mini`, or `tinyllama`)
  ```bash
  ollama pull qwen2.5:1.5b
  ```

---

## Setup & Installation

### 1. Clone the Repository
```bash
git clone <repo-url>
cd tos-analyzer
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# or: source .venv/bin/activate  # macOS/Linux

# Install dependencies
cd backend
pip install -r requirements.txt
pip install ollama python-multipart  # Additional required packages (only download if the installation fo these packages failed while installing the requirements from the requirements.txt file)

# Download spaCy model
python -m spacy download en_core_web_sm

# Create .env file in backend directory
# Add these lines to backend/.env:
# NEO4J_URL=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=strongpasswd
# GROQ_API_KEY=<single_key_optional>
# GROQ_API_KEYS=<comma_separated_analysis_keys>
# GROQ_CHAT_API_KEYS=<comma_separated_chat_keys>
# ENABLE_ANALYSIS_CACHE=false
# CLOUD_BATCH_SIZE=10
# CLOUD_MAX_WORKERS=4
# RAG_TOP_K=8
# RISK_MIN_SCORE=6
```

### 3. Start Neo4j Database
```bash
# From project root
docker compose up -d neo4j
```

### 4. Create Neo4j Vector Index (One-Time Setup)
**Run this command once after starting Neo4j for the first time:**
```bash
docker exec tos-neo4j cypher-shell -u neo4j -p strongpasswd "DROP INDEX chunk_embeddings IF EXISTS; CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS FOR (c:Chunk) ON (c.embedding) OPTIONS {indexConfig: {``vector.dimensions``: 512, ``vector.similarity_function``: 'cosine'}};"
```

**Note:** This index persists in the Neo4j volume. You only need to re-run this if you:
- Change embedding dimensions
- Delete the `neo4j_data` volume
- Run `docker compose down -v`

### 5. Frontend Setup
```bash
cd frontend
npm install
```

---

## Running the Application

### Start All Services

**Terminal 1 - Backend:**
```bash
cd backend/src
uvicorn main:app --reload
```
Backend runs on: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:5173`

### Access the Application
Open your browser and navigate to: `http://localhost:5173`

---

## Usage

1. **Upload Document**: Click "Upload Terms of Service" and select a `.txt`, `.pdf`, or `.html` file
2. **Analysis**: Wait for the initial analysis to complete (~2-10 minutes depending on document size)
3. **Review Results**: View detected risky clauses with categories and explanations
4. **Ask Questions**: Use the chat interface to ask specific questions about the document

**Note:** Analysis cache behavior is controlled by `ENABLE_ANALYSIS_CACHE` in `backend/.env`.

---

## Restarting After Closing

If you've closed everything and want to restart:

```bash
# 1. Start Neo4j (if not running)
docker compose up -d neo4j

# 2. Start backend (in terminal 1, from project root)
cd backend/src
uvicorn main:app --reload

# 3. Start frontend (in terminal 2, from project root)
cd frontend
npm run dev
```

**The Neo4j vector index and data persist in Docker volumes** — no need to recreate them.

---

## Performance Optimization

- **Caching**: Analysis results are cached per document (based on content hash)
- **Cloud Reliability**: Supports multiple Groq API keys with retry + backoff for rate limits
- **Parallel Processing**: Triple extraction workers and batch sizes are configurable in `backend/.env`
- **Small Models**: For systems with limited RAM (<4GB), use smaller Ollama models:
  - `qwen2.5:1.5b` (recommended)
  - `phi3:mini`
  - `tinyllama`

Edit `backend/src/langchain_setup.py` to change the model:
```python
llm = LocalLLM(model_name="qwen2.5:1.5b")  # Change model name here
```

---

## Troubleshooting

### Neo4j Connection Issues
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# View Neo4j logs
docker logs tos-neo4j
```

### Backend Errors
```bash
# Check if all dependencies are installed
pip list | grep -E "fastapi|uvicorn|neo4j|ollama"

# Verify Ollama is running
ollama list
```

### Memory Issues
If you see "model requires more system memory" errors:
1. Check available RAM: Task Manager → Performance → Memory
2. Close other applications
3. Switch to a smaller Ollama model (see Performance Optimization)

### Dimension Mismatch Errors
If you see "Index query vector has X dimensions, but indexed vectors have Y":
1. Drop and recreate the vector index with correct dimensions (see step 4 above)
2. Re-upload the document

---

## Project Structure
```
tos-analyzer/
├── backend/
│   ├── src/
│   │   ├── main.py          # FastAPI application
│   │   ├── ingest.py        # Document ingestion & triple extraction
│   │   ├── retrieve.py      # RAG & vector search
│   │   ├── langchain_setup.py  # LLM & Neo4j setup
│   │   ├── models.py        # Pydantic models
│   │   └── text_processor.py  # Text chunking & embeddings
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   └── App.jsx
│   └── package.json
├── docker-compose.yaml
└── README.md
```

---

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing patterns
- Tests are included for new features
- Documentation is updated

---

## License

[Add your license here]
