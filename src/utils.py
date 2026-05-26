"""工具函数"""

import hashlib
import json
from asyncio import gather
from pathlib import Path
from typing import Any, Coroutine

from pydantic import BaseModel

from .models import (
    CourseUUID,
    HomeworkID,
    Problem,
    ProblemID,
    ProblemRef,
    ProblemSet,
    SourceFile,
    WorkReportItem,
)


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


async def write_data_json(folder: Path, data: BaseModel) -> None:
    folder.mkdir(exist_ok=True, parents=True)
    with (folder / "data.json").open("w", encoding="utf-8") as f:
        json.dump(data.model_dump(), f, ensure_ascii=False, indent=4)


def merge_problem_set_content(
    folder: Path, title: str, new_refs: list[ProblemRef]
) -> ProblemSet:
    existing = ProblemSet.from_file(folder)
    if existing is not None and existing.type == "problemSet":
        merged = existing.merge_refs(new_refs)
    else:
        merged = ProblemSet(type="problemSet", title=title, content=new_refs)

    merged.title = title
    return merged


async def write_work_report(
    output_root: Path,
    course_uuid: CourseUUID,
    home_work_name: str,
    homework_id: HomeworkID,
    work_report: list[WorkReportItem],
) -> ProblemRef:
    homework_folder_id = ProblemID(
        make_numeric_id(f"course:{course_uuid}:homework:{homework_id}")
    )
    homework_dir = output_root / homework_folder_id

    problem_refs: list[ProblemRef] = []
    write_tasks: list[Coroutine[Any, Any, None]] = []
    for index, item in enumerate(work_report):
        problem_id = ProblemID(
            make_numeric_id(
                f"homework:{homework_id}:problem:{index}:{item.subject}:{item.challenge_description}"
            )
        )
        problem_refs.append(ProblemRef(id=problem_id, title=item.subject))
        problem_dir = homework_dir / problem_id
        source_files = [
            SourceFile(
                code=code.content,
                filename=code.filename,
                language=infer_language(code.filename),
            )
            for code in item.game_codes
        ]
        problem_data = Problem(
            title=item.subject,
            description=item.challenge_description,
            content=source_files,
        )
        write_tasks.append(write_data_json(problem_dir, problem_data))

    if write_tasks:
        await gather(*write_tasks)

    homework_data = merge_problem_set_content(
        homework_dir, home_work_name, problem_refs
    )
    await write_data_json(homework_dir, homework_data)
    return ProblemRef(id=homework_folder_id, title=home_work_name)
