from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import uuid

# Connect to Qdrant running locally
client = QdrantClient("http://localhost:6333")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Ensure collection exists
if not client.collection_exists("memos"):
    client.create_collection(
        collection_name="memos",
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )

def write_memory(memory):
    # Convert the memory summary to an embedding vector
    vector = model.encode(memory["summary"]).tolist()
    # Upsert (insert/update) the memory into Qdrant
    client.upsert(
        collection_name="memos",
        points=[{
            "id": str(uuid.uuid4()),
            "vector": vector,
            "payload": memory
        }]
    )
