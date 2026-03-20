import json
import os
from typing import Any
from asyncio import run, gather
from src.educoder import Educoder
from pathlib import Path


async def write_to_file(filename: str, content: str | list[Any] | dict[str, Any]):
    output = Path("output")
    file_path = output / filename
    file_path.parent.mkdir(exist_ok=True, parents=True)
    with file_path.open("w", encoding="utf-8") as f:
        if isinstance(content, dict | list):
            import json

            json.dump(content, f, ensure_ascii=False, indent=4)
        else:
            f.write(content)


async def write_work_report(
    course_name: str,
    home_work_name: str,
    work_report: list[tuple[str, str, list[dict[str, str]]]],
):
    for name, _, codes in work_report:
        await write_to_file(f"{course_name}/{home_work_name}/{name}.json", codes)
    pass


async def main():
    username = os.getenv("EDUCORDER_USERNAME") or os.getenv("USERNAME")
    password = os.getenv("EDUCORDER_PASSWORD") or os.getenv("PASSWORD")
    if not username or not password:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            username = config.get("username")
            password = config.get("password")
    async with Educoder(username, password) as educoder:
        course_list = await educoder.get_course_list()
        print("课程列表:")
        for idx, course in enumerate(course_list):
            print(f"{idx}. {course[0]}")
        course_idx = int(input("请输入课程编号: "))
        course_uuid = course_list[course_idx][2]
        homework_list = await educoder.get_homework_list(course_uuid)
        print("作业列表:")
        for idx, homework in enumerate(homework_list):
            print(f"{idx}. {homework[0]}")
        homework_idx = input("请输入作业编号(可以输入范围如0-2): ")
        if "-" in homework_idx:
            start, end = map(int, homework_idx.split("-"))
            homework_idx_list = list(range(start, end + 1))
        else:
            homework_idx_list = [int(homework_idx)]
        await gather(
            *[
                write_work_report(
                    course_list[course_idx][0],
                    homework_list[idx][0],
                    await educoder.get_work_report(homework_list[idx][2]),
                )
                for idx in homework_idx_list
            ]
        )


if __name__ == "__main__":
    run(main())
