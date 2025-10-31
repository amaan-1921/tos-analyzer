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
- RAG-based clause analysis using DeepSeek-R1 (7B) and Legal-BERT embeddings  
- Interactive chat interface for document exploration  
- Full-stack architecture with FastAPI (backend) and React + Tailwind CSS (frontend)  
- Ongoing improvements including multi-LLM integration, UI/UX enhancements, and performance optimization  

---

## Tech Stack  
**Frontend:** React, Tailwind CSS  
**Backend:** Python, FastAPI, LangChain  
**Database:** Neo4j  
**Models:** DeepSeek-R1 (7B), Legal-BERT  
**Architecture:** Retrieval-Augmented Generation (RAG)

---

## System Architecture  
```text
Document Input → Preprocessing → Clause Extraction → Embedding (DeepSeek-R1 + Legal-BERT)
      ↓
Neo4j Knowledge Graph ←→ RAG Pipeline ←→ LangChain
      ↓
Frontend (React + Tailwind) → Chat-based Exploration Interface
