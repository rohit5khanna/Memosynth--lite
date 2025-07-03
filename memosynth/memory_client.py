import os
import asyncio

from memosynth.vector_store import write_memory, model
from memosynth.timeline_store import log_memory, log_conflict
from memosynth.graph_store import create_memory_node
from memosynth.utility import cosine_similarity, call_ollama

# Create the config directory if it doesn't exist
os.makedirs('config', exist_ok=True)

example_memory = {
"id": "m-001",
"project": "demo_project",
"agent": "doc_bot",
"summary": "Client asked about margin drop in Q2.",
"type": "insight",
"tags": ["finance", "Q2", "risk"],
"source": "Earnings_Report_Q2.pdf",
"author": "doc_bot",
"created_at": "2025-06-19",
"version": 1,
"confidence": 0.9,
"visibility": "project",
"sensitivity": "medium"
}


import json

with open("config/sample_memory.json", "w") as f:
	json.dump(example_memory, f, indent=2)

from memosynth.vector_store import client, model
from datetime import datetime, timezone

# Set last_accessed
example_memory["last_accessed"] = datetime.now(timezone.utc).isoformat()

async def query_memory(prompt, top_k=3, recency_weight=0.3, confidence_weight=0.1):
    # Step 1: Get more candidates for re-ranking
    vector = await asyncio.to_thread(model.encode, prompt)
    vector = vector.tolist()
    
    # Async search
    candidates = await client.search(
        collection_name="memos",
        query_vector=vector,
        limit=top_k * 3                         #Fetch more for re-ranking
    )

    now = datetime.now(timezone.utc)
    scored_memories = []

    for mem in candidates:
        payload = mem.payload
        # Recency score: more recent = higher score
        last_accessed = datetime.fromisoformat(payload.get("last_accessed", payload.get("created_at")))
        days_old = (now - last_accessed).days if last_accessed else 0
        recency_score = 1 / (1 + days_old)  # Recent = close to 1, old = close to 0

        # Use confidence as importance
        confidence = payload.get("confidence", 0.5)

        # Combine scores (60% similarity, 30% recency, 10% confidence)
        combined_score = (
            mem.score * (1 - recency_weight - confidence_weight) +
            recency_score * recency_weight +
            confidence * confidence_weight
        )

        scored_memories.append((payload, combined_score))

    # Step 2: Sort and return top_k
    scored_memories.sort(key=lambda x: x[1], reverse=True)
    results = [mem[0] for mem in scored_memories[:top_k]]
    await log_query(prompt, top_k, [m["id"] for m in results])
    return results


async def write_and_sync_memory(memory):
    try:
        await asyncio.gather(
        write_memory(memory),                           #Write to vector DB (Qdrant)
        log_memory(memory),                             #Log to timeline (DuckDB)
        create_memory_node(memory)                      #Add/update node in graph (Neo4j)
    )
        print(f"Memory {memory['id']} written and synced across all stores.")
    except Exception as e:
        print(f"Error syncing memory: {e}")


async def summarize_memories(memories, temperature=0.25):
    prompt = (
    "Summarize the following points in a single, concise paragraph. "
    "Do NOT mention that you are an AI assistant. "
    "Do NOT include any preamble, explanation, or reference to your own role. No mention of this prompt. "
    "Only output the direct answer:\n"
    + "\n".join([m["summary"] for m in memories])
    )
    summary = await call_ollama(prompt, temperature=temperature)
    await log_summary([m["id"] for m in memories], prompt, summary)
    return summary



async def diff(mem1, mem2, model_param=None):
    # Encode summaries to vectors
    # Run blocking operations in threads
    vec1, vec2 = await asyncio.gather(
        asyncio.to_thread(model.encode, mem1['summary']),
        asyncio.to_thread(model.encode, mem2['summary'])
    )
    
    # Calculate cosine similarity
    similarity = cosine_similarity(vec1, vec2)
    
    # Threshold: A score of 0.98 and above will be treated as similar
    if similarity < 0.98:
        return f"⚠️ Difference in summaries (cosine similarity: {similarity:.3f}):\n1: {mem1['summary']}\n2: {mem2['summary']}"
    else:
        return "✅ No significant differences"


async def resolve(mem1, mem2):
    prompt = (
        "Resolve any contradiction between these two insights and provide a single, reconciled summary in a professional way."
        "Do NOT mention that you are an AI assistant. "
        "Do NOT include any preamble, explanation, or reference to your own role. No mention of this prompt. "
        "Only output the direct answer:\n"
        f"1: {mem1['summary']}\n"
        f"2: {mem2['summary']}"
    )
    return await call_ollama(prompt)


from memosynth.vector_store import get_memory_by_id, write_memory

async def update_memory(new_memory):
    # Step 1: Get the latest memory from the DB
    current = await get_memory_by_id(new_memory["id"])
    if current is None:
        print("Memory not found. Creating new.")
        new_memory["version"] = 1
        await write_memory(new_memory)
        return

    # Step 2: Compare versions
    if new_memory["version"] == current["version"]:
        # No conflict: safe to update
        new_memory["version"] += 1
        await write_memory(new_memory)
        print("Memory updated successfully.")
    else:
        # Conflict detected!
        print("Version conflict detected!")
        print(f"Current version: {current['version']}, Your version: {new_memory['version']}")
        # Log the conflict
        await log_conflict(new_memory, current, conflict_type="version")
        
