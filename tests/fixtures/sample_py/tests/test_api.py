from pkg.api import endpoint

def test_endpoint():
    assert endpoint(2) == 4
