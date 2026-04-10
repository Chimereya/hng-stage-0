from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import httpx
from datetime import datetime, timezone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["access-control-allow-origin"] = "*"
    return response


@app.get("/api/classify")
async def classify(request: Request, name: Optional[str] = Query(default=None)):
    # Return 422 if name was passed as an array type
    raw_params = str(request.url.query)
    if "name[]" in raw_params:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "Invalid parameter type"}
        )

    # Return 400 if name is missing or blank
    if not name or not name.strip():
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Missing or empty name"}
        )
    
    # Calling the Genderize API to classify the name
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                "https://api.genderize.io",
                params={"name": name.strip()}
            )
        except Exception:
            return JSONResponse(
                status_code=502,
                content={"status": "error", "message": "External API unreachable"}
            )

        # Handling when the external API returns a non-200 status code
        if resp.status_code != 200:
            return JSONResponse(
                status_code=502,
                content={"status": "error", "message": "External API error"}
            )

        data = resp.json()

    # Handle null gender
    if not data.get("gender"):
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": "No prediction available"}
        )

    is_confident = (
        data.get("probability", 0) >= 0.90 and
        data.get("count", 0) >= 100
    )

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": {
                "name": data["name"],
                "gender": data["gender"],
                "probability": data["probability"],
                "count": data["count"],
                "is_confident": is_confident,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }
        }
    )
