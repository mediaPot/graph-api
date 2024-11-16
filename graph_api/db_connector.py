import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

from graph_api import queries

load_dotenv()


class Neo4jConnector:
    def __init__(self):
        self.uri = os.environ.get("NEO4J_URI")
        self.user = os.environ.get("NEO4J_USER")
        self.password = os.environ.get("NEO4J_PASSWORD")
        self.db = os.environ.get("NEO4J_DATABASE")
        self.queries = queries

    def get_neo4j_session(self):
        driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
            encrypted=False,
            database=self.db,
        )
        session = driver.session()
        yield session

        session.close()
