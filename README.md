# ResearchGraph AI

**Evidence-first research discovery and knowledge graph exploration.**

ResearchGraph AI is a local-development research workspace that explores research papers and their relationships in a Neo4j knowledge graph. It uses a React frontend, a FastAPI backend, and SQLite for local paper collections. This repository is intended as a portfolio and learning project, not a hosted production service.

## Contents

- [Features](#features)
- [Technology stack](#technology-stack)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Run locally on Windows](#run-locally-on-windows)
- [Configure Neo4j](#configure-neo4j)
- [Using the application](#using-the-application)
- [API documentation](#api-documentation)
- [Data storage](#data-storage)
- [Troubleshooting](#troubleshooting)
- [Security and limitations](#security-and-limitations)
- [Development checks](#development-checks)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Overview and database status:** check connection health and graph statistics.
- **Paper discovery:** search and browse paper records already stored in Neo4j.
- **Knowledge graph:** explore nodes and relationships.
- **Research assistant:** retrieve graph-backed evidence for a research question. This is not an LLM-powered chatbot.
- **Paper comparison:** compare two to four selected paper records.
- **Research-gap exploration:** inspect gap-related results based on the data and logic available in the project.
- **Collections:** create, rename, list, and delete collections; add or remove paper IDs.
- **Import preview:** validate CSV or JSON research records before any database write. The preview endpoint does **not** import records into Neo4j.
- **Interactive API documentation:** inspect backend endpoints through FastAPI Swagger UI.

Results depend on the contents and structure of the Neo4j database configured by each user.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI, Uvicorn |
| Graph database | Neo4j |
| Local collections | SQLite |
| Configuration | Environment variables, `python-dotenv` |
| Icons | `lucide-react` |

## Architecture

```text
Browser
  |
  v
React + Vite frontend (default: http://localhost:5173)
  |
  | HTTP
  v
FastAPI backend (http://localhost:8011)
  |                         |
  v                         v
Neo4j graph database       SQLite file
research papers,           collections and
authors, concepts,         collection-paper links
methods, relationships
```

The frontend calls the API. Neo4j provides graph data; SQLite stores local collection metadata and associated paper IDs. The frontend API base can be overridden with `VITE_API_BASE_URL`.

## Project structure

```text
ResearchGraph-AI/
├── api.py                       # FastAPI backend
├── app.py                       # Streamlit interface/prototype
├── requirements.txt             # Python dependencies
├── test_connection.py           # Neo4j connectivity check
├── .env                         # Create locally; never commit
├── .gitignore
├── researchgraph-local.sqlite3  # Generated local collection database
└── frontend/
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    └── src/
        ├── api.js               # Frontend API client
        ├── App.jsx              # Main application interface
        ├── App.css
        ├── index.css
        └── main.jsx
```

Some local files, including `.env`, `.venv/`, and `researchgraph-local.sqlite3`, are intentionally excluded from Git. The API creates the SQLite database when needed.

## Requirements

- Windows 10/11
- Git (if cloning)
- Python 3.11 or another version supported by the dependencies
- Node.js and npm
- A reachable Neo4j Aura database or compatible Neo4j instance

Check your tools in PowerShell:

```powershell
py --version
node --version
npm --version
git --version
```

## Run locally on Windows

### 1. Download the project

```powershell
git clone https://github.com/vamshi-Narla/ResearchGraph-AI.git
cd ResearchGraph-AI
```

Alternatively, download the ZIP from GitHub and extract it, then open PowerShell in the extracted project folder.

### 2. Set up Python

Run from the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Configure Neo4j

Create a `.env` file in the project root, beside `api.py`:

```dotenv
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=replace_with_your_own_password
NEO4J_DATABASE=neo4j
```

Replace the sample values with the connection details for your own Neo4j instance. Your URI and database name may differ. Keep `.env` private; never commit it or publish passwords, API keys, or connection strings containing secrets.

### 4. Start the API

In the first PowerShell terminal, from the project root with the virtual environment activated:

```powershell
python -m uvicorn api:app --reload --port 8011
```

Leave this terminal running. The API is available at:

- API root: <http://localhost:8011/>
- Health check: <http://localhost:8011/api/health>
- Interactive API docs: <http://localhost:8011/docs>
- OpenAPI schema: <http://localhost:8011/openapi.json>

The health endpoint checks the connection to the configured Neo4j database.

### 5. Start the frontend

Open a **second PowerShell terminal** in the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually <http://localhost:5173/>.

If Vite selects a different port, use the exact URL printed in the terminal. If you use a non-default port, add its origin to `RESEARCHGRAPH_CORS_ORIGINS` in the API environment and restart the API.

### 6. Stop the servers

Press `Ctrl+C` in each terminal.

## Configure Neo4j

The application expects an existing Neo4j database with research records in a structure compatible with the API queries. The graph may contain labels such as `Paper`, `Author`, `Concept`, and `Method`, with relationships such as `AUTHORED_BY`, `STUDIES`, `USES_METHOD`, and `RELATED_TO`.

Starting the API does not automatically populate a complete research corpus. If the database is empty, search and graph screens may return empty results.

The import feature currently supports **CSV/JSON preview and validation only**. Its response indicates that no database write occurred. Use a separate, deliberate data-loading workflow compatible with the graph schema to populate the database.

## Using the application

1. Start the API and frontend using the steps above.
2. Open the frontend URL printed by Vite.
3. Check database status on the overview/settings interface.
4. Use **Discover papers** to search records in Neo4j.
5. Use **Knowledge graph** to explore available entities and relationships.
6. Use **Research assistant** to retrieve graph-backed evidence for a question.
7. Use the comparison interface to select two to four papers.
8. Create a collection to organize paper IDs; collections are stored in local SQLite.
9. Use **Import data** to preview CSV or JSON records and review validation messages. Previewing does not write records to Neo4j.

Displayed results depend on the database and the records it contains.

## API documentation

With the backend running, visit <http://localhost:8011/docs>. Use the interactive documentation for exact routes, parameters, request bodies, and response formats.

Main API areas include:

| Area | Purpose |
|---|---|
| `GET /` | API information |
| `GET /api/health` | Neo4j connectivity |
| `GET /api/stats` | Graph statistics |
| Paper/search routes | Search and retrieve paper records |
| Graph routes | Retrieve graph nodes and connections |
| Assistant route | Retrieve graph-backed evidence |
| Comparison route | Compare selected papers |
| Research-gap route | Return gap-related analysis |
| Collection routes | Manage collections in SQLite |
| `POST /api/import/preview` | Preview CSV/JSON content without writing it to Neo4j |

The running `/docs` page is the source of truth for the complete route list.

## Data storage

### Neo4j

Stores the research graph used for discovery and graph-backed features. The repository does not provide a complete research corpus for every installation.

### SQLite

By default, the API creates `researchgraph-local.sqlite3` in the project root. It contains:

- `collections`: collection ID, name, and creation timestamp.
- `collection_papers`: collection ID and paper ID associations.

Override the path with `RESEARCHGRAPH_LOCAL_DB`. Deleting the SQLite file removes local collections; back it up first if you need to preserve them.

## Troubleshooting

### Neo4j is not configured or unavailable

- Confirm `.env` is in the project root beside `api.py`.
- Verify `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD`.
- Check `NEO4J_DATABASE` if your instance uses a specific database.
- Confirm the instance is running and reachable.
- Restart the API after editing `.env`.
- Do not paste real credentials into public issues or screenshots.

### The frontend cannot reach the API

- Start the API on port `8011`.
- Check <http://localhost:8011/api/health>.
- Review the browser console and backend terminal.
- If you changed the frontend port, add that origin to `RESEARCHGRAPH_CORS_ORIGINS`.
- If the API runs at another address, set `VITE_API_BASE_URL` for the frontend environment as appropriate.

### Node.js or npm is not recognized

Install Node.js, reopen PowerShell, and check `node --version` and `npm --version`.

### Python dependency errors

Activate `.venv` and run these commands from the project root:

```powershell
python -m pip install -r requirements.txt
python -m pip check
```

### Port 5173 is busy

Vite may choose another port. Open the URL it prints and ensure that origin is allowed by the API CORS configuration.

## Security and limitations

- This is a local development and portfolio project.
- User authentication and per-user access control are not configured.
- Do not expose the development API directly to the public internet.
- Keep `.env` private and ensure it remains ignored by Git.
- CSV/JSON import is preview-only; it does not persist imported records.
- The research assistant uses graph retrieval/application logic and is not an LLM-powered chatbot.
- Search, comparison, and gap-related results depend on the data and schema in Neo4j.
- Counts from a small test graph should not be presented as universal project statistics.

## Development checks

From the project root:

```powershell
python -m pip check
```

From the `frontend` directory:

```powershell
npm install
npm run build
```

These checks verify Python dependency consistency and build the frontend. They do not replace testing the running app against your Neo4j database.

## Contributing

1. Fork the repository.
2. Create a branch for your change.
3. Keep changes focused and document new configuration.
4. Run relevant dependency/build checks.
5. Open a pull request describing the change and how it was tested.

Do not include `.env`, credentials, private datasets, or local SQLite files in contributions.

## License

No license is specified in this README. Unless a license file is added, reuse and redistribution are not automatically granted. Add a `LICENSE` file if you intend to publish the project under a particular open-source license.
