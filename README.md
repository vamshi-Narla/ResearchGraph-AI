# ResearchGraph AI

ResearchGraph AI is a local research workspace backed by the existing Neo4j
Aura graph. The React app reads live graph data through the FastAPI service.
The earlier Streamlit interface remains available in `app.py`.

## Run locally on Windows

Open two PowerShell terminals in the project folder and activate the existing
virtual environment in each:

```powershell
.\.venv\Scripts\Activate.ps1
```

In the first terminal, start the API:

```powershell
python -m uvicorn api:app --reload --port 8011
```

In the second terminal, start Vite:

```powershell
cd frontend
npm run dev
```

Open <http://localhost:5173>. The API is at <http://localhost:8011>, with
interactive API documentation at <http://localhost:8011/docs>.

The API reads `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and
`NEO4J_DATABASE` from the root `.env`. Keep that file private and never put
database credentials in a `VITE_` variable. The optional frontend API base setting is `VITE_API_BASE_URL`; copy
`frontend/.env.example` to `frontend/.env.local` only if you need to override
the local default.

## What is implemented

- Overview counts and paper records are queried from Neo4j, not demo constants.
- Paper search, paper detail, graph browsing, node connections, and bounded
  graph results use the existing Neo4j records.
- The research assistant page is transparent database evidence retrieval; it
  does not call an LLM or search the wider web.
- Comparisons and candidate research-gap signals are computed only from the
  indexed graph and its stored properties.
- Collections are saved in a separate local SQLite file. They do not write to
  or delete records in Neo4j.
- CSV and JSON import supports validation and preview only. It does not write
  previewed records to the graph.
- The settings view reports real API/database connectivity and available local
  capabilities. This local app does not implement user authentication.

## Import preview format

Import preview accepts `.csv` files with a header row or `.json` files
containing one paper object, a list of paper objects, or an object with a
`papers` list. `title` is required. Recognized optional fields are `id`,
`abstract`, `year`, `doi`, `source_url`, `domain`, `publication_type`,
`keywords`, `methodology`, `dataset`, `findings`, and `limitations`.
Preview is limited to 500 rows and reports validation issues without writing
to Neo4j.

## Limits

The assistant does evidence retrieval, not generative AI. Gap exploration
surfaces underrepresented concepts in this graph, not universal claims about
all published research. Records are displayed as stored; the application does
not independently verify publication metadata. The local development API is
not production-secured and should not be exposed to the public internet.
