import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.adaptive_router.router import route

def test_route_basic():
    assert isinstance(route("hello", {}), str)
