from typing import Any, Mapping

from aiohttp import ClientResponse, ClientSession
from yarl import URL

from ..make_header import make_header


class EducoderSession(ClientSession):
    async def _request(  # type: ignore
        self,
        method: str,
        str_or_url: str | URL,
        *,
        headers: Mapping[str, str] | None = None,
        **kwargs: dict[Any, Any],
    ) -> ClientResponse:
        headers = make_header(method, headers)  # type: ignore
        return await super()._request(method, str_or_url, headers=headers, **kwargs)  # type: ignore
