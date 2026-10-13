## Run locally on Windows

### Prerequisites

- Python 3.11 or a compatible version supported by the dependencies.
- Node.js and npm.
- Access to a Neo4j Aura database, or another compatible Neo4j instance.

### 1. Download the project

Clone the repository:

```powershell
git clone https://github.com/vamshi-Narla/ResearchGraph-AI.git
cd ResearchGraph-AI
```

Alternatively, download the ZIP from GitHub and extract it.

### 2. Set up the Python environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Neo4j

Create a `.env` file in the project root. Add your own Neo4j connection details:

```dotenv
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=your_neo4j_database
```

Replace the example values with your own credentials. Never commit `.env` or publish database passwords.

### 4. Install frontend dependencies

Open a second PowerShell terminal in the project root:

```powershell
cd frontend
npm install
npm run dev
```

### 5. Start the API

In the first terminal, from the project root with the Python environment activated:

```powershell
python -m uvicorn api:app --reload --port 8011
```

Open the frontend at http://localhost:5173.

The API documentation is available at http://localhost:8011/docs.

If the frontend uses a different port, open the local URL printed by Vite in the terminal.

**Note:** This is a local development setup. The application does not implement user authentication and should not be exposed directly to the public internet.