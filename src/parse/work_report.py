from base import EducoderSession


async def get_origin_work_report(session: EducoderSession, student_work_id: str):
    """获取作业报告

    参数:
    - `session`: EducoderSession 对象
    - `student_work_id`: 学生作业 id // 由 `get_homework_list` 获取的列表中每个元组的第三个元素
    返回值:
    一个字典，主要包括以下字段: (具体查看对应schema)
    ```
    {
        "shixun_detail": []
    }
    ```
    """
    url: str = f"https://data.educoder.net/api/student_works/{student_work_id}/shixun_work_report.json"
    async with session.get(url=url) as response:
        data = await response.json()
        return data


async def get_work_report(
    session: EducoderSession, student_work_id: str
) -> list[tuple[str, str, list[dict[str, str]]]]:
    """获取作业报告

    参数:
    - `session`: EducoderSession 对象
    - `student_work_id`: 学生作业 id // 由 `get_homework_list` 获取的列表中每个元组的第三个元素
    返回值:
    一个列表，每个元素是一个元组，包含以下三个元素:
    - 课程名称 (str)
    - 课程描述 (str)
    - 课程代码列表 (list[dict[str, str]])
        - 每个字典包含以下字段:
            - `path`: 代码路径 (str)
            - `filename`: 代码文件名 (str)
            - `content`: 代码内容 (str)
    """
    data = await get_origin_work_report(session, student_work_id)
    result: list[tuple[str, str, list[dict[str, str]]]] = []
    for i in data["shixun_detail"]:
        result.append((i["subject"], i["challenge_description"], i["game_codes"]))
    return result
