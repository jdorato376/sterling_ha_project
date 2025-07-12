import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from addons.sterling_os import agent_senate, trust_registry


def test_weighted_vote(tmp_path, monkeypatch):
    file = tmp_path / "trust.json"
    monkeypatch.setattr(trust_registry, "TRUST_FILE", file)
    trust_registry.save_weights({"a": 1.0, "b": 0.5})
    senate = agent_senate.AgentSenate(["a", "b"])
    result = senate.vote_on_action([
        {"agent_id": "a", "confidence": 0.6, "response": "A"},
        {"agent_id": "b", "confidence": 0.9, "response": "B"},
    ])
    assert result["agent_id"] == "a"


def test_update_weight(tmp_path, monkeypatch):
    file = tmp_path / "trust.json"
    monkeypatch.setattr(trust_registry, "TRUST_FILE", file)
    trust_registry.save_weights({"a": 0.5})
    trust_registry.update_weight("a", 0.3)
    assert trust_registry.load_weights()["a"] == 0.8


def test_set_weight_clamps(tmp_path, monkeypatch):
    file = tmp_path / "trust.json"
    monkeypatch.setattr(trust_registry, "TRUST_FILE", file)
    trust_registry.set_weight("a", 1.5)
    assert trust_registry.load_weights()["a"] == 1.0


def test_set_weight_clamps_negative(tmp_path, monkeypatch):
    file = tmp_path / "trust.json"
    monkeypatch.setattr(trust_registry, "TRUST_FILE", file)
    trust_registry.set_weight("a", -0.3)
    assert trust_registry.load_weights()["a"] == 0.0


def test_set_weight_str_input(tmp_path, monkeypatch):
    file = tmp_path / "trust.json"
    monkeypatch.setattr(trust_registry, "TRUST_FILE", file)
    trust_registry.set_weight("a", "0.4")
    assert trust_registry.load_weights()["a"] == 0.4


def test_persistent_registry(tmp_path, monkeypatch):
    trust_file = tmp_path / "trust.json"
    store_file = tmp_path / "store.json"
    monkeypatch.setattr(trust_registry, "TRUST_FILE", trust_file)
    monkeypatch.setattr(trust_registry, "TRUST_REGISTRY_FILE", store_file)
    trust_registry.trust_registry = {}
    trust_registry.save_weights({"a": 0.3})
    trust_registry.load_trust_registry(store_file)
    assert trust_registry.trust_registry["a"] == 0.3
    trust_registry.update_weight("a", 0.4)
    trust_registry.trust_registry = {}
    trust_registry.load_trust_registry(store_file)
    assert trust_registry.trust_registry["a"] == 0.7
