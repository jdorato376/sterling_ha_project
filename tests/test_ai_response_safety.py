import importlib.util
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('cognitive_router', os.path.join(os.path.dirname(__file__), '..', 'cognitive_router.py'))
cognitive_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cognitive_router)


def test_ai_response_safety(tmp_path, monkeypatch):
    mem = tmp_path / 'runtime_memory.json'
    mem.write_text('{}')
    monkeypatch.setattr(cognitive_router.RUNTIME_STORE, 'path', mem)

    def malicious(query: str):
        return {'agent': 'general', 'response': '<script>alert(1)</script>', 'confidence': 0.9}

    monkeypatch.setattr(cognitive_router, 'general_agent', malicious)
    cognitive_router.HANDLERS['general'] = malicious

    res = cognitive_router.handle_request('hello world')
    assert '<' not in res['response']
