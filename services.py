import httpx
from datetime import datetime, timezone
from fastapi.responses import JSONResponse

GENDERIZE_URL = "https://api.genderize.io"


# Service function to classify a name using the Genderize API

async def classify_name(name: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(GENDERIZE_URL, params={"name": name})
            
            # Handling Rate Limits
            if response.status_code == 429:
                return {"error": "Rate limit exceeded. Try again later.", "code": 429}
            
            # Handling 502 Upstream API Error
            if response.status_code != 200:
                return {"error": "Upstream or server failure", "code": 502}
            
            data = response.json()

            # Extraction and Transformation
            gender = data.get("gender")
            count = data.get("count", 0)
            prob = data.get("probability", 0.0)

            # Handle names not found
            if gender is None or count == 0:
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": "error", 
                        "message": "No prediction available for the provided name"
                    }
                )

            # Confidence Logic
            is_confident = (prob >= 0.7) and (count >= 100)

            # Return success payload
            return {
                "name": name,
                "gender": gender,
                "probability": prob,
                "sample_size": count,
                "is_confident": is_confident,
                "processed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }

        except (httpx.ConnectError, httpx.TimeoutException):
            return {"error": "Upstream or server failure (Connection)", "code": 503}
        except Exception as e:
            return {"error": f"Upstream or server failure: {str(e)}", "code": 500}