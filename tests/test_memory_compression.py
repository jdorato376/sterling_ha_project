import importlib.util
import os

MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', 'concord', 'strategic_memory_compression.py')

spec = importlib.util.spec_from_file_location('concord.memory', MODULE_PATH)
memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory)


def test_compress_logs():
    result = memory.compress_logs(['start', 'middle', 'end'])
    assert result.startswith('start') and result.endswith('end')
