from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings
from app.graph.client import neo4j_client
from app.worker.celery_app import celery

class Entity(BaseModel):
    name: str = Field(description="Name of the entity (Person, Project, Technology, etc.)")
    type: str = Field(description="Type of the entity")

class Relation(BaseModel):
    source: str = Field(description="Source entity name")
    target: str = Field(description="Target entity name")
    type: str = Field(description="Relationship type (e.g., LIKES, WORKS_ON, LOCATED_IN)")

class KnowledgeGraphUpdate(BaseModel):
    entities: List[Entity] = Field(description="List of entities identified in the text")
    relations: List[Relation] = Field(description="List of relationships identified between entities")

# Initialize LLM for extraction (Use a smaller/faster model for this background task)
# Note: Initializing this at module level in Celery worker is fine.
llm_extractor = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)

parser = JsonOutputParser(pydantic_object=KnowledgeGraphUpdate)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at extracting knowledge graphs from text. Identify key entities and relationships. Return JSON."),
    ("user", "{text}\n\n{format_instructions}")
])

chain = prompt | llm_extractor | parser

@celery.task(name="consolidate_memory_task")
def consolidate_memory_task(user_id: int, text: str):
    """
    Analyzes text to extract knowledge graph elements and updates Neo4j.
    Runs as a Celery task.
    """
    try:
        # Using invoke (synchronous) since Celery tasks are sync by default
        result = chain.invoke({"text": text, "format_instructions": parser.get_format_instructions()})

        # Update Neo4j
        for entity in result.get("entities", []):
            neo4j_client.query(
                "MERGE (e:Entity {name: $name}) ON CREATE SET e.type = $type",
                {"name": entity["name"], "type": entity["type"]}
            )
            # Link User to Entity
            neo4j_client.query(
                "MATCH (u:User {id: $uid}), (e:Entity {name: $name}) MERGE (u)-[:KNOWS]->(e)",
                {"uid": user_id, "name": entity["name"]}
            )

        for relation in result.get("relations", []):
            neo4j_client.query(
                """
                MATCH (a:Entity {name: $source}), (b:Entity {name: $target})
                MERGE (a)-[:RELATION {type: $type}]->(b)
                """,
                {"source": relation["source"], "target": relation["target"], "type": relation["type"]}
            )

        print(f"Memory consolidated for user {user_id}")
    except Exception as e:
        print(f"Error consolidating memory: {e}")
