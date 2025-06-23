import duckdb
import os

# Connect to (or create) the DuckDB database file
con = duckdb.connect("memory_timeline.db")

def init_timeline_table():
    con.execute("""
        CREATE TABLE IF NOT EXISTS memory_log (
            id TEXT,
            summary TEXT,
            timestamp TEXT,
            version INT
        )
    """)

def log_memory(memory):
    # Check if this id already exists
    existing = con.execute(
        "SELECT COUNT(*) FROM memory_log WHERE id = ?", (memory["id"],)
    ).fetchone()[0]
    if existing:
        print("This entry already exists!")
        return
    # Otherwise, insert the new memory
    con.execute(
        "INSERT INTO memory_log VALUES (?, ?, ?, ?)",
        (memory["id"], memory["summary"], memory["created_at"], memory["version"])
    )

# Initialize table when module loads
init_timeline_table()