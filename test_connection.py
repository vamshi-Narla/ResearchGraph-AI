
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(Path(__file__).with_name(".env"), override=True)

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
database = os.getenv("NEO4J_DATABASE")

missing_settings = [
    name
    for name, value in (
        ("NEO4J_URI", uri),
        ("NEO4J_USERNAME", username),
        ("NEO4J_PASSWORD", password),
        ("NEO4J_DATABASE", database),
    )
    if not value
]
if missing_settings:
    raise ValueError(
        f"Missing required Neo4j settings in .env: {', '.join(missing_settings)}"
    )

with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    driver.verify_connectivity()
    with driver.session(database=database) as session:
        result = session.run(
            "RETURN 'ResearchGraph AI connected!' AS message"
        )
        print(result.single()["message"])
