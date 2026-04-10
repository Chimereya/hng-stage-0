from pydantic import BaseModel

# These pydantic models strictly enforces the response format

class GenderData(BaseModel):
    name: str
    gender: str
    probability: float
    sample_size: int
    is_confident: bool
    processed_at: str

class SuccessResponse(BaseModel):
    status: str = "success"
    data: GenderData

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str