from pydantic import BaseModel 
from typing import Optional 
class HealthResponse(BaseModel): 
    status: str 
    database: bool 
    ai_models: dict 
