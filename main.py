from unittest import result

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from services import classify_name

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to add CORS headers to all responses
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["access-control-allow-origin"] = "*"
    return response

# Endpoint to classify a name using the Genderize API
@app.get("/api/classify")
async def classify(request: Request, name: Optional[str] = Query(default=None)):
    # Return 422 if name was passed as an array type
    raw_params = str(request.url.query)
    if "name[]" in raw_params:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "name is not a string"}
        )

    # Return 400 if name is missing or blank
    if not name or not name.strip():
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Missing or empty name parameter"}
        )
    
    # Call the service function to classify the name
    result = await classify_name(name.strip())

    # Handling the errors from the service function
    if "error" in result:
        return JSONResponse(
            status_code=result.get("code", 500),
            content={
                "status": "error",
                "message": result["error"]
            }
        )

    return {
        "status": "success",
        "data": result
    }
