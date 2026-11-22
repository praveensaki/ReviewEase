
import json
import pandas as pd

from src.database import connect


def load_analytics():
    """Load research data without modifying the original database."""

    with connect() as conn:
        sessions = pd.read_sql_query(
            """
            SELECT id AS session_id,
                   participant_code,
                   condition,
                   started_at,
                   completed_at
            FROM sessions
            ORDER BY id
            """,
            conn
        )

        decisions = pd.read_sql_query(
            """
            SELECT session_id, finding_id, decision, comment
            FROM decisions
            ORDER BY session_id, finding_id
            """,
            conn
        )

        questionnaires = pd.read_sql_query(
            """
            SELECT session_id, responses
            FROM questionnaires
            """,
            conn
        )

        events = pd.read_sql_query(
            """
            SELECT session_id, event_type, occurred_at
            FROM events
            ORDER BY occurred_at
            """,
            conn
        )

    # Calculate session duration in minutes.
    if not sessions.empty:
        sessions["started_at"] = pd.to_datetime(
            sessions["started_at"], utc=True, errors="coerce"
        )
        sessions["completed_at"] = pd.to_datetime(
            sessions["completed_at"], utc=True, errors="coerce"
        )

        sessions["duration_minutes"] = (
            sessions["completed_at"] - sessions["started_at"]
        ).dt.total_seconds() / 60

    # Expand questionnaire JSON into separate columns.
    if not questionnaires.empty:
        questionnaires["responses"] = questionnaires["responses"].apply(
            lambda value: json.loads(value) if isinstance(value, str) else {}
        )

        response_data = pd.json_normalize(questionnaires["responses"])
        questionnaires = pd.concat(
            [
                questionnaires[["session_id"]].reset_index(drop=True),
                response_data.reset_index(drop=True)
            ],
            axis=1
        )

        questionnaires = questionnaires.rename(columns={
            "mental_demand": "Mental demand",
            "effort": "Effort",
            "frustration": "Frustration",
            "trust": "Trust",
            "clarity": "Clarity"
        })

    return sessions, decisions, questionnaires, events
