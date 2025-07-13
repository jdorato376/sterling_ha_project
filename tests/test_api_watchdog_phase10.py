import os
import sys
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location(
    'api_watchdog',
    os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'api_watchdog.py')
)
api_watchdog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_watchdog)


def test_watchdog_disable():
    for _ in range(3):
        api_watchdog.record_call('x', 2.5, success=False)
    assert api_watchdog.is_disabled('x') is True
