from .base import EducoderSession
from .login import login
from .parse import get_course_list, get_homework_list, get_user_info, get_work_report


class Educoder:
    def __init__(self, username: str = "", password: str = "") -> None:
        self.username = username
        self.password = password
        self.session = EducoderSession()
        self._logined = False
        pass

    @property
    def logined(self) -> bool:
        return self._logined

    async def login(self):
        cookies = await login(self.username, self.password, self.session)
        if cookies is None:
            raise Exception("登录失败")
        self._logined = True

    async def get_course_list(self):
        if not self.logined:
            raise Exception("请先登录")
        user_info = await get_user_info(self.session)
        course_list = await get_course_list(self.session, user_info["login"])
        return course_list

    async def get_homework_list(self, course_uuid: str):
        if not self.logined:
            raise Exception("请先登录")
        homework_list = await get_homework_list(self.session, course_uuid)
        return homework_list

    async def get_work_report(self, student_work_id: str):
        if not self.logined:
            raise Exception("请先登录")
        work_report = await get_work_report(self.session, student_work_id)
        return work_report

    async def __aenter__(self):
        try:
            await self.login()
        except Exception as e:
            await self.session.close()
            raise e
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        await self.session.close()
