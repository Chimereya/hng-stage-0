import httpx
from datetime import datetime, timezone

GENDERIZE_URL = "https://api.genderize.io"

# Service function to classify a name using the Genderize API
async def classify_name(name: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(GENDERIZE_URL, params={"name": name})
            # Handling rate limits (429) or Service Unavailable (503)
            if response.status_code == 429:
                return {"error": "Rate limit exceeded. Try again later.", "code": 429}
            
            if response.status_code != 200:
                return {"error": f"External API returned status {response.status_code}", "code": 502}
            
            data = response.json()

        except httpx.ConnectError:
            return {"error": "Could not connect to the classification service.", "code": 503}
        except httpx.TimeoutException:
            return {"error": "Classification service timed out.", "code": 504}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}", "code": 500}

    # Extracting fields from the external API response
    gender = data.get("gender")
    count = data.get("count", 0)
    prob = data.get("probability", 0.0)

    # Handling null or zero count
    if not gender or count == 0:
        return {
            "error": "No prediction available for the provided name. Try a more common name.", 
            "code": 200 
        }
    
    # Processing the name with confidence logic
    is_confident = (prob >= 0.7) and (count >= 100)

    return {
        "name": name,
        "gender": gender,
        "probability": prob,
        "sample_size": count,
        "is_confident": is_confident,
        "processed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    
        