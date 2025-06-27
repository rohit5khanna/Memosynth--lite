# 🧠 MemoSynth-Lite

> **A modular, open-source memory system for LLM agents — enabling storage, retrieval, summarization, and reasoning over "memories" using only free, local tools.**

## 🚀 Overview

MemoSynth-Lite lets an AI agent remember, retrieve, relate, and summarize information over time—just like a human memory.  
It combines semantic search, timeline tracking, and graph-based reasoning to emulate rich, contextual memory for LLM-powered agents.

- **Store** memories with metadata (source, time, tags)
- **Search** semantically (not just keywords)
- **Track** memory evolution and conflicts
- **Summarize** and **resolve** using LLMs
- **All local, all free:** Qdrant, DuckDB, Neo4j, and Ollama

## 🗂️ Project Structure

```plaintext
/
├── config/                # Config files & sample data
├── memosynth/             # Core library code
│   ├── __init__.py
│   ├── graph_store.py     # Neo4j graph memory integration
│   ├── memory_client.py   # High-level async memory APIs
│   ├── timeline_store.py  # DuckDB timeline (temporal) storage
│   ├── utility.py         # Helper functions (e.g., cosine similarity)
│   └── vector_store.py    # Qdrant vector DB integration
├── notebook/              # Jupyter notebooks (e.g., demo.ipynb)
├── test/                  # Test scripts
├── venv/                  # Python virtual environment
├── README.md              # This file
└── requirements.txt       # Python dependencies
```
![File structure screenshot](https://pplx-res.cloudinary.com/image/private/user_uploads/31230649/a3fb9239-eedf-4458-ab26-704c7c597040/Screenshot-2025-06-25-at-9. module screenshot](https://pplx-res.cloudinary.com/image/private/user_uploads/31230649/11de4f03-be94-4ac7-bf8e-43045de4ffc4/Screenshot-2025-06-25-at-9.36.33-PM Core Components

| Module                | Purpose                                                      |
|-----------------------|-------------------------------------------------------------|
| `vector_store.py`     | Store/retrieve memories as embeddings in Qdrant (semantic)   |
| `timeline_store.py`   | Log memory events and conflicts in DuckDB (temporal)         |
| `graph_store.py`      | Model relationships/entities in Neo4j (relational/graph)     |
| `memory_client.py`    | High-level async APIs for all memory operations              |
| `utility.py`          | Helper functions (e.g., cosine similarity)                   |

## 🔗 APIs

### High-Level Async APIs (`memory_client.py`)

| Function | Description | Example Usage |
|----------|-------------|--------------|
| `write_and_sync_memory(memory)` | Store memory in vector DB, log to timeline, update graph | `await write_and_sync_memory(memory)` |
| `query_memory(prompt, top_k=3, recency_weight=0.3, confidence_weight=0.1)` | Semantic search with recency/confidence re-ranking | `await query_memory("What are Q2 risks?")` |
| `summarize_memories(memories)` | LLM-powered summary of multiple memories | `await summarize_memories([mem1, mem2])` |
| `diff(mem1, mem2, model)` | Vector-based difference detection | `await diff(mem1, mem2, model)` |
| `resolve(mem1, mem2)` | LLM-powered conflict resolution | `await resolve(mem1, mem2)` |
| `update_memory(new_memory)` | Handles versioning and conflict logging | `await update_memory(new_memory)` |

### Supporting APIs

- **Vector Store (`vector_store.py`):** `write_memory`, `get_memory_by_id`
- **Timeline Store (`timeline_store.py`):** `log_memory`, `log_conflict`
- **Graph Store (`graph_store.py`):** `create_memory_node`, `relate_memories`, `find_related_memories`, `extract_entities_and_relationships`, `link_memory_to_entities`
- **Utility (`utility.py`):** `cosine_similarity`

## 🧬 Memory Workflow

1. **Write a Memory**
   - Memory is stored as an embedding in Qdrant (vector DB).
   - Metadata (e.g., time, author, tags) is saved alongside.
   - Timeline entry is created in DuckDB.
   - Memory node and extracted entities are added to Neo4j graph DB.

2. **Query Memories**
   - User prompt is embedded and searched semantically in Qdrant.
   - Results are re-ranked by recency and confidence.
   - Top results are returned.

3. **Summarize Memories**
   - Multiple memories are summarized using a local LLM (Ollama).

4. **Diff and Resolve**
   - Differences between memory summaries are detected using vector similarity.
   - Contradictions/conflicts are resolved with LLM synthesis.
   - Version conflicts are logged in DuckDB.

5. **Graph Reasoning**
   - Entity and relationship extraction from memory summaries.
   - Graph traversal to find related memories.

## 📝 Memory Schema

A "memory" is a structured Python dict with rich metadata:

```python
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
```

## ⚙️ Installation & Setup

### 1. Clone the Repo

```bash
git clone 
cd memosynth-lite
```

### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Required Services

- **Qdrant (Vector DB):**
  ```bash
  docker run -p 6333:6333 qdrant/qdrant
  ```
- **Neo4j (Graph DB):**
  ```bash
  docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/ neo4j
  ```
- **Ollama (LLM Server):**
  - [Install Ollama](https://ollama.com/) and run locally.
- **DuckDB:** No server needed; runs as a file.

## 🧪 Usage & Demo

> **💡 Add code blocks and screenshots here to show each feature in action!**
>
> _Below are placeholders—replace or expand with your actual demo outputs and images._

### 1. **Store & Sync Memories**

```python
import asyncio
from memosynth.memory_client import write_and_sync_memory, example_memory

memory2 = {...}  # Define as per schema
memory3 = {...}

async def main():
    await write_and_sync_memory(example_memory)
    await write_and_sync_memory(memory2)
    await write_and_sync_memory(memory3)

asyncio.run(main())
```
> _🖼️ You can add a screenshot of a successful run or log output here._

### 2. **Query Memories**

```python
from memosynth.memory_client import query_memory

results = asyncio.run(query_memory("What are Q2 risks?"))
for mem in results:
    print(mem["summary"], mem["confidence"], mem["last_accessed"])
```
> _📸 Suggestion: Add a screenshot of query results or paste a sample output block here._

### 3. **Summarize Memories**

```python
from memosynth.memory_client import summarize_memories

all_memories = [example_memory, memory2, memory3]
summary = asyncio.run(summarize_memories(all_memories))
print(summary)
```
> _📝 Add a sample summary output or image here!_

### 4. **Compare & Resolve Differences**

```python
from memosynth.memory_client import diff, resolve

print(asyncio.run(diff(example_memory, memory2, model=None)))
print(asyncio.run(resolve(example_memory, memory2)))
```
> _⚡ Show a sample diff and resolution output here._

### 5. **Timeline Visualization**

```python
import duckdb
import pandas as pd

con = duckdb.connect('memory_timeline.db')
df_timeline = con.execute("SELECT * FROM memory_log ORDER BY timestamp DESC").fetchdf()
print(df_timeline)
```
> _📊 Suggestion: Add a screenshot of the timeline DataFrame or a table here._

### 6. **Graph Memory & Relationships**

```python
from memosynth.graph_store import relate_memories, find_related_memories

asyncio.run(relate_memories(memory1["id"], memory2["id"], rel_type="RELATED_TO"))
related = asyncio.run(find_related_memories("m-001", max_hops=2))
for rid, summary in related:
    print(f"{rid}: {summary}")
```
> _🕸️ Add a graph diagram or output block showing related memories!_

### 7. **Edge Cases & Conflict Logging**

- Version conflicts are logged automatically.
- Empty/malformed input is handled gracefully (see code comments).

> _🛠️ Add a code example and output for a version conflict or error case here._

## 🛠️ Technologies Used

| Tool         | Purpose                        |
|--------------|-------------------------------|
| Qdrant       | Vector DB (semantic search)    |
| DuckDB       | Timeline/log (temporal)        |
| Neo4j        | Graph DB (relationships)       |
| Ollama       | Local LLM server (summaries)   |
| SentenceTransformers | Embedding model        |
| Python Async | Non-blocking, scalable APIs    |

## 🧑‍💻 Contributing

- Fork, branch, and PR as usual.
- Write tests in `/test`.
- Keep new APIs async.
- Help expand the demo notebook!



> **✏️ _TODO: Add more demo outputs, screenshots, and diagrams for each feature above!_**  
> _Replace placeholders with your real results for maximum clarity and impact._  
> _You can also add a project logo or architecture diagram at the top!_

*Made for robust, local-first AI memory systems.*
