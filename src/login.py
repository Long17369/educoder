from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base64 import b64encode
from yarl import URL

from .base import EducoderSession
from .make_header import make_header


def encrypt_password(password: str) -> str:
    key = "5183666c72eec9e4".encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, key)  # type: ignore
    padded_password = pad(password.strip().encode(), AES.block_size)
    encrypted_password = cipher.encrypt(padded_password)
    result = b64encode(encrypted_password).decode("utf-8")
    return result


async def login(username: str, password: str):
    """登录

    参数:
    - `username`: 用户名
    - `password`: 密码

    返回值:
    登录成功时返回一个 `http.cookies.SimpleCookie` 对象，包含登录后的 cookies。
    登录失败时返回 `None`。
    """
    url = URL("https://data.educoder.net/api/accounts/login.json")
    async with EducoderSession(headers=make_header("POST")) as session:
        async with session.post(
            url, json={"login": username, "password": encrypt_password(password)}
        ) as response:
            if response.status == 200:
                return session.cookie_jar
            else:
                return None


if __name__ == "__main__":
    import asyncio
    import os

    username = os.getenv("EDUCORDER_USERNAME") or input(
        "Enter your EDUCORDER_USERNAME: "
    )
    password = os.getenv("EDUCORDER_PASSWORD") or input(
        "Enter your EDUCORDER_PASSWORD: "
    )

    if not username or not password:
        print(
            "Please set the EDUCORDER_USERNAME and EDUCORDER_PASSWORD environment variables."
        )
    else:
        cookies = asyncio.run(login(username, password))
        print(cookies)
