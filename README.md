# Windows Policy Intelligence Engine

An advanced, AI-driven toolset for parsing, analyzing, searching, and managing Microsoft Windows Group Policy (ADMX/ADML) definitions.

This project provides a complete end-to-end pipeline:
- **Parser**: Converts complex XML ADMX/ADML files into structured JSON.
- **Database**: High-performance SQLite database with Full-Text Search (FTS5).
- **API**: A FastAPI backend providing RESTful endpoints for policy queries.
- **Frontend**: A modern React (Vite + Tailwind CSS v4) dashboard.
- **Script Generator**: Jinja2 templating to dynamically build PowerShell remediation, rollback scripts, and Intune OMA-URI profiles.
- **Diff Engine**: A comparison tool to track additions and deprecations between ADMX snapshots.
- **Intelligence**: A local RAG pipeline (Ollama + ChromaDB) and graph correlator for security scoring and AI recommendations.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.9+**
- **Node.js 18+** (for the React Frontend)
- **Ollama** (for local AI features)

### 2. Backend Environment Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the local SQLite database (`policies.db`)**:
   Before starting the API, you must populate the database using the provided examples.
   ```bash
   python db_examples.py
   ```

3. **Start the FastAPI server**:
   The backend provides endpoints for searching, querying registry operations, and script generation.
   ```bash
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```
   *Note: To prevent SQLite background thread errors, the database connection is initialized with `check_same_thread=False`.*
   Interactive API documentation will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Frontend Environment Setup

The frontend is a modern React application built with Vite and Tailwind CSS.
It is configured to proxy API requests (e.g., `/scripts`, `/search`, `/registry`) to the local FastAPI backend running on `http://127.0.0.1:8000`.

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install npm dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. **Additional Frontend Commands**:
   - `npm run build`: Build for production.
   - `npm run lint`: Run ESLint checks.

*Note: The frontend uses modern React conventions (React 19+) where explicit `import React from 'react'` is not required for JSX. To prevent peer dependency conflicts, `eslint` and `@eslint/js` are kept at v9.x.*

### 4. Setting up Local AI Models (Ollama)

If you plan to use the AI Assistant features, install and start Ollama, then pull the necessary models:
```bash
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

---

## 🧠 Advanced Features

### 📜 Script Generation
The script generation module (`admx_parser/scripting/`) uses a Strategy Pattern to handle different script formats and a `PolicyMapper` for extracting registry operations.
The engine dynamically uses Jinja2 templates to build PowerShell `.ps1`, Registry `.reg` files, and Intune Custom Configuration Profiles (OMA-URI).

**Via CLI**:
Generate local `.ps1` and `.reg` test files for an example policy:
```bash
python script_examples.py
```
This generates files such as `*_detect.ps1`, `*_remediate.ps1`, `*_rollback.ps1`, `*_validate.ps1`, and `*.reg` in the `generated_scripts/` directory.

**Via API**:
Scripts can be dynamically generated using the `/scripts` FastAPI endpoint.
For Intune OMA-URI generation, invoke the API with `script_type=intune`.

### 🤖 LLM and RAG Integration
AI capabilities are implemented using `langchain_ollama` modules (replacing deprecated `langchain_community` modules).
Specifically, it relies on `OllamaLLM` for generation and `OllamaEmbeddings` for vector searches.

**Local RAG Pipeline (ChromaDB)**
Index parsed policies into the local vector database:
```bash
python rag_examples.py --index
```
Once indexed, query the AI locally via the CLI:
```bash
python rag_examples.py
```

**AI Remediation via API**:
You can invoke AI-driven remediation suggestions through the API by setting `script_type=ai_remediation` with a configurable `model` parameter.

### 🛡️ Policy Intelligence & Security Scoring
Detect registry conflicts, generate a dependency graph, and assign security risk scores to your policies:
```bash
python intelligence_examples.py
```

### 🔍 ADMX Version Diffing
Compare two different versions of ADMX outputs (e.g., Windows 10 vs Windows 11 policies):
```bash
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
│   ├── scripting/           # Strategy Pattern & Jinja2 Script Generator
│   ├── models.py            # Dataclasses
│   └── parser.py            # XML to JSON logic
├── api/                     # FastAPI Backend
├── frontend/                # React Vite Application
├── examples/                # Example Output JSONs
├── main.py                  # CLI Entry point for parsing
├── requirements.txt         # Python dependencies
└── README.md                # This file
```
