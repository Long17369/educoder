import json
import os
from asyncio import gather, run
from pathlib import Path

from src.base import gather_with_progress
from src.educoder import Educoder
from src.models import ProblemID, ProblemRef
from src.utils import (
    make_numeric_id,
    merge_problem_set_content,
    write_data_json,
    write_work_report,
)


async def main():
    username = os.getenv("EDUCORDER_USERNAME") or os.getenv("USERNAME")
    password = os.getenv("EDUCORDER_PASSWORD") or os.getenv("PASSWORD")
    if not username or not password:
        with open("config.json", "r", encoding="utf-8") as f:
            config: dict[str, str] = json.load(f)
            username = config.get("username")
            password = config.get("password")
    if not username or not password:
        print(
            "请在环境变量中设置EDUCORDER_USERNAME和EDUCORDER_PASSWORD，或在config.json中提供用户名和密码。"
        )
        return
    async with Educoder(username, password) as educoder:
        course_list = await educoder.get_course_list()
        print("课程列表:")
        for idx, course in enumerate(course_list):
            print(f"{idx}. {course.name}")
        course_idx = int(input("请输入课程编号: "))
        course_uuid = course_list[course_idx].uuid
        homework_list = await educoder.get_homework_list(course_uuid)
        print("作业列表:")
        for idx, homework in enumerate(homework_list):
            print(f"{idx}. {homework.name}")
        homework_idx = input("请输入作业编号(可以输入范围如0-2): ")
        if "-" in homework_idx:
            start, end = map(int, homework_idx.split("-"))
            homework_idx_list = list(range(start, end + 1))
        else:
            homework_idx_list = [int(homework_idx)]
        course_name = course_list[course_idx].name
        course_uuid = course_list[course_idx].uuid
        output_root = Path("output")
        course_folder = ProblemID(make_numeric_id(f"course:{course_uuid}"))
        course_root = output_root / course_folder

        # 先并行获取所有 work_report（网络 I/O，带进度条）
        work_reports = await gather_with_progress(
            [
                educoder.get_work_report(homework_list[idx].student_work_id)
                for idx in homework_idx_list
            ],
            desc="获取作业报告",
        )

        # 再并行写入所有作业数据（磁盘 I/O）
        homework_refs = await gather(
            *[
                write_work_report(
                    course_root,
                    course_uuid,
                    homework_list[idx].name,
                    homework_list[idx].homework_id,
                    work_reports[i],
                )
                for i, idx in enumerate(homework_idx_list)
            ]
        )

        course_data = merge_problem_set_content(course_root, course_name, homework_refs)
        await write_data_json(course_root, course_data)

        root_ref = [ProblemRef(id=course_folder, title=course_name)]
        root_data = merge_problem_set_content(output_root, "Educoder Courses", root_ref)
        await write_data_json(output_root, root_data)


if __name__ == "__main__":
    run(main())
