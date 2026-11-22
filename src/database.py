import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "reviewease.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def now():
    return datetime.now(timezone.utc).isoformat()

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_code TEXT NOT NULL, condition TEXT NOT NULL,
            started_at TEXT NOT NULL, completed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
            event_type TEXT NOT NULL, event_data TEXT NOT NULL, occurred_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
            finding_id TEXT NOT NULL, decision TEXT NOT NULL, comment TEXT,
            created_at TEXT NOT NULL, UNIQUE(session_id, finding_id),
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        CREATE TABLE IF NOT EXISTS questionnaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL UNIQUE,
            responses TEXT NOT NULL, created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        """)

def create_session(participant_code, condition):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO sessions(participant_code, condition, started_at) VALUES (?, ?, ?)",
            (participant_code, condition, now()))
        return cur.lastrowid

def log_event(session_id, event_type, event_data):
    with connect() as conn:
        conn.execute(
            "INSERT INTO events(session_id, event_type, event_data, occurred_at) VALUES (?, ?, ?, ?)",
            (session_id, event_type, json.dumps(event_data), now()))

def save_decision(session_id, finding_id, decision, comment=""):
    with connect() as conn:
        conn.execute("""
            INSERT INTO decisions(session_id, finding_id, decision, comment, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(session_id, finding_id) DO UPDATE SET
            decision=excluded.decision, comment=excluded.comment, created_at=excluded.created_at
        """, (session_id, finding_id, decision, comment, now()))

def save_questionnaire(session_id, responses):
    with connect() as conn:
        conn.execute("INSERT OR REPLACE INTO questionnaires(session_id, responses, created_at) VALUES (?, ?, ?)",
                     (session_id, json.dumps(responses), now()))
        conn.execute("UPDATE sessions SET completed_at=? WHERE id=?", (now(), session_id))

def get_summary():
    with connect() as conn:
        rows = conn.execute("""
            SELECT s.id AS session_id, s.participant_code, s.condition, s.started_at, s.completed_at,
                   COUNT(DISTINCT d.finding_id) AS decisions, COUNT(DISTINCT e.id) AS interaction_events
            FROM sessions s LEFT JOIN decisions d ON d.session_id=s.id
            LEFT JOIN events e ON e.session_id=s.id GROUP BY s.id ORDER BY s.id DESC
        """).fetchall()
    return pd.DataFrame([dict(row) for row in rows])
