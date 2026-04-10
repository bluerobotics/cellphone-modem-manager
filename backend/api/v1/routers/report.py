from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi_versioning import versioned_api_route

from modem import Modem
from modem.exceptions import ATConnectionTimeout, InvalidModemDevice
from report.generator import ReportGenerator, DIAGNOSTIC_STEPS


report_router_v1 = APIRouter(
    prefix="/modem",
    tags=["report_v1"],
    route_class=versioned_api_route(1, 0),
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@report_router_v1.post("/{modem_id}/report", status_code=status.HTTP_200_OK)
async def generate_report(modem_id: str):
    """
    Start a new metrics report generation for the given modem, or stream the current
    one if a report is already being generated.
    Returns a newline-delimited JSON stream of report events.
    """
    try:
        modem = Modem.get_device(modem_id)
    except InvalidModemDevice as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except ATConnectionTimeout as error:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error

    generator = ReportGenerator.get_or_start(modem_id, modem)
    await generator.start()

    return StreamingResponse(
        generator.stream_events(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@report_router_v1.get("/{modem_id}/report/status", status_code=status.HTTP_200_OK)
async def report_status(modem_id: str):
    """
    Check whether a metrics report is currently being generated for the given modem.
    """
    generator = ReportGenerator.get(modem_id)
    if not generator:
        return {"running": False}

    completed = sum(1 for e in generator.events if e["type"] == "step_complete")

    return {
        "running": generator.running,
        "progress": {
            "current_step": completed,
            "total_steps": len(DIAGNOSTIC_STEPS),
        },
    }
