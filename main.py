import json
import os
import hashlib
from typing import Any, cast
from asyncio import run, gather
from src.educoder import Educoder
from pathlib import Path


def make_numeric_id(seed: str, length: int = 12) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return str(int(digest, 16) % (10**length)).zfill(length)


def infer_language(filename: str) -> str | None:
    ext = Path(filename).suffix.lower()
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".c": "c",
        ".go": "go",
        ".rs": "rust",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".kt": "kotlin",
        ".sql": "sql",
        ".sh": "shell",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".xml": "xml",
        ".md": "markdown",
    }
    return ext_map.get(ext)


def build_problem_source_files(codes: list[dict[str, str]]) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    for code_item in codes:
        content = code_item.get("content", "")
        source_file: dict[str, str] = {"code": content}

        filename = code_item.get("filename", "")
        if filename:
            source_file["filename"] = filename
            language = infer_language(filename)
            if language:
                source_file["language"] = language

        files.append(source_file)
    return files


def build_problem_data(
    title: str, description: str, codes: list[dict[str, str]]
) -> dict[str, Any]:
    problem_data: dict[str, Any] = {
        "type": "problem",
        "title": title,
        "content": build_problem_source_files(codes),
    }
    if description:
        problem_data["description"] = description
    return problem_data


async def write_data_json(folder: Path, data: dict[str, Any]) -> None:
    folder.mkdir(exist_ok=True, parents=True)
    with (folder / "data.json").open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def merge_problem_set_content(
    folder: Path, title: str, new_refs: list[dict[str, str]]
) -> dict[str, Any]:
    existing_order: list[str] = []
    merged_by_id: dict[str, dict[str, str]] = {}
    data_file = folder / "data.json"

    if data_file.exists():
        try:
            with data_file.open("r", encoding="utf-8") as f:
                old_data_raw: Any = json.load(f)
            if isinstance(old_data_raw, dict):
                old_data = cast(dict[str, Any], old_data_raw)
                old_type = old_data.get("type")
                old_content_raw = old_data.get("content")
                if old_type == "problemSet" and isinstance(old_content_raw, list):
                    old_content = cast(list[Any], old_content_raw)
                    for item_raw in old_content:
                        if isinstance(item_raw, dict):
                            item = cast(dict[str, Any], item_raw)
                            item_id_raw = item.get("id")
                            item_title_raw = item.get("title")
                            if isinstance(item_id_raw, str) and isinstance(
                                item_title_raw, str
                            ):
                                item_id: str = item_id_raw
                                existing_order.append(item_id)
                                merged_by_id[item_id] = {
                                    "id": item_id,
                                    "title": item_title_raw,
                                }
        except (json.JSONDecodeError, OSError):
            pass

    for ref in new_refs:
        item_id = ref["id"]
        merged_by_id[item_id] = {"id": item_id, "title": ref["title"]}
        if item_id not in existing_order:
            existing_order.append(item_id)

    merged_content = [merged_by_id[item_id] for item_id in existing_order]
    return {"type": "problemSet", "title": title, "content": merged_content}


async def write_work_report(
    output_root: Path,
    course_uuid: str,
    home_work_name: str,
    homework_id: str,
    work_report: list[tuple[str, str, list[dict[str, str]]]],
) -> dict[str, str]:
    homework_folder_id = make_numeric_id(f"course:{course_uuid}:homework:{homework_id}")
    homework_dir = output_root / homework_folder_id

    problem_refs: list[dict[str, str]] = []
    for index, (title, description, codes) in enumerate(work_report):
        problem_id = make_numeric_id(
            f"homework:{homework_id}:problem:{index}:{title}:{description}"
        )
        problem_refs.append({"id": problem_id, "title": title})
        problem_dir = homework_dir / problem_id
        problem_data = build_problem_data(title, description, codes)
        await write_data_json(problem_dir, problem_data)

    homework_data = merge_problem_set_content(homework_dir, home_work_name, problem_refs)
    await write_data_json(homework_dir, homework_data)
    return {"id": homework_folder_id, "title": home_work_name}


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
        course_name = course_list[course_idx][0]
        course_uuid = course_list[course_idx][2]
        output_root = Path("output")
        course_folder = make_numeric_id(f"course:{course_uuid}")
        course_root = output_root / course_folder

        homework_refs = await gather(
            *[
                write_work_report(
                    course_root,
                    course_uuid,
                    homework_list[idx][0],
                    str(homework_list[idx][1]),
                    await educoder.get_work_report(homework_list[idx][2]),
                )
                for idx in homework_idx_list
            ]
        )

        course_data = merge_problem_set_content(course_root, course_name, homework_refs)
        await write_data_json(course_root, course_data)

        root_ref = [{"id": course_folder, "title": course_name}]
        root_data = merge_problem_set_content(output_root, "Educoder Courses", root_ref)
        await write_data_json(output_root, root_data)


if __name__ == "__main__":
    run(main())
