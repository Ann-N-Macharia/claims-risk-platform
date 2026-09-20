from pathlib import Path

import numpy as np
import pandas as pd

INCIDENT_TYPES = ("collision", "theft", "fire", "weather")
FEATURE_COLUMNS = [
    "claim_amount",
    "policy_tenure_months",
    "customer_age",
    "vehicle_age_years",
    "prior_claims",
    "claim_hour",
    "documentation_complete",
    "police_report_filed",
    "incident_type",
]


def generate_claims(n_rows: int = 1200, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    incident_type = rng.choice(INCIDENT_TYPES, size=n_rows, p=[0.52, 0.2, 0.08, 0.2])
    claim_amount = np.clip(rng.gamma(shape=2.4, scale=45000, size=n_rows), 5000, 750000)
    policy_tenure = rng.integers(1, 180, size=n_rows)
    customer_age = rng.integers(18, 86, size=n_rows)
    vehicle_age = rng.integers(0, 18, size=n_rows)
    prior_claims = rng.poisson(0.8, size=n_rows)
    claim_hour = rng.integers(0, 24, size=n_rows)
    documentation_complete = rng.choice([False, True], size=n_rows, p=[0.22, 0.78])
    police_report_filed = rng.choice([False, True], size=n_rows, p=[0.42, 0.58])

    incident_risk = pd.Series(incident_type).map(
        {"collision": 0.05, "theft": 0.18, "fire": 0.12, "weather": 0.04}
    ).to_numpy()
    logit = (
        -2.7
        + incident_risk
        + (claim_amount > 250000) * 0.8
        + (claim_hour < 5) * 0.5
        + (prior_claims >= 2) * 0.55
        + (~documentation_complete) * 0.9
        + (~police_report_filed) * 0.35
        + rng.normal(0, 0.45, n_rows)
    )
    fraud_probability = 1 / (1 + np.exp(-logit))
    fraud_flag = rng.binomial(1, fraud_probability)

    return pd.DataFrame(
        {
            "claim_amount": claim_amount.round(2),
            "policy_tenure_months": policy_tenure,
            "customer_age": customer_age,
            "vehicle_age_years": vehicle_age,
            "prior_claims": prior_claims,
            "claim_hour": claim_hour,
            "documentation_complete": documentation_complete,
            "police_report_filed": police_report_filed,
            "incident_type": incident_type,
            "fraud_flag": fraud_flag,
        }
    )


def validate_claims(data: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = set(FEATURE_COLUMNS + ["fraud_flag"])
    missing = required.difference(data.columns)
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")
    if data.empty:
        errors.append("Dataset is empty")
    if data[FEATURE_COLUMNS].isna().any().any():
        errors.append("Feature columns contain null values")
    if not data["claim_amount"].gt(0).all():
        errors.append("Claim amounts must be positive")
    if not data["incident_type"].isin(INCIDENT_TYPES).all():
        errors.append("Unknown incident type")
    return errors


def save_dataset(data: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)

