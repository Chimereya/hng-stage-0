# hng-stage-0


##  Description
This is a simple FastAPI service that classifies a given name by gender using the Genderize API.  
It processes the response and returns a structured output with confidence evaluation.

##  Features
- Classifies gender from a name
- Computes confidence based on probability and sample size
- Handles edge cases
- Proper error handling
- CORS enabled
- Fully tested with pytest


## Technology Stack
- **Framework:** FastAPI
- **Language:** Python 3.12
- **Testing:** Pytest with Respx for mocking


##  API Endpoint

### GET /api/classify

#### Query Parameters
- `name` (string, required)



#### Example Request
/api/classify?name=Peter

##  Success Response

```json
{
  "status": "success",
  "data": {
    "name": "peter",
    "gender": "male",
    "probability": 1.0,
    "sample_size": 1346866,
    "is_confident": true,
    "processed_at": "2026-04-10T17:48:18Z"
  }
}
```


##  Setup & Installation

1. **Clone the repository**
```bash
git clone https://github.com/Chimereya/hng-stage-0.git
```
cd hng-stage-0


2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run tests**
```bash
pytest
```

4. **Run the application locally**
```bash
uvicorn main:app --reload
```




