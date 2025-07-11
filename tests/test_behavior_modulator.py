import pytest
from behavior_modulator import adjust_behavior_based_on_diff


def test_behavior_when_app_modified():
    diff_data = {"modified": ["app.py"]}
    behavior = adjust_behavior_based_on_diff(diff_data)
    assert behavior["monitor_frequency_sec"] == 10


def test_behavior_when_tests_modified():
    diff_data = {"modified": ["tests/test_foo.py"]}
    behavior = adjust_behavior_based_on_diff(diff_data)
    assert behavior["test_layer"] is True


def test_behavior_when_uptime_modified():
    diff_data = {"modified": ["uptime_tracker.py"]}
    behavior = adjust_behavior_based_on_diff(diff_data)
    assert behavior["log_heartbeat"] is True
