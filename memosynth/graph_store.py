from neo4j import AsyncGraphDatabase
from datetime import datetime
from memosynth.utility import call_ollama
import json
from json_repair import repair_json


import re


#Connect to Neo4j running locally with default credentials
driver = AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "geophysicist"))

async def create_memory_node(memory):
    async with driver.session() as session:
        await session.run(
            "MERGE (m:Memory {id: $id, summary: $summary})",
            id = memory["id"],
            summary = memory["summary"]
        )

async def relate_memories(source_id, target_id, relationship="RELATED_TO"):
    async with driver.session() as session:
        await session.run(
            f"""
            MATCH (a:Memory {{id: $source_id}})
            MATCH (b:Memory {{id: $target_id}})
            MERGE (a)-[r:{relationship}]->(b)
            """,
            source_id=source_id, target_id=target_id
        )



async def extract_entities_and_relationships(summary):
    prompt = (
        "Extract entities and relationships from the following text. "
        "You MUST return ONLY a valid JSON object with exactly these two keys: 'nodes' and 'edges'. "
        "Do not include any text before or after the JSON. "
        "Do not add explanations or comments. "
        "Do not use trailing commas. "
        "Format:\n"
        '{\n'
        '  "nodes": [\n'
        '    {"id": "entity1", "type": "organization", "name": "Entity Name"}\n'
        '  ],\n'
        '  "edges": [\n'
        '    {"source": "entity1", "target": "entity2", "type": "RELATIONSHIP_TYPE"}\n'
        '  ]\n'
        '}\n\n'
        f"Text: '{summary}'\n\n"
        "JSON:"
    )
    
    response = await call_ollama(prompt, temperature=0.1)
    
    if not response or not response.strip():
        print(f"LLM returned empty response for summary: {summary}")
        return {"nodes": [], "edges": []}
    
    try:
        # Use json-repair to fix and parse
        cleaned = repair_json(response.strip())
        data = json.loads(cleaned)
        # Normalize as before
        normalized_data = {"nodes": [], "edges": []}
        if "nodes" in data:
            normalized_data["nodes"] = data["nodes"]
        if "edges" in data:
            normalized_data["edges"] = data["edges"] if isinstance(data["edges"], list) else [data["edges"]]
        elif "edge" in data:
            normalized_data["edges"] = data["edge"] if isinstance(data["edge"], list) else [data["edge"]]
        return normalized_data
    except Exception as e:
        print(f"JSON extraction failed: {e}")
        print(f"Raw response: {response!r}")
        return {"nodes": [], "edges": []}


async def create_entity_nodes(nodes):
    """Create entity nodes in Neo4j from extracted nodes, labeled as Entity."""
    if not nodes:
        return
        
    for node in nodes:
        if not isinstance(node, dict):
            print(f"Skipping invalid node (not a dict): {node}")
            continue

        node_id = node.get("id", "").strip()
        node_name = node.get("name", "").strip()
        node_type = node.get("type", "entity")
        
        if not node_id or not node_name:
            print(f"Skipping node with missing id or name: {node}")
            continue

        try:
            async with driver.session() as session:
                await session.run(
                    "MERGE (e:Entity {id: $id, name: $name, type: $type})",
                    id=node_id,
                    name=node_name,
                    type=node_type
                )
        except Exception as e:
            print(f"Failed to create entity node {node_id}: {e}")


async def create_entity_relationships(edges):
    """Create relationships between entity nodes in Neo4j."""
    for edge in edges:
        if not edge.get("source") or not edge.get("target"):
            continue
        try:
            async with driver.session() as session:
                await session.run(
                    """
                    MATCH (e1:Entity {id: $source_id}), (e2:Entity {id: $target_id})
                    MERGE (e1)-[r:%s]->(e2)
                    """ % edge.get("type", "RELATED"),
                    source_id=edge["source"],
                    target_id=edge["target"]
                )
        except Exception as e:
            print(f"Failed to create relationship {edge}: {e}")


async def link_memory_to_entities(memory_id, nodes):
    """Link a memory node to all extracted entity nodes."""
    for node in nodes:
        if not node.get("id"):
            continue
        try:
            async with driver.session() as session:
                await session.run(
                    """
                    MATCH (m:Memory {id: $memory_id}), (e:Entity {id: $entity_id})
                    MERGE (m)-[:MENTIONS]->(e)
                    """,
                    memory_id=memory_id,
                    entity_id=node["id"]
                )
        except Exception as e:
            print(f"Failed to link memory {memory_id} to entity {node['id']}: {e}")



async def initialize_graph_db():
    """Call this once during application startup"""
    async with driver.session() as session:
        await session.run("CREATE INDEX memory_id_index IF NOT EXISTS FOR (m:Memory) ON (m.id)")
        await session.run("CREATE INDEX memory_confidence_index IF NOT EXISTS FOR (m:Memory) ON (m.confidence)")

async def find_related_memories(memory_id, max_hops=3, limit=50):
    # Safety checks
    if not isinstance(max_hops, int) or max_hops > 5:
        max_hops = 3
    if not isinstance(limit, int) or limit > 100:
        limit = 50
    query = f"""
    MATCH (start:Memory {{id: $memory_id}})
    MATCH (start)-[r*1..{max_hops}]-(related:Memory)
    WHERE related.id <> $memory_id
    RETURN DISTINCT related.id AS related_id, related.summary AS summary
    LIMIT {limit}
    """
    async with driver.session() as session:
        result = await session.run(query, memory_id=memory_id)
        related_memories = []
        async for record in result:
            related_memories.append((record["related_id"], record["summary"]))
        return related_memories



