import httpx
from datetime import datetime, timezone

GENDERIZE_URL = "https://api.genderize.io"

# Service function to classify a name using the Genderize API
async def classify_name(name: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(GENDERIZE_URL, params={"name": name})
            if response.status_code != 200:
                return {"error": "External API error"}
            
            data = response.json()
        except Exception:
            return {"error": "Service unavailable"}
    
    gender = data.get("gender")
    count = data.get("count", 0)

    # Handling null or zero count
    if not gender or count == 0:
        return {"error": "No prediction available for the provided name"}
    
    # Processing the names
    prob = data.get("probability", 0.0)
    is_confident = (prob >= 0.7) and (count >= 100)

    return {
        "name": name,
        "gender": gender,
        "probability": prob,
        "sample_size": count,
        "is_confident": is_confident,
        "processed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    
        