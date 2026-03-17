from hashlib import md5
from base64 import b64encode
from time import time
from typing import Any


def make_sign(method: str, time: str) -> str:
    n = f"method={method}&ak=e9dd5b4322f9f7d83d009de9bfa100c3&sk=2e3da06ae26ba9f76a5d8d355746f2fe&time={time}"
    b64 = b64encode(n.encode())
    return md5(b64).hexdigest()


def make_header(
    method: str = "GET", header: dict[str, Any] | None = None
) -> dict[str, Any]:
    if header is None:
        header = {}
    new_header = header.copy()
    t = int(time() * 1000)
    n = f"method={method}&ak=e9dd5b4322f9f7d83d009de9bfa100c3&sk=2e3da06ae26ba9f76a5d8d355746f2fe&time={t}"
    new_header["X-EDU-Signature"] = md5(b64encode(n.encode())).hexdigest()
    new_header["X-EDU-Timestamp"] = str(t)
    new_header["X-EDU-Type"] = "pc"
    return new_header


if __name__ == "__main__":
    print(make_sign("GET", "1773665660335"))
