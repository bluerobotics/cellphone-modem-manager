from fastapi import APIRouter, HTTPException, Query, status
from fastapi_versioning import versioned_api_route

from cells import CellFetcher
from cells.models import NearbyCellTower
from settings import CellLocationSettings


cells_router_v1 = APIRouter(
    prefix="/cells",
    tags=["cells_v1"],
    route_class=versioned_api_route(1, 0),
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


cell_fetcher = CellFetcher()

@cells_router_v1.get("/coordinate", status_code=status.HTTP_200_OK)
async def fetch_cell_coordinate(
    mcc: int = Query(..., description="Mobile Country Code"),
    mnc: int = Query(..., description="Mobile Network Code"),
    lac: int = Query(..., description="Location Area Code"),
    cell_id: int = Query(..., description="Cell ID")
) -> CellLocationSettings:
    cell = await cell_fetcher.fetch_cell(mcc, mnc, lac, cell_id)

    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")

    return cell


@cells_router_v1.get("/nearby", status_code=status.HTTP_200_OK)
async def fetch_nearby_cells(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
) -> list[NearbyCellTower]:
    return await cell_fetcher.fetch_nearby_cells(lat, lon)
