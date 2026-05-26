from ..base import EducoderSession
from ..models import CodeItem, StudentWorkID, WorkReportItem


async def get_origin_work_report(
    session: EducoderSession, student_work_id: StudentWorkID
):
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
    session: EducoderSession, student_work_id: StudentWorkID
) -> list[WorkReportItem]:
    """获取作业报告

    参数:
    - `session`: EducoderSession 对象
    - `student_work_id`: 学生作业 id // 由 `get_homework_list` 获取的列表中每个元素的 student_work_id
    返回值:
    一个 WorkReportItem 列表
    """
    data = await get_origin_work_report(session, student_work_id)
    result: list[WorkReportItem] = []
    for i in data["shixun_detail"]:
        result.append(
            WorkReportItem(
                subject=i["subject"],
                challenge_description=i["challenge_description"],
                game_codes=[
                    CodeItem(
                        content=code.get("content", ""),
                        filename=code.get("filename", ""),
                        path=code.get("path", ""),
                    )
                    for code in i["game_codes"]
                ],
            )
        )
    return result
