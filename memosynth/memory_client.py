import os

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

def query_memory(prompt, top_k=3):
    # Convert the prompt to an embedding vector
    vector = model.encode(prompt).tolist()
    # Search Qdrant for similar vectors
    result = client.search(
        collection_name="memos",
        query_vector=vector,
        limit=top_k
    )
    # Return the payloads (original memory dictionaries)
    return [r.payload for r in result]


#LLM Import
import requests

def call_ollama(prompt, model="tinyllama"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False  # Force single JSON response
        }
    )
    return response.json()["response"]


def summarize_memories(memories):
    prompt = "Summarize these insights:\n" + "\n".join([m["summary"] for m in memories])
    return call_ollama(prompt)

def diff(mem1, mem2):
    if mem1["summary"] != mem2["summary"]:
        return f"⚠️ Difference in summaries:\n1: {mem1['summary']}\n2: {mem2['summary']}"
    return "✅ No differences"

def resolve(mem1, mem2):
    prompt = (
        "Resolve any contradiction between these two insights and provide a single, reconciled summary:\n"
        f"1: {mem1['summary']}\n"
        f"2: {mem2['summary']}"
    )
    return call_ollama(prompt)
