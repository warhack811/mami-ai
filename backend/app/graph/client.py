from neo4j import GraphDatabase
from app.core.config import settings

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def query(self, query: str, parameters: dict = None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def add_fact(self, subject: str, predicate: str, object: str, user_id: int):
        query = """
        MERGE (u:User {id: $user_id})
        MERGE (s:Entity {name: $subject})
        MERGE (o:Entity {name: $object})
        MERGE (s)-[:RELATION {type: $predicate}]->(o)
        MERGE (u)-[:KNOWS]->(s)
        """
        self.query(query, {"subject": subject, "predicate": predicate, "object": object, "user_id": user_id})

neo4j_client = Neo4jClient()
