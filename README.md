# MemoSynth-Lite

A Beginner-Friendly Project to Build an LLM Agent Memory System

---

## 📝 Project Overview

**MemoSynth-Lite** is a hands-on, beginner-friendly project that guides you through building a lightweight memory system for AI agents. The system enables an agent to store, retrieve, summarize, and relate "memories"—mimicking human-like recall and reasoning—using only free, open-source tools.

**Core Features:**
- Store memories with semantic embeddings in a vector database (Qdrant)
- Track source, and time for each memory
- Query, summarize, and compare memories using LLMs (TinyLlama via Ollama)
- Maintain a timeline of events (DuckDB)
- Relate memories in a simple graph (Neo4j)
- Interactive demonstration in Jupyter Notebook

---

## 📁 Project Structure

```
memosynth-lite/
├── memosynth/
│   ├── memory_client.py
│   ├── vector_store.py
│   ├── timeline_store.py
│   ├── graph_store.py
├── notebook/
│   └── demo.ipynb
├── config/
│   └── sample_memory.json
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. **Clone the Repository**
```
git clone https://github.com/rohit5khanna/memosynth-lite.git
cd memosynth-lite
```

### 2. **Set Up Python Environment**
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. **Start Required Services**
- **Qdrant (Vector DB):**
  ```
  docker run -p 6333:6333 qdrant/qdrant
  ```
- **DuckDB:** No server needed; used as a local file.
- **Neo4j (Graph DB):**
  ```
  docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/geophysicist neo4j
  ```
- **Ollama (LLM inference):**
  ```
  brew install ollama
  ollama serve
  ollama pull tinyllama
  ```

### 4. **Run the Interactive Demo**
```
jupyter notebook notebook/demo.ipynb
```
Follow the notebook cells to simulate memory storage, querying, summarization, diff, and resolution.

---

## 🧩 Key Components

- **`memory_client.py`**: Defines the memory schema and APIs for summarization, diff, and resolve.
- **`vector_store.py`**: Handles semantic storage and retrieval using Qdrant and sentence-transformers.
- **`timeline_store.py`**: Logs memory events and tracks them over time using DuckDB.
- **`graph_store.py`**: (Optional) Manages memory nodes and simple relationships in Neo4j.
- **`demo.ipynb`**: Walks through the full memory workflow interactively.

---

## 💡 Example Memory Object

```
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

---

## 🛠️ APIs & Usage

- **Write Memory:**  
  Store a memory in Qdrant and log in DuckDB.
- **Query Memory:**  
  Retrieve semantically similar memories using vector search.
- **Summarize Memories:**  
  Use TinyLlama (via Ollama) to generate concise summaries.
- **Diff & Resolve:**  
  Compare two memories and resolve contradictions using LLM.
- **Graph Relationships:**  
  Add basic links between memories in Neo4j for visualization.

---

## 🧠 Memory Workflow

1. **Environment Setup & State Reset:**  
   Prepare the environment, clear previous data from Qdrant and DuckDB.

2. **Define Memories:**  
   Specify three memory objects, each with rich metadata.

3. **Store Memories:**  
   Write each memory to the vector store and log to the timeline.

4. **Graph Memory :**  
   Create nodes and relationships in Neo4j for advanced memory linking.

5. **Visualize Timeline:**  
   Display all memories as a table using pandas.

6. **Query Memories:**  
   Retrieve relevant memories with semantic search.

7. **Summarize Memories:**  
   Generate a summary using an LLM.

8. **Compare & Resolve:**  
   Show differences and resolve contradictions between memories.

| Step                    | Code/Function(s) Used                   | Output/Goal                        |
|-------------------------|---------------------------------------- |------------------------------------|
| State reset             | `delete_collection`, `DELETE FROM`      | Fresh demo run                     |
| Define memories         | Python dicts                            | 3 memory objects                   |
| Store memories          | `write_memory`, `log_memory`            | Data in Qdrant, DuckDB             |
| Graph memory            | `create_memory_node`,`relate_memories`, | Nodes/edges in Neo4j,              |
                            `find_related_memories`                   multi-hop query
| Visualize timeline      | pandas DataFrame                        | Tabular timeline                   |
| Query                   | `query_memory`                          | Relevant memories                  |
| Summarize               | `summarize_memories`                    | LLM-generated summary              |
| Diff & resolve          | `diff`, `resolve`                       | Highlight & synthesize             |

---

## 📚 Dependencies

- Python 3.8+
- [sentence-transformers](https://www.sbert.net/)
- [qdrant-client](https://qdrant.tech/)
- [duckdb](https://duckdb.org/)
- [neo4j](https://neo4j.com/) (optional)
- [pandas](https://pandas.pydata.org/)
- [rich](https://rich.readthedocs.io/)
- [Ollama](https://ollama.com/) (for local LLM inference)

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a pull request.  
For suggestions or issues, open a GitHub issue or contact the maintainer.

---


## 🙋‍♂️ Contact

For questions or support, open an issue on GitHub or email [121rohit5khanna@gmail.com].

---


**Inspired by [MemoSynth-Lite](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/31230649/a1f62bc3-0e5d-49fa-bb20-d5b9849ef56b/Copy-of-MemoSynth-Lite.pdf) and the open-source agent memory community.**
```