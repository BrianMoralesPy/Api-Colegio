from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel import Session, text
from core.database import get_session
import time

router = APIRouter(tags=["Health"])


# 1️⃣ Liveness (sin DB)
@router.api_route("/live", methods=["GET", "HEAD"])
def live(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"status": "alive"}


# 2️⃣ Health check completo (incluye DB)
@router.api_route("/health", methods=["GET", "HEAD"], summary="Full health check")
def health(
    request: Request,
    session: Session = Depends(get_session)
):
    try:
        start = time.time()
        session.exec(text("SELECT 1"))
        response_time = round((time.time() - start) * 1000, 2)

        if request.method == "HEAD":
            return Response(status_code=200)

        return {
            "status": "ok",
            "database": "connected",
            "response_time_ms": response_time
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection error"
        )