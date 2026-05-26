from typing import Any

from ..base import EducoderSession
from ..models import UserInfo


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


async def get_user_info(session: EducoderSession) -> UserInfo:
    """获取用户信息

    要求已经登录

    返回一个 UserInfo 对象
    """
    data = await get_origin_user_info(session)
    return UserInfo(login=data["login"])
