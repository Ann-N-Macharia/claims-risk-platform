from typing import Literal

from pydantic import BaseModel, Field


IncidentType = Literal["collision", "theft", "fire", "weather"]


class ClaimRequest(BaseModel):
    claim_amount: float = Field(gt=0, le=5_000_000)
    policy_tenure_months: int = Field(ge=1, le=600)
    customer_age: int = Field(ge=18, le=100)
    vehicle_age_years: int = Field(ge=0, le=50)
    prior_claims: int = Field(ge=0, le=50)
    claim_hour: int = Field(ge=0, le=23)
    incident_type: IncidentType
    documentation_complete: bool
    police_report_filed: bool


class PredictionResponse(BaseModel):
    fraud_risk_probability: float = Field(ge=0, le=1)
    fraud_risk_band: Literal["low", "medium", "high"]
    predicted_claim_severity: float = Field(ge=0)
    recommendation: str
    model_version: str
    disclaimer: str

