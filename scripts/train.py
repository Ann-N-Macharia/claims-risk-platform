from pathlib import Path

from claims_platform.data import generate_claims, save_dataset, validate_claims
from claims_platform.model import train_models


def main() -> None:
    data = generate_claims()
    errors = validate_claims(data)
    if errors:
        raise SystemExit(f"Data validation failed: {errors}")
    save_dataset(data, Path("artifacts/claims.csv"))
    train_models()
    print("Training complete. Artifacts saved under artifacts/.")


if __name__ == "__main__":
    main()
