"""内部数据模型 —— 非网络原始数据，用于各层之间传递"""

from pathlib import Path
from typing import Literal, NewType

from pydantic import BaseModel, ValidationError

# ── 强类型 ID ─────────────────────────────────────────────────
# 用 NewType 防止不同含义的 str ID 被误传

CourseUUID = NewType("CourseUUID", str)
HomeworkID = NewType("HomeworkID", str)
StudentWorkID = NewType("StudentWorkID", str)
ProblemID = NewType("ProblemID", str)


# ── 内部传递模型 ──────────────────────────────────────────────


class Course(BaseModel):
    """课程"""

    name: str
    url: str
    uuid: CourseUUID


class Homework(BaseModel):
    """作业"""

    name: str
    homework_id: HomeworkID
    student_work_id: StudentWorkID


class CodeItem(BaseModel):
    """单个代码文件（来自网络原始数据）"""

    content: str = ""
    filename: str = ""
    path: str = ""


class WorkReportItem(BaseModel):
    """作业报告中的单个题目"""

    subject: str
    challenge_description: str
    game_codes: list[CodeItem]


class UserInfo(BaseModel):
    """用户信息"""

    login: str


# ── 输出模型 ──────────────────────────────────────────────────


class SourceFile(BaseModel):
    """输出用的代码文件"""

    code: str
    filename: str = ""
    language: str | None = None


class Problem(BaseModel):
    """单个题目"""

    type: Literal["problem"] = "problem"
    title: str
    description: str = ""
    content: list[SourceFile]


class ProblemRef(BaseModel):
    """题目引用（用于 ProblemSet.content）"""

    id: ProblemID
    title: str


class ProblemSet(BaseModel):
    """题目集合"""

    type: str
    title: str
    content: list[ProblemRef]

    @classmethod
    def from_file(cls, folder: Path) -> "ProblemSet | None":
        data_file = folder / "data.json"
        if not data_file.exists():
            return None
        try:
            return cls.model_validate_json(data_file.read_text(encoding="utf-8"))
        except (ValidationError, OSError):
            return None

    def merge_refs(self, new_refs: list[ProblemRef]) -> "ProblemSet":
        merged_by_id: dict[ProblemID, ProblemRef] = {r.id: r for r in self.content}
        existing_order = [r.id for r in self.content]
        for ref in new_refs:
            merged_by_id[ref.id] = ref
            if ref.id not in existing_order:
                existing_order.append(ref.id)
        return ProblemSet(
            type="problemSet",
            title=self.title,
            content=[merged_by_id[i] for i in existing_order],
        )
