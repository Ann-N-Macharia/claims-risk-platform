# Claims Risk and Fraud Detection Platform

An insurance claims decision-support application demonstrating data validation, predictive modelling, API development, explainability, and a business-facing dashboard.

The model is trained on **synthetic data** and not be used for real claims decisions.

## Features

- Deterministic synthetic claims dataset for reproducible demos
- Input validation and data-quality checks
- Fraud-risk classification and claim-severity regression
- FastAPI prediction service with interactive OpenAPI documentation
- Streamlit dashboard for claims staff
- Human-in-the-loop framing: predictions support investigation; they do not approve or reject claims

## Local setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py -m scripts.train
uvicorn claims_platform.api:app --reload
```

Open <http://127.0.0.1:8000/docs> for the API documentation.

In a second terminal:

```powershell
streamlit run dashboard.py
```

By default, the dashboard calls the local API at `http://127.0.0.1:8000`. To test a deployed Render API from the local dashboard, set `API_URL` before starting Streamlit:

```powershell
$env:API_URL = "https://your-service-name.onrender.com"
streamlit run dashboard.py
```

The dashboard will then send requests to `https://your-service-name.onrender.com/predict`.

## Deploy the API to Render

This repository includes a `render.yaml` Blueprint for deploying the FastAPI service and Streamlit dashboard as two web services.

1. Push the `claims-risk-platform` folder to a GitHub repository.
2. In Render, choose **New +** and then **Blueprint**.
3. Connect the GitHub repository and select the branch containing `render.yaml`.
4. Confirm the `claims-risk-api` and `claims-risk-dashboard` services.
5. Deploy the services.
6. After deployment, open the API service's `/health` endpoint.
7. Open the dashboard service URL in your browser.

The container uses Render's `PORT` environment variable automatically. Render's free service may take a short time to wake after inactivity.

The dashboard's `API_URL` must point to the deployed API service URL. Update the value in `render.yaml` if Render assigned your API a different URL, or set `API_URL` in the dashboard service's Environment settings.

### Manual Render configuration

If you create a Web Service instead of using the Blueprint, use:

- **Runtime:** Docker
- **Dockerfile path:** `./Dockerfile`
- **Docker context:** `.`
- **Health check path:** `/health`

For the Streamlit service, use:

- **Runtime:** Python
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `streamlit run dashboard.py --server.address 0.0.0.0 --server.port $PORT`
- **Environment variable:** `API_URL=https://<your-api-service>.onrender.com`

## Example request

```powershell
$body = @{
  claim_amount = 125000
  policy_tenure_months = 18
  customer_age = 42
  vehicle_age_years = 4
  prior_claims = 1
  claim_hour = 23
  incident_type = "collision"
  documentation_complete = $false
  police_report_filed = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8000/predict -Method Post -Body $body -ContentType "application/json"
```

## Project structure

```text
claims-risk-platform/
├── claims_platform/
│   ├── api.py          # FastAPI application
│   ├── data.py         # Synthetic data generation and validation
│   ├── model.py        # Training, persistence, and prediction
│   └── schemas.py      # API request/response contracts
├── scripts/train.py    # Reproducible model training entry point
├── tests/
├── dashboard.py
└── Dockerfile
```

## Responsible AI and production notes

- Use real data only with approved access controls and retention policies.
- Review performance and error rates across relevant customer groups before release.
- Keep a human investigator in the loop for adverse or high-impact decisions.
- Log model version, input schema version, and prediction timestamp for auditability.
- Add drift monitoring and periodic recalibration before production use.
