import os
import duckdb
import asyncio
from datetime import datetime, timezone

# Connect to (or create) the DuckDB database file
con = duckdb.connect("memory_timeline.db")
db_lock = asyncio.Lock()  # Ensures thread safety for DuckDB writes

# Table Initialization

async def init_tables():
    async with db_lock:
        await asyncio.to_thread(
            con.execute,
            """
            CREATE TABLE IF NOT EXISTS memory_log (
                id TEXT PRIMARY KEY,
                summary TEXT,
                timestamp TEXT,
                version INT
            )
            """
        )
        await asyncio.to_thread(
            con.execute,
            """
            CREATE TABLE IF NOT EXISTS conflict_log (
                timestamp TEXT,
                conflict_type TEXT,
                new_memory_id TEXT,
                current_memory_id TEXT,
                new_summary TEXT,
                current_summary TEXT,
                new_version INT,
                current_version INT,
                new_confidence FLOAT,
                current_confidence FLOAT
            )
            """
        )

# Ensure tables are initialized on module load
asyncio.create_task(init_tables())

# Memory Logging 

async def log_memory(memory):
    """Log a memory to the timeline, skipping if already present."""
    async with db_lock:
        # Check if this id already exists
        exists = await asyncio.to_thread(
            lambda: con.execute(
                "SELECT 1 FROM memory_log WHERE id = ?",
                (memory["id"],)
            ).fetchone()
        )
        if exists:
            print(f"Memory {memory['id']} already exists!")
            return
        # Otherwise, insert the new memory
        await asyncio.to_thread(
            con.execute,
            "INSERT INTO memory_log VALUES (?, ?, ?, ?)",
            (memory["id"], memory["summary"], memory["created_at"], memory["version"])
        )

# Conflict Logging 

async def log_conflict(new_memory, current_memory, conflict_type="version"):
    """Log a version/conflict event to the conflict_log table."""
    async with db_lock:
        await asyncio.to_thread(
            con.execute,
            """
            INSERT INTO conflict_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                conflict_type,
                new_memory.get("id"),
                current_memory.get("id"),
                new_memory.get("summary"),
                current_memory.get("summary"),
                new_memory.get("version"),
                current_memory.get("version"),
                new_memory.get("confidence"),
                current_memory.get("confidence")
            )
        )
