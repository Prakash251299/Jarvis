import aiosqlite
from datetime import datetime, timezone

async def create_tables(conn: aiosqlite.Connection):
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        model_used TEXT NOT NULL,
        is_archived INTEGER DEFAULT 0
    );
    """)

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role TEXT CHECK(role IN ('user', 'assistant', 'system')) NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        tokens_used INTEGER,
        audio_path TEXT,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
    );
    """)

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS memory_entries (
        id TEXT PRIMARY KEY,
        conversation_id TEXT,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        created_at TEXT NOT NULL,
        relevance_score REAL DEFAULT 1.0,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
    );
    """)

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    await conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(timestamp);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_conv ON memory_entries(conversation_id);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_key ON memory_entries(key);")

    now = datetime.now(timezone.utc).isoformat()
    default_settings = [
        ("model", "qwen3:8b", now),
        ("whisper_model", "base", now),
        ("piper_voice", "en_US-lessac-medium", now),
        ("voice_output_enabled", "true", now),
        ("memory_enabled", "true", now)
    ]
    for key, val, updated_at in default_settings:
        await conn.execute(
            "INSERT OR IGNORE INTO settings (key, value, updated_at) VALUES (?, ?, ?);",
            (key, val, updated_at)
        )

    await conn.commit()
