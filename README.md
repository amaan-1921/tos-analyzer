# ToS Analyzer

A privacy-focused tool that analyzes Terms of Service (ToS) documents to detect risky, unfair, or benign clauses using a locally-hosted language model (e.g., Mistral via LM Studio). Built with React and FastAPI, this project helps users understand potential threats in ToS agreements.

This project is under active development. Future improvements include enhancing detection accuracy, refining the user interface, and deploying a public version.

## Project Structure

```plaintext
tos-analyzer/
  ├── backend/
  │   ├── src/
  │   │   ├── main.py
  │   │   ├── model_predictor.py
  │   │   ├── text_processor.py
  │   │   └── requirements.txt
      └── ...
  ├── frontend/
  │   ├── public/
  │   ├── src/
          └── ...
  │   ├── package.json
  │   └── vite.config.js
      └── ...
```
## Getting Started

### 1. Clone the Repository

git clone https://github.com/amaan-1921/tos-analyzer.git
cd tos-analyzer

### 2. Backend Setup (FastAPI)

Ensure Python 3.10+ is installed.
```bash
cd backend
python -m venv venv
source venv/bin/activate    # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
uvicorn src.main:app --reload
```
### 3. LM Studio Setup (for local LLM)


1. Download and install LM Studio.
2. Load a compatible model (e.g., mistral-7b-instruct-v0.2 GGUF).
3. Enable the "OpenAI-Compatible API Server".
4. Confirm the server is running at http://127.0.0.1:1234.

### 4. Frontend Setup (React + Tailwind + Vite)
```bash
cd ../frontend
npm install
npm run dev
```
Visit http://localhost:5173 in your browser.

## Features


- Detects risky, unfair, or benign clauses in ToS documents.

- Uses a local language model via LM Studio for privacy.

- Supports text input and file upload (.txt).

- Built with React and Tailwind CSS for a clean user interface.

- Modular backend with FastAPI for scalability.

## Tech Stack

- Frontend: React, Vite, Tailwind CSS

- Backend: FastAPI, Python

- AI Model: Mistral (via LM Studio)

## Contributors

- Ansul Kumar

- Mohammed Amaan Thayyil



> Note: This is a research/educational project. The analysis provided is not legal advice.

## Future Plans

- Add support for PDF uploads.

- Containerize the application with Docker.

- Improve clause grouping and analysis accuracy.

- Deploy a hosted version (e.g., Vercel, Render, or Fly.io).
