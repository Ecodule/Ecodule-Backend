from pydantic import BaseModel

class UserStatsResponse(BaseModel):
    total_money_saved: float = 0.0
    total_co2_reduction: float = 0.0

class OverallStatsResponse(BaseModel):
    total_money_saved: float = 0.0
    total_co2_reduction: float = 0.0