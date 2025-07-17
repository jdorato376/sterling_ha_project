from modules.vertex_integration.vertex_client import predict
import os

def test_predict_stub():
    os.environ["VERTEX_ENDPOINT"] = "projects/x/locations/y/endpoints/z"
    assert isinstance(predict("hi"), str)
