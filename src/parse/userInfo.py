from typing import Any
from base import EducoderSession


async def get_origin_user_info(session: EducoderSession) -> dict[str, Any]:
    """获取用户信息

    要求已经登录

    返回一个字典，包含用户信息

    主要包含以下字段:
    - `login`: 用户名
    """
    url = "https://data.educoder.net/api/users/get_user_info.json"

    async with session.get(url) as response:
        data = await response.json()
        return data


async def get_user_info(session: EducoderSession) -> dict[str, str]:
    """获取用户信息

    要求已经登录

    返回一个字典，包含用户信息

    主要包含以下字段:
    - `login`: 用户名
    """
    data = await get_origin_user_info(session)
    return {
        "login": data["login"],
    }
