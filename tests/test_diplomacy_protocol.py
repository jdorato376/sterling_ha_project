import importlib.util
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location('addons.sterling_os.diplomacy_protocol', os.path.join(os.path.dirname(__file__), '..', 'addons', 'sterling_os', 'diplomacy_protocol.py'))
diplomacy_protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diplomacy_protocol)


def test_mediate_tie():
    votes = {'a': True, 'b': False}
    trust = {'a': 0.5, 'b': 0.5}
    assert diplomacy_protocol.mediate(votes, trust) is None


def test_propose_rebalance():
    votes = {'a': True, 'b': False}
    trust = {'a': 0.5, 'b': 0.5}
    result = diplomacy_protocol.propose_rebalance(votes, trust)
    assert result['a'] > trust['a']
    assert result['b'] < trust['b']
