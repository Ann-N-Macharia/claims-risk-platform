from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .data import FEATURE_COLUMNS, generate_claims, validate_claims

MODEL_VERSION = "claims-demo-1.0.0"
ARTIFACT_PATH = Path("artifacts/claims_models.joblib")


def _preprocessor() -> ColumnTransformer:
    categorical = ["incident_type"]
    numeric = [column for column in FEATURE_COLUMNS if column not in categorical]
    return ColumnTransformer(
        [
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("numeric", "passthrough", numeric),
        ]
    )


def train_models(path: Path = ARTIFACT_PATH) -> dict[str, Any]:
    data = generate_claims()
    errors = validate_claims(data)
    if errors:
        raise ValueError(f"Generated data failed validation: {errors}")

    features = data[FEATURE_COLUMNS]
    classifier = Pipeline(
        [
            ("preprocessor", _preprocessor()),
            ("model", RandomForestClassifier(n_estimators=160, random_state=42, class_weight="balanced")),
        ]
    )
    regressor = Pipeline(
        [
            ("preprocessor", _preprocessor()),
            ("model", RandomForestRegressor(n_estimators=160, random_state=42, min_samples_leaf=3)),
        ]
    )
    classifier.fit(features, data["fraud_flag"])
    regressor.fit(features, data["claim_amount"])
    artifact = {"classifier": classifier, "regressor": regressor, "model_version": MODEL_VERSION}
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, path)
    return artifact


def load_models(path: Path = ARTIFACT_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Model artifact not found at {path}. Run `py scripts/train.py` first.")
    return joblib.load(path)


def predict(claim: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:

    features = pd.DataFrame([claim], columns=FEATURE_COLUMNS)
    fraud_probability = float(artifact["classifier"].predict_proba(features)[0, 1])
    severity = max(0.0, float(artifact["regressor"].predict(features)[0]))
    if fraud_probability >= 0.7:
        band, recommendation = "high", "Route to a specialist investigator for review."
    elif fraud_probability >= 0.4:
        band, recommendation = "medium", "Request secondary review and verify supporting documents."
    else:
        band, recommendation = "low", "Continue standard claims processing with routine checks."
    return {
        "fraud_risk_probability": round(fraud_probability, 4),
        "fraud_risk_band": band,
        "predicted_claim_severity": round(severity, 2),
        "recommendation": recommendation,
        "model_version": artifact["model_version"],
        "disclaimer": "Decision support only. A qualified claims professional must make the final decision.",
    }

