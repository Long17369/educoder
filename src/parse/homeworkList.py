from typing import Any

from ..base import EducoderSession, gather_with_progress


async def get_origin_homework_list(
    session: EducoderSession, course_uuid: str, page: int = 1
) -> dict[str, Any]:
    """获取原始作业列表

    参数:
    - `session`: EducoderSession 对象
    - `course_uuid`: 课程 uuid // 由 `get_course_url_list` 获取的字典的值的第二个元素
    返回值:

    一个字典, 主要包括以下字段:
    ```
    {
        homeworks: list // 作业列表
    }
    ```
    每个作业是一个字典，主要包括以下字段:
    ```
    {
        "homework_id": int, // 作业 id
        "name": str, // 作业名称
        "student_work_id": int, // 学生作业 id
    }
    ```
    """
    url = f"https://data.educoder.net/api/courses/{course_uuid}/homework_commons.json?page={page}"
    async with session.get(url=url) as response:
        data = await response.json()
        return data


async def get_homework_list(session: EducoderSession, course_uuid: str):
    """获取作业列表, 自动处理分页

    参数:
    - `session`: EducoderSession 对象
    - `course_uuid`: 课程 uuid // 由 `get_course_url_list` 获取的字典的值的第二个元素
    返回值:
    一个列表，每个元素是一个元组，包含:
    - 作业名称 `homework_name`
    - 作业 id `homework_id`
    - 学生作业 id `student_work_id`
    """

    async def get_homework_list_page(page: int):
        data = await get_origin_homework_list(session, course_uuid, page)
        homework_list: list[tuple[str, str, str]] = []
        for homework in data["homeworks"]:
            homework_list.append(
                (
                    homework["name"],
                    homework["homework_id"],
                    homework["student_work_id"],
                )
            )
        return homework_list, data.get("query_total_count", 0)

    homework_list, total_count = await get_homework_list_page(1)

    total_pages = (total_count + len(homework_list) - 1) // len(homework_list)
    if total_pages <= 1:
        return homework_list

    tasks = [get_homework_list_page(page + 1) for page in range(1, total_pages)]
    results = await gather_with_progress(tasks, desc="获取作业列表分页", unit="页")
    for homework_list_page, _ in results:
        homework_list.extend(homework_list_page)

    return homework_list
