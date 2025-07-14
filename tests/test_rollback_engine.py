import importlib.util
import os

spec = importlib.util.spec_from_file_location('threads.rollback_engine', os.path.join(os.path.dirname(__file__), '..', 'threads', 'rollback_engine.py'))
rollback_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rollback_engine)


def test_rollback_thread():
    result = rollback_engine.rollback_thread('test')
    assert result == {'thread': 'test', 'status': 'reverted'}
