from ethics import EthicsEngine


def test_evaluate_selects_best_agent(tmp_path, monkeypatch):
    const_file = tmp_path / "constitution.yaml"
    const_file.write_text(
        "hierarchy:\n  agent_a: 100\n  agent_b: 50\n"
    )
    ledger_file = tmp_path / "ledger.json"
    engine = EthicsEngine()
    monkeypatch.setattr(engine, "constitution", {"hierarchy": {"agent_a": 100, "agent_b": 50}})
    monkeypatch.setattr(engine, "precedent", {})
    result = engine.evaluate(
        "cmd",
        {"agent_a": "do", "agent_b": "do"},
        {"agent_a": 0.8, "agent_b": 0.9},
        "low",
    )
    assert result["approved_agent"] == "agent_a"
