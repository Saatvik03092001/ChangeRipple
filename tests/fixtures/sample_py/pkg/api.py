from .service import double

def endpoint(value: int) -> int:
    return double(value)
