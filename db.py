import os
import sqlite3
import uuid
from datetime import datetime, date

from crypto import encrypt_phone, decrypt_phone, hash_phone

IDENTITY_DB = os.environ.get("IDENTITY_DB_PATH", "data/identity.db")
HEALTH_DB = os.environ.get("HEALTH_DB_PATH", "data/health.db")


def _connect(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_databases():
    with _connect(IDENTITY_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id TEXT PRIMARY KEY,
                phone_hash TEXT UNIQUE NOT NULL,
                phone_encrypted TEXT NOT NULL,
                signup_date TEXT NOT NULL,
                uv_exposure INTEGER NOT NULL DEFAULT 0,
                uv_hours_per_week REAL,
                zip_code TEXT,
                household_size INTEGER,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_state (
                phone_hash TEXT PRIMARY KEY,
                state TEXT NOT NULL DEFAULT 'IDLE',
                participant_id TEXT,
                context TEXT DEFAULT '{}',
                updated_at TEXT NOT NULL
            )
        """)

    with _connect(HEALTH_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id TEXT NOT NULL,
                week_start TEXT NOT NULL,
                sick INTEGER NOT NULL,
                severity INTEGER,
                symptoms TEXT,
                responded_at TEXT NOT NULL
            )
        """)


# --- Conversation state ---

def get_state(phone_number: str) -> dict:
    ph = hash_phone(phone_number)
    with _connect(IDENTITY_DB) as conn:
        row = conn.execute(
            "SELECT state, participant_id, context FROM conversation_state WHERE phone_hash = ?",
            (ph,)
        ).fetchone()
    if row:
        import json
        return {"state": row["state"], "participant_id": row["participant_id"],
                "context": json.loads(row["context"])}
    return {"state": "NEW", "participant_id": None, "context": {}}


def set_state(phone_number: str, state: str, participant_id: str = None, context: dict = None):
    import json
    ph = hash_phone(phone_number)
    now = datetime.utcnow().isoformat()
    ctx = json.dumps(context or {})
    with _connect(IDENTITY_DB) as conn:
        conn.execute("""
            INSERT INTO conversation_state (phone_hash, state, participant_id, context, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(phone_hash) DO UPDATE SET
                state = excluded.state,
                participant_id = COALESCE(excluded.participant_id, conversation_state.participant_id),
                context = excluded.context,
                updated_at = excluded.updated_at
        """, (ph, state, participant_id, ctx, now))


# --- Participants ---

def create_participant(phone_number: str, uv_exposure: bool, uv_hours: float = None,
                       zip_code: str = None, household_size: int = None) -> str:
    pid = str(uuid.uuid4())
    ph = hash_phone(phone_number)
    pe = encrypt_phone(phone_number)
    now = datetime.utcnow().isoformat()
    with _connect(IDENTITY_DB) as conn:
        conn.execute("""
            INSERT INTO participants (id, phone_hash, phone_encrypted, signup_date,
                                     uv_exposure, uv_hours_per_week, zip_code, household_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pid, ph, pe, now, int(uv_exposure), uv_hours, zip_code, household_size))
    return pid


def get_participant_by_phone(phone_number: str) -> dict | None:
    ph = hash_phone(phone_number)
    with _connect(IDENTITY_DB) as conn:
        row = conn.execute(
            "SELECT * FROM participants WHERE phone_hash = ?", (ph,)
        ).fetchone()
    return dict(row) if row else None


def get_all_active_participants() -> list[dict]:
    with _connect(IDENTITY_DB) as conn:
        rows = conn.execute(
            "SELECT id, phone_encrypted FROM participants WHERE active = 1"
        ).fetchall()
    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "phone_number": decrypt_phone(row["phone_encrypted"])
        })
    return results


# --- Health responses ---

def record_response(participant_id: str, sick: bool, severity: int = None,
                    symptoms: str = None):
    now = datetime.utcnow().isoformat()
    week_start = _current_week_start()
    with _connect(HEALTH_DB) as conn:
        conn.execute("""
            INSERT INTO responses (participant_id, week_start, sick, severity, symptoms, responded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (participant_id, week_start, int(sick), severity, symptoms, now))


def _current_week_start() -> str:
    today = date.today()
    monday = today - __import__("datetime").timedelta(days=today.weekday())
    return monday.isoformat()
