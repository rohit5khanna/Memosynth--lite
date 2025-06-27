from qdrant_client import AsyncQdrantClient, models
from sentence_transformers import SentenceTransformer
from datetime import datetime, timezone
import uuid
from memosynth.graph_store import extract_entities_and_relationships, create_entity_nodes, create_entity_relationships, link_memory_to_entities
import asyncio


# Connect to Qdrant running locally
client = AsyncQdrantClient("http://localhost:6333")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Ensure collection exists
async def initialize():
    """Async collection setup"""
    if not await client.collection_exists("memos"):
        await client.create_collection(
            collection_name="memos",
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
        )



async def write_memory(memory):
    """Write memory to Qdrant with proper UUID point ID"""
    print(f"📝 Writing memory: {memory['id']}")
    
    # Generate or get UUID for Qdrant point ID
    qdrant_id = memory.get("qdrant_id")
    if not qdrant_id:
        qdrant_id = str(uuid.uuid4())
        memory["qdrant_id"] = qdrant_id  # Store mapping for future reference
    
    # Create embedding vector
    vector = await asyncio.to_thread(model.encode, memory["summary"])
    vector = vector.tolist()
    
    # Update metadata
    memory["last_accessed"] = datetime.now(timezone.utc).isoformat()
    
    # Upsert to Qdrant with UUID point ID
    try:
        await client.upsert(
            collection_name="memos",
            points=[{
                "id": qdrant_id,           # ✅ Valid UUID string
                "vector": vector,
                "payload": memory          # ✅ Contains your "id": "m-001"
            }]
        )
        print(f"✅ Memory {memory['id']} successfully written to Qdrant")
    except Exception as e:
        print(f"❌ Failed to write memory {memory['id']} to Qdrant: {e}")
        raise
    
    # Extract entities and relationships from summary
    extraction = await extract_entities_and_relationships(memory["summary"])
    nodes = extraction.get("nodes", [])
    edges = extraction.get("edges", [])

    # Process graph operations using new functions
    await create_entity_nodes(nodes)                          # Add entity nodes to Neo4j
    await create_entity_relationships(edges)                  # Add relationships to Neo4j
    await link_memory_to_entities(memory["id"], nodes)        # Relate this memory to each extracted entity



async def get_memory_by_id(memory_id):
    # Try normal key
    result = await client.scroll(
        collection_name="memos",
        scroll_filter={"must": [{"key": "id", "match": {"value": memory_id}}]},
        limit=1
    )
    if result and result[0]:
        return result[0][0].payload

    # Try with metadata prefix
    result_meta = await client.scroll(
        collection_name="memos",
        scroll_filter={"must": [{"key": "metadata.id", "match": {"value": memory_id}}]},
        limit=1
    )
    if result_meta and result_meta[0]:
        return result_meta[0][0].payload

    return None

