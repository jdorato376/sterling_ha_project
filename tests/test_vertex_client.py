import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.vertex_integration.vertex_client import predict

def test_predict_stub():
    os.environ["VERTEX_ENDPOINT"] = "projects/x/locations/y/endpoints/z"
    assert isinstance(predict("hi"), str)
