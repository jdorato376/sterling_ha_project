from modules.adaptive_router.router import route

def test_route_basic():
    assert isinstance(route("hello", {}), str)
