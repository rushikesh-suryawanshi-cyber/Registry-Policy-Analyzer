# Windows Policy Intelligence Engine

An advanced, AI-driven toolset for parsing, analyzing, searching, and managing Microsoft Windows Group Policy (ADMX/ADML) definitions. 

This project provides a complete end-to-end pipeline:
- **Parser**: Converts complex XML ADMX/ADML files into structured JSON.
- **Database**: High-performance SQLite database with Full-Text Search (FTS5).
- **API**: A FastAPI backend providing RESTful endpoints for policy queries.
- **Frontend**: A modern React (Vite + Tailwind CSS v4) dashboard.
- **Script Generator**: Jinja2 templating to dynamically build PowerShell remediation and rollback scripts.
- **Diff Engine**: A comparison tool to track additions and deprecations between ADMX snapshots.
- **Intelligence**: A local RAG pipeline (Ollama + ChromaDB) and graph correlator for security scoring and AI recommendations.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.9+**
- **Node.js 18+** (for the React Frontend)
- **Ollama** (for local AI features)

### 2. Environment Setup

Install the required Python dependencies:
```powershell
pip install -r requirements.txt
```

If you plan to use the AI Assistant features, install and start Ollama, then pull the necessary models:
```powershell
ollama pull llama3
ollama pull nomic-embed-text
```

### 3. Parsing ADMX Files
Place your ADMX/ADML files in a directory. Run the parser to convert them into a structured JSON file:

```powershell
python main.py
```
*(By default, this looks in `/home/rsuryawanshi/admx_files/...` but you can edit the script to point to your local Windows `C:\Windows\PolicyDefinitions` directory).*

### 4. Database & API
Initialize the SQLite database with FTS5 search capabilities and start the FastAPI server:

```powershell
uvicorn api.main:app --reload
```
You can view the interactive API documentation at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 5. Running the React Frontend
Open a new terminal window, navigate to the `frontend` folder, and start the Vite development server:

```powershell
cd frontend
npm install
npm run dev
```
Open your browser to [http://localhost:5173](http://localhost:5173) to view the modern Policy Intelligence Dashboard.

---

## 🧠 Advanced Features

### Local RAG Pipeline (AI Assistant)
To index your parsed policies into the local ChromaDB vector database:
```powershell
python rag_examples.py --index
```
Once indexed, you can run `python rag_examples.py` to query the AI via the CLI, or use the "AI Assistant" tab in the React Frontend.

### Policy Intelligence & Security Scoring
Run the intelligence module to detect registry conflicts, generate a dependency graph, and assign security risk scores to your policies:
```powershell
python intelligence_examples.py
```

### Script Generation
The engine can dynamically generate PowerShell `.ps1` and Registry `.reg` files. Test the Jinja2 engine locally:
```powershell
python script_examples.py
```

### ADMX Version Diffing
To compare two different versions of ADMX outputs (e.g., Windows 10 vs Windows 11 policies):
```powershell
python diff_report_example.py
```

---

## 📁 Project Architecture

```text
admx ai driven/
├── admx_parser/             # Core Python Engine
│   ├── db/                  # SQLite & FTS5 Repository Layer
│   ├── diff/                # Version Comparison Engine
│   ├── intelligence/        # Graph, Correlator, and Scoring Engine
│   ├── rag/                 # ChromaDB and LangChain Pipeline
│   ├── scripting/           # Jinja2 PowerShell Generator
│   ├── models.py            # Dataclasses
│   └── parser.py            # XML to JSON logic
├── api/                     # FastAPI Backend
├── frontend/                # React Vite Application
├── examples/                # Example Output JSONs
├── main.py                  # CLI Entry point for parsing
├── requirements.txt         # Python dependencies
└── README.md                # This file
```
