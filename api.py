import csv
import json
import logging
import os
import re
import sqlite3
import uuid
from contextlib import asynccontextmanager, contextmanager
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError
from pydantic import BaseModel, Field, field_validator

load_dotenv(Path(__file__).with_name(".env"))

logger = logging.getLogger("researchgraph.api")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or None
COLLECTION_DB_PATH = Path(
    os.getenv(
        "RESEARCHGRAPH_LOCAL_DB",
        str(Path(__file__).with_name("researchgraph-local.sqlite3")),
    )
)
driver = None


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if hasattr(value, "iso_format"):
        return value.iso_format()
    if all(hasattr(value, axis) for axis in ("x", "y")):
        point = {"x": value.x, "y": value.y}
        if hasattr(value, "z"):
            point["z"] = value.z
        return point
    return str(value)


def get_driver():
    if driver is None:
        raise HTTPException(
            status_code=503,
            detail="Neo4j is not configured. Check the required NEO4J_* settings.",
        )
    return driver


def run_query(query: str, parameters: dict[str, Any] | None = None) -> list[dict]:
    try:
        with get_driver().session(database=NEO4J_DATABASE) as session:
            return [
                json_safe(record.data())
                for record in session.run(query, parameters or {})
            ]
    except HTTPException:
        raise
    except (DriverError, Neo4jError) as exc:
        logger.warning("Neo4j query failed (%s)", type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail="The database could not complete this request.",
        ) from exc


