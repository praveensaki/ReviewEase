def test_database_workflow(tmp_path, monkeypatch):
    import src.database as db
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    sid = db.create_session("P001", "Progressive disclosure")
    db.log_event(sid, "review_started", {})
    db.save_decision(sid, "F-001", "Accept finding")
    db.save_questionnaire(sid, {"mental_demand": 4})
    summary = db.get_summary()
    assert len(summary) == 1
    assert summary.iloc[0]["participant_code"] == "P001"
    assert summary.iloc[0]["decisions"] == 1
