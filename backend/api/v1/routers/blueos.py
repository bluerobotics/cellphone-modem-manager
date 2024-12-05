from typing import Any

import aiohttp
from fastapi import APIRouter, Response, status
from fastapi_versioning import versioned_api_route

from config import BLUE_OS_HOST


blueos_router_v1 = APIRouter(
    prefix="/blueos",
    tags=["blueos_v1"],
    route_class=versioned_api_route(1, 0),
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

# This just proxy all GET requests to the BlueOS host

@blueos_router_v1.get("/{path:path}", status_code=status.HTTP_200_OK)
async def blueos_proxy_get(path: str, response: Response):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{BLUE_OS_HOST}/{path}") as resp:
            resp.raise_for_status()
            response = Response(content=await resp.content.read(), status_code=resp.status)
    return response
