from os import path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_versioning import VersionedFastAPI

# Routers
from api.v1.routers import blueos_router_v1, cells_router_v1, index_router_v1, modem_router_v1

application = FastAPI(
    title="Cellular Modem Manager Configuration API",
    description="This extension API provides ways to configure and explore resources of cellphone modems",
)

# API v1
application.include_router(blueos_router_v1)
application.include_router(index_router_v1)
application.include_router(cells_router_v1)
application.include_router(modem_router_v1)

application = VersionedFastAPI(application, prefix_format="/v{major}.{minor}", enable_latest=True)

@application.get("/", status_code=200)
async def root() -> RedirectResponse:
    """
    Root endpoint for Cellular Modem Manager extension.
    """

    return RedirectResponse(url="/static/index.html")


@application.get("/register_service", status_code=200)
def register_service() -> RedirectResponse:
    return RedirectResponse(url="/static/service.json")

# Mount static files
application.mount("/static", StaticFiles(directory=path.join(path.dirname(__file__), "static")), name="static")

# Enable CORS
application.add_middleware(CORSMiddleware, allow_origins=["*"])
