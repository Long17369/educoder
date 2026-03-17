from typing import Any

from yarl import URL
from base.requsets import EducoderSession


async def get_course_list(session: EducoderSession, username: str) -> dict[str, Any]:
    """获取课程列表

    参数:
    - `session`: EducoderSession 对象
    - `username`: 用户名 // 由 `get_user_info` 获取的字典的 `login` 字段

    返回值:

    一个字典
    ```
    {
        count: int, //课程总数
        courses: list // 课程列表
    }
    ```
    courses 列表中的每个元素是一个字典，主要包含以下字段:
    - `first_category_url` 课程一级分类的 URL
    - `name` 课程名称
    """
    url = f"https://data.educoder.net/api/users/{username}/courses.json"
    async with session.get(url=url) as response:
        data = await response.json()
        return data
    return


async def get_course_url_list(
    session: EducoderSession, username: str
) -> dict[str, URL]:
    """获取课程 URL 列表

    参数:
    - `session`: EducoderSession 对象
    - `username`: 用户名 // 由 `get_user_info` 获取的字典的 `login` 字段

    返回值:
    一个字典，键为课程名称，值为课程 URL
    """
    data = await get_course_list(session, username)
    course_url_list: dict[str, URL] = {}
    for course in data["courses"]:
        course_url_list[course["name"]] = URL(
            "https://www.educoder.net" + course["first_category_url"]
        )
    return course_url_list
