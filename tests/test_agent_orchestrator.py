import os
import sys
import importlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

agent_orchestrator = importlib.import_module('addons.sterling_os.agent_orchestrator')
import types


def test_arbitrate_override():
    responses = {'core': 'c', 'gemini': 'g'}
    trust = {'core': 0.5, 'gemini': 0.9}
    result = agent_orchestrator.arbitrate(responses, trust, override='core')
    assert result == 'c'


def test_handle_query_vote(monkeypatch):
    monkeypatch.setitem(sys.modules, 'addons', types.ModuleType('addons'))
    monkeypatch.setitem(sys.modules, 'addons.sterling_os', types.ModuleType('addons.sterling_os'))
    monkeypatch.setitem(sys.modules, 'addons.sterling_os.memory_manager', types.ModuleType('addons.sterling_os.memory_manager'))
    monkeypatch.setattr(agent_orchestrator.memory_manager, 'add_event', lambda e: None, raising=False)
    monkeypatch.setattr(agent_orchestrator, '_gemini_response', lambda q: 'g')
    monkeypatch.setattr(agent_orchestrator, '_local_llm_response', lambda q: 'c')
    trust = {'core': 0.5, 'gemini': 0.9}
    result = agent_orchestrator.handle_query_vote('hi', trust)
    assert result['agent_used'] == 'gemini'
    assert result['response'] == 'g'
