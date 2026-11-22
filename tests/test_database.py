
import json

import pytest

import src.database as db
from src.analytics import load_analytics


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    return db


def test_create_session(test_db):
    session_id = test_db.create_session(
        "P001", "Conventional review"
    )

    summary = test_db.get_summary()

    assert len(summary) == 1
    assert summary.iloc[0]["session_id"] == session_id
    assert summary.iloc[0]["participant_code"] == "P001"
    assert summary.iloc[0]["condition"] == "Conventional review"


def test_log_event(test_db):
    session_id = test_db.create_session(
        "P002", "Progressive disclosure"
    )

    test_db.log_event(
        session_id,
        "finding_expanded",
        {"finding_id": "F-001"}
    )

    with test_db.connect() as conn:
        event = conn.execute(
            "SELECT * FROM events WHERE session_id = ?",
            (session_id,)
        ).fetchone()

    assert event["event_type"] == "finding_expanded"
    assert json.loads(event["event_data"]) == {
        "finding_id": "F-001"
    }


def test_save_decision_and_update_existing_decision(test_db):
    session_id = test_db.create_session(
        "P003", "Conventional review"
    )

    test_db.save_decision(
        session_id, "F-001", "Accept finding", "Valid issue"
    )

    test_db.save_decision(
        session_id, "F-001", "Reject finding", "Not relevant"
    )

    with test_db.connect() as conn:
        decisions = conn.execute(
            "SELECT * FROM decisions WHERE session_id = ?",
            (session_id,)
        ).fetchall()

    assert len(decisions) == 1
    assert decisions[0]["decision"] == "Reject finding"
    assert decisions[0]["comment"] == "Not relevant"


def test_questionnaire_submission(test_db):
    session_id = test_db.create_session(
        "P004", "Progressive disclosure"
    )

    responses = {
        "mental_demand": 4,
        "effort": 3,
        "trust": 5
    }

    test_db.save_questionnaire(session_id, responses)

    with test_db.connect() as conn:
        questionnaire = conn.execute(
            "SELECT * FROM questionnaires WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        session = conn.execute(
            "SELECT completed_at FROM sessions WHERE id = ?",
            (session_id,)
        ).fetchone()

    assert json.loads(questionnaire["responses"]) == responses
    assert session["completed_at"] is not None


def test_summary_counts_decisions_and_events(test_db):
    session_id = test_db.create_session(
        "P005", "Progressive disclosure"
    )

    test_db.save_decision(session_id, "F-001", "Accept finding")
    test_db.save_decision(session_id, "F-002", "Unsure")

    test_db.log_event(session_id, "review_started", {})
    test_db.log_event(
        session_id, "finding_expanded", {"finding_id": "F-001"}
    )

    summary = test_db.get_summary()

    assert summary.iloc[0]["decisions"] == 2
    assert summary.iloc[0]["interaction_events"] == 2


def test_analytics_loading(test_db):
    session_id = test_db.create_session(
        "P006", "Conventional review"
    )

    test_db.save_decision(
        session_id, "F-001", "Accept finding"
    )

    test_db.save_questionnaire(
        session_id,
        {
            "mental_demand": 3,
            "effort": 4,
            "frustration": 2,
            "trust": 5,
            "clarity": 4
        }
    )

    test_db.log_event(session_id, "review_started", {})

    sessions, decisions, questionnaires, events = load_analytics()

    assert len(sessions) == 1
    assert len(decisions) == 1
    assert len(questionnaires) == 1
    assert len(events) == 1

    assert questionnaires.iloc[0]["Mental demand"] == 3
    assert questionnaires.iloc[0]["Trust"] == 5
    assert sessions.iloc[0]["completed_at"] is not None
