from neo4j import GraphDatabase
from datetime import datetime

#Connect to Neo4j running locally with default credentials
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "geophysicist"))

def create_memory_node(memory):
    with driver.session() as session:
        session.run(
            "MERGE (m:Memory {id: $id, summary: $summary})",
            id = memory["id"],
            summary = memory["summary"]
        )

def relate_memories(id1, id2, rel_type="RELATED_TO"):
    """
    Create a relationship of type rel_type between two memories by id.
    """
    with driver.session() as session:
        session.run(
            f"""
            MATCH (a:Memory {{id: $id1}})
            MATCH (b:Memory {{id: $id2}})
            MERGE (a)-[r:{rel_type}]->(b)
            """,
            id1=id1, id2=id2
        )



def find_related_memories(memory_id, hops=2):
    with driver.session() as session:
        result = session.run(
            f"""
            MATCH (start:Memory {{id: $memory_id}})
            MATCH path = (start)-[*1..{hops}]-(related:Memory)
            RETURN DISTINCT related.id AS related_id, related.summary AS summary
            """,
            memory_id=memory_id
        )
        return [(record["related_id"], record["summary"]) for record in result]
