from ..base import EducoderSession


async def get_origin_homework_list(session: EducoderSession, course_uuid: str):
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
    url = f"https://data.educoder.net/api/courses/{course_uuid}/homework_commons.json"
    async with session.get(url=url) as response:
        data = await response.json()
        return data


async def get_homework_list(session: EducoderSession, course_uuid: str):
    """获取作业列表

    参数:
    - `session`: EducoderSession 对象
    - `course_uuid`: 课程 uuid // 由 `get_course_url_list` 获取的字典的值的第二个元素
    返回值:
    一个列表，每个元素是一个元组，包含:
    - 作业名称 `homework_name`
    - 作业 id `homework_id`
    - 学生作业 id `student_work_id`
    """
    data = await get_origin_homework_list(session, course_uuid)
    homework_list: list[tuple[str, str, str]] = []
    for homework in data["homeworks"]:
        homework_list.append(
            (
                homework["name"],
                homework["homework_id"],
                homework["student_work_id"],
            )
        )
    return homework_list
