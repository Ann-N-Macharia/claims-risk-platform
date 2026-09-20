from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .model import load_models, predict
from .schemas import ClaimRequest, PredictionResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.models = load_models()
    yield


app = FastAPI(
    title="Claims Risk and Fraud Detection API",
    version="1.0.0",
    description="Synthetic-data demonstration of an insurance claims decision-support service.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict_claim(claim: ClaimRequest) -> PredictionResponse:
    try:
        result = predict(claim.model_dump(), app.state.models)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PredictionResponse(**result)

