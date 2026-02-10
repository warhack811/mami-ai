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
        entities = result.get("entities", [])
        if entities:
            # Batch merge entities
            neo4j_client.query(
                """
                UNWIND $entities AS entity
                MERGE (e:Entity {name: entity.name})
                ON CREATE SET e.type = entity.type
                """,
                {"entities": entities}
            )
            # Batch link User to Entities
            neo4j_client.query(
                """
                MATCH (u:User {id: $uid})
                WITH u
                UNWIND $entities AS entity
                MATCH (e:Entity {name: entity.name})
                MERGE (u)-[:KNOWS]->(e)
                """,
                {"uid": user_id, "entities": entities}
            )

        relations = result.get("relations", [])
        if relations:
            # Batch merge relations
            neo4j_client.query(
                """
                UNWIND $relations AS rel
                MATCH (a:Entity {name: rel.source}), (b:Entity {name: rel.target})
                MERGE (a)-[:RELATION {type: rel.type}]->(b)
                """,
                {"relations": relations}
            )

        print(f"Memory consolidated for user {user_id}")
    except Exception as e:
        print(f"Error consolidating memory: {e}")