def initialize_local_store() -> None:
    COLLECTION_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(COLLECTION_DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS collection_papers (
                collection_id TEXT NOT NULL REFERENCES collections(id)
                    ON DELETE CASCADE,
                paper_id TEXT NOT NULL,
                PRIMARY KEY (collection_id, paper_id)
            );
            """
        )


@contextmanager
def collection_connection():
    connection = sqlite3.connect(COLLECTION_DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global driver
    initialize_local_store()
    if NEO4J_URI and NEO4J_USERNAME and NEO4J_PASSWORD:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        )
    else:
        logger.warning("Neo4j credentials are not configured.")
    try:
        yield
    finally:
        if driver is not None:
            driver.close()
            driver = None


app = FastAPI(
    title="ResearchGraph AI API",
    description="Evidence-first research discovery over your Neo4j graph.",
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "RESEARCHGRAPH_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Enter a research question.")
        return value


class CompareRequest(BaseModel):
    paper_ids: list[str] = Field(min_length=2, max_length=4)

    @field_validator("paper_ids")
    @classmethod
    def paper_ids_must_be_unique(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("Paper identifiers cannot be blank.")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("Choose each paper only once.")
        return cleaned


class CollectionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)

    @field_validator("name")
    @classmethod
    def collection_name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Collection name cannot be blank.")
        return value


class ImportPreviewRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(max_length=2_000_000)


@app.get("/")
def root():
    return {
        "name": "ResearchGraph AI",
        "message": "ResearchGraph AI API is running.",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():
    try:
        with get_driver().session(database=NEO4J_DATABASE) as session:
            session.run("RETURN 1 AS ok").single()
    except HTTPException:
        raise
    except (DriverError, Neo4jError) as exc:
        logger.warning("Neo4j health check failed (%s)", type(exc).__name__)
        raise HTTPException(
            status_code=503,
            detail="The API is running, but its Neo4j connection is unavailable.",
        ) from exc
    return {
        "status": "connected",
        "service": "ResearchGraph AI",
        "database": NEO4J_DATABASE or "server default",
    }


@app.get("/api/stats")
def stats():
    node_records = run_query(
        """
        MATCH (n)
        UNWIND labels(n) AS label
        RETURN label, count(DISTINCT n) AS count
        ORDER BY label
        """
    )
    relationship_records = run_query(
        """
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(r) AS count
        ORDER BY type
        """
    )
    node_counts = {row["label"]: row["count"] for row in node_records}
    relationship_counts = {
        row["type"]: row["count"] for row in relationship_records
    }
    totals = run_query("MATCH (n) RETURN count(n) AS total")
    return {
        "total_nodes": totals[0]["total"] if totals else 0,
        "total_relationships": sum(relationship_counts.values()),
        "papers": node_counts.get("Paper", 0),
        "authors": node_counts.get("Author", 0),
        "concepts": node_counts.get("Concept", 0),
        "methods": node_counts.get("Method", 0),
        "nodes_by_label": node_counts,
        "relationships_by_type": relationship_counts,
    }


@app.get("/api/papers")
def papers(
    search: str = Query(default="", max_length=200),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100_000),
    sort: str = Query(default="title", pattern="^(title|year)$"),
):
    records = run_query(
        """
        MATCH (p:Paper)
        WHERE $search = ""
            OR any(
                field IN [p.title, p.name, p.abstract, p.doi, p.domain]
                WHERE toLower(toString(coalesce(field, "")))
                    CONTAINS toLower($search)
            )
            OR EXISTS {
                MATCH (p)-[:AUTHORED_BY]-(a:Author)
                WHERE toLower(coalesce(a.name, "")) CONTAINS toLower($search)
            }
        WITH p
        ORDER BY
            CASE WHEN $sort = "year" THEN toInteger(p.year) END DESC,
            toLower(coalesce(p.title, p.name, p.id, ""))
        RETURN elementId(p) AS element_id, properties(p) AS properties
        SKIP $offset
        LIMIT $limit
        """,
        {"search": search.strip(), "limit": limit, "offset": offset, "sort": sort},
    )
    return {
        "count": len(records),
        "limit": limit,
        "offset": offset,
        "papers": [
            {
                "id": str(row["properties"].get("id") or row["element_id"]),
                "element_id": row["element_id"],
                **row["properties"],
            }
            for row in records
        ],
    }


@app.get("/api/papers/{paper_id}")
def paper_detail(paper_id: str):
    rows = run_query(
        """
        MATCH (p:Paper)
        WHERE toString(p.id) = $paper_id OR elementId(p) = $paper_id
        OPTIONAL MATCH (p)-[r]-(related)
        RETURN
            elementId(p) AS element_id,
            properties(p) AS properties,
            collect(DISTINCT CASE WHEN related IS NULL THEN null ELSE {
                id: elementId(related),
                labels: labels(related),
                properties: properties(related),
                relationship: type(r)
            } END) AS connections
        LIMIT 1
        """,
        {"paper_id": paper_id},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Paper not found.")
    row = rows[0]
    return {
        "id": str(row["properties"].get("id") or row["element_id"]),
        "element_id": row["element_id"],
        "properties": row["properties"],
        "connections": [item for item in row["connections"] if item is not None],
    }


@app.get("/api/search")
def search(
    q: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
):
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Search query cannot be blank.")
    records = run_query(
        """
        MATCH (n)
        WHERE any(
            key IN keys(n)
            WHERE toLower(toString(coalesce(n[key], "")))
                CONTAINS toLower($query)
        )
        RETURN elementId(n) AS id, labels(n) AS labels,
               properties(n) AS properties
        ORDER BY coalesce(n.title, n.name, n.id, "")
        LIMIT $limit
        """,
        {"query": query, "limit": limit},
    )
    return {"query": query, "count": len(records), "results": records}


@app.get("/api/graph")
def graph(limit: int = Query(default=100, ge=1, le=200)):
    node_records = run_query(
        """
        MATCH (n)
        RETURN elementId(n) AS id, labels(n) AS labels,
               properties(n) AS properties
        ORDER BY elementId(n)
        LIMIT $limit
        """,
        {"limit": limit},
    )
    node_ids = [row["id"] for row in node_records]
    edge_records = run_query(
        """
        MATCH (a)-[r]->(b)
        WHERE elementId(a) IN $node_ids AND elementId(b) IN $node_ids
        RETURN DISTINCT elementId(r) AS id,
               elementId(a) AS source, elementId(b) AS target, type(r) AS type
        LIMIT $limit
        """,
        {"node_ids": node_ids, "limit": min(limit * 3, 600)},
    ) if node_ids else []
    return {
        "nodes": node_records,
        "edges": edge_records,
        "count": {"nodes": len(node_records), "relationships": len(edge_records)},
        "truncated": len(node_records) == limit,
    }


@app.get("/api/nodes/{node_id}")
def node_detail(node_id: str):
    rows = run_query(
        """
        MATCH (n)
        WHERE elementId(n) = $node_id
        RETURN elementId(n) AS id, labels(n) AS labels,
               properties(n) AS properties
        LIMIT 1
        """,
        {"node_id": node_id},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Graph node not found.")
    return rows[0]


@app.get("/api/nodes/{node_id}/connections")
def node_connections(
    node_id: str,
    limit: int = Query(default=100, ge=1, le=200),
):
    rows = run_query(
        """
        MATCH (n)-[r]-(related)
        WHERE elementId(n) = $node_id
        RETURN DISTINCT elementId(related) AS id, labels(related) AS labels,
               properties(related) AS properties, type(r) AS relationship
        LIMIT $limit
        """,
        {"node_id": node_id, "limit": limit},
    )
    return {"node_id": node_id, "count": len(rows), "connections": rows}


@app.post("/api/assistant/query")
def assistant_query(request: AssistantRequest):
    stop_words = {
        "about", "after", "also", "among", "and", "are", "can", "could",
        "does", "for", "from", "have", "how", "into", "list", "many",
        "mention", "mentions", "more", "most", "paper", "papers", "please",
        "research", "show", "that", "the", "their", "these", "this", "those",
        "what", "when", "where", "which", "who", "why", "with", "would",
    }
    terms = list(dict.fromkeys(
        term.lower()
        for term in re.findall(r"[\w-]{3,}", request.question)
        if term.lower() not in stop_words
    ))
    if not terms:
        raise HTTPException(
            status_code=422,
            detail="Include a searchable research term of at least three characters.",
        )
    rows = run_query(
        """
        MATCH (n)
        WHERE any(
            key IN keys(n)
            WHERE any(
                term IN $terms
                WHERE toLower(toString(coalesce(n[key], "")))
                    CONTAINS term
            )
        )
        OR (
            "author" IN $terms
            AND "Author" IN labels(n)
        )
        OR (
            "concept" IN $terms
            AND "Concept" IN labels(n)
        )
        OR (
            "method" IN $terms
            AND "Method" IN labels(n)
        )
        RETURN elementId(n) AS id, labels(n) AS labels,
               properties(n) AS properties
        ORDER BY coalesce(n.title, n.name, n.id, "")
        LIMIT 12
        """,
        {"terms": terms},
    )
    sources = [
        {
            "id": row["properties"].get("id") or row["id"],
            "labels": row["labels"],
            "properties": row["properties"],
        }
        for row in rows
    ]
    return {
        "mode": "database_evidence_retrieval",
        "notice": (
            "This is database evidence retrieval, not an AI-generated answer. "
            "No external scholarly sources were queried."
        ),
        "question": request.question,
        "terms": terms,
        "count": len(sources),
        "sources": sources,
    }


@app.post("/api/compare")
def compare(request: CompareRequest):
    rows = run_query(
        """
        MATCH (p:Paper)
        WHERE toString(p.id) IN $paper_ids OR elementId(p) IN $paper_ids
        RETURN coalesce(toString(p.id), elementId(p)) AS id,
               properties(p) AS properties
        LIMIT 4
        """,
        {"paper_ids": request.paper_ids},
    )
    found = {row["id"]: row["properties"] for row in rows}
    missing = [paper_id for paper_id in request.paper_ids if paper_id not in found]
    if missing:
        raise HTTPException(
            status_code=404,
            detail="One or more selected paper records were not found.",
        )
    return {
        "papers": [
            {"id": paper_id, "properties": found[paper_id]}
            for paper_id in request.paper_ids
        ],
        "fields": [
            "title", "year", "domain", "publication_type", "source_type",
            "abstract", "doi", "source_url", "methodology", "dataset",
            "findings", "limitations",
        ],
    }


@app.get("/api/gaps")
def candidate_gaps(limit: int = Query(default=20, ge=1, le=100)):
    rows = run_query(
        """
        MATCH (c:Concept)
        OPTIONAL MATCH (c)-[]-(p:Paper)
        WITH c, collect(DISTINCT p) AS linked_papers
        WITH c, [paper IN linked_papers WHERE paper IS NOT NULL] AS linked_papers
        RETURN elementId(c) AS id, properties(c) AS concept,
               size(linked_papers) AS paper_count,
               [paper IN linked_papers |
                   {id: toString(paper.id), title: paper.title}] AS papers
        ORDER BY paper_count ASC, coalesce(c.name, "")
        LIMIT $limit
        """,
        {"limit": limit},
    )
    return {
        "scope": "Current indexed database only; candidate signals, not universal gaps.",
        "count": len(rows),
        "candidates": rows,
    }


@app.get("/api/collections")
def list_collections():
    with collection_connection() as connection:
        rows = connection.execute(
            """
            SELECT c.id, c.name, c.created_at,
                   (SELECT COUNT(*) FROM collection_papers AS count_papers
                    WHERE count_papers.collection_id = c.id) AS paper_count,
                   COALESCE(
                       (SELECT json_group_array(saved.paper_id)
                        FROM collection_papers AS saved
                        WHERE saved.collection_id = c.id),
                       '[]'
                   ) AS paper_ids
            FROM collections AS c
            ORDER BY c.created_at DESC
            """
        ).fetchall()
    return {
        "collections": [
            {
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"],
                "paper_count": row["paper_count"],
                "paper_ids": json.loads(row["paper_ids"]),
            }
            for row in rows
        ]
    }


@app.post("/api/collections", status_code=201)
def create_collection(request: CollectionRequest):
    collection_id = str(uuid.uuid4())
    created_at = datetime.now().astimezone().isoformat()
    with collection_connection() as connection:
        connection.execute(
            "INSERT INTO collections (id, name, created_at) VALUES (?, ?, ?)",
            (collection_id, request.name, created_at),
        )
    return {
        "id": collection_id,
        "name": request.name,
        "created_at": created_at,
        "paper_count": 0,
        "paper_ids": [],
    }


@app.patch("/api/collections/{collection_id}")
def rename_collection(collection_id: str, request: CollectionRequest):
    with collection_connection() as connection:
        cursor = connection.execute(
            "UPDATE collections SET name = ? WHERE id = ?",
            (request.name, collection_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Collection not found.")
    return {"id": collection_id, "name": request.name}


@app.delete("/api/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    with collection_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM collections WHERE id = ?",
            (collection_id,),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Collection not found.")


@app.post("/api/collections/{collection_id}/papers", status_code=201)
def add_paper_to_collection(collection_id: str, paper_id: str = Query(min_length=1)):
    exists = run_query(
        """
        MATCH (p:Paper)
        WHERE toString(p.id) = $paper_id OR elementId(p) = $paper_id
        RETURN count(p) > 0 AS exists
        """,
        {"paper_id": paper_id},
    )
    if not exists or not exists[0]["exists"]:
        raise HTTPException(status_code=404, detail="Paper not found.")
    with collection_connection() as connection:
        collection = connection.execute(
            "SELECT 1 FROM collections WHERE id = ?",
            (collection_id,),
        ).fetchone()
        if collection is None:
            raise HTTPException(status_code=404, detail="Collection not found.")
        connection.execute(
            """
            INSERT OR IGNORE INTO collection_papers (collection_id, paper_id)
            VALUES (?, ?)
            """,
            (collection_id, paper_id),
        )
    return {"collection_id": collection_id, "paper_id": paper_id}


@app.delete("/api/collections/{collection_id}/papers", status_code=204)
def remove_paper_from_collection(
    collection_id: str,
    paper_id: str = Query(min_length=1),
):
    with collection_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM collection_papers
            WHERE collection_id = ? AND paper_id = ?
            """,
            (collection_id, paper_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Saved paper not found in this collection.",
            )


@app.post("/api/import/preview")
def import_preview(request: ImportPreviewRequest):
    suffix = Path(request.filename).suffix.lower()
    if suffix not in {".csv", ".json"}:
        raise HTTPException(
            status_code=415,
            detail="Supported preview formats are CSV and JSON.",
        )
    try:
        if suffix == ".json":
            data = json.loads(request.content)
            if isinstance(data, dict) and isinstance(data.get("papers"), list):
                records = data["papers"]
            elif isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = [data]
            else:
                raise ValueError("JSON must contain a paper object or list.")
        else:
            records = list(csv.DictReader(request.content.splitlines()))
    except (json.JSONDecodeError, csv.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {exc}") from exc

    if not records:
        raise HTTPException(status_code=400, detail="The file contains no records.")
    if len(records) > 500:
        raise HTTPException(
            status_code=413,
            detail="Preview is limited to 500 records at a time.",
        )

    supported_fields = {
        "id", "title", "abstract", "year", "doi", "source_url", "domain",
        "publication_type", "keywords", "methodology", "dataset", "findings",
        "limitations",
    }
    errors = []
    warnings = []
    preview = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append({"row": index, "message": "Each record must be an object."})
            continue
        normalized = {
            str(key).strip().lower(): value
            for key, value in record.items()
        }
        if not str(normalized.get("title") or "").strip():
            errors.append({"row": index, "message": "Required field 'title' is missing."})
            continue
        unknown = sorted(set(normalized) - supported_fields)
        if unknown:
            warnings.append({"row": index, "ignored_fields": unknown})
        preview.append({
            key: json_safe(value)
            for key, value in normalized.items()
            if key in supported_fields
        })

    return {
        "filename": Path(request.filename).name,
        "format": suffix[1:],
        "preview_only": True,
        "database_written": False,
        "supported_fields": sorted(supported_fields),
        "columns": sorted({
            key for record in records if isinstance(record, dict) for key in record
        }),
        "valid_count": len(preview),
        "invalid_count": len(errors),
        "warnings": warnings,
        "errors": errors,
        "records": preview[:20],
        "records_truncated": len(preview) > 20,
    }
