"""并发执行工具 —— 带进度条的 asyncio.gather 封装"""

from asyncio import gather
from typing import Awaitable, Sequence, TypeVar

from tqdm.asyncio import tqdm

T = TypeVar("T")


async def gather_with_progress(
    coros: Sequence[Awaitable[T]],
    desc: str = "请求中",
    unit: str = "个",
) -> list[T]:
    """并行执行一组协程，同时显示 tqdm 进度条。

    每完成一个协程，进度条前进一格。适用于网络 I/O 等可并发的异步任务。

    参数:
        coros: 协程序列
        desc: 进度条描述文本
        unit: 进度条单位

    返回:
        按输入顺序排列的结果列表
    """
    with tqdm(total=len(coros), desc=desc, unit=unit) as tqdm_asyncio:

        async def _run_one(coro: Awaitable[T]) -> T:
            result = await coro
            tqdm_asyncio.update(1)
            return result

        tasks = [_run_one(coro) for coro in coros]

        results = await gather(*tasks)

    return results
