import requests
import streamlit as st


st.set_page_config(page_title="Claims Risk Review", page_icon="🛡️", layout="centered")
st.title("Claims Risk Review")
st.caption("Synthetic-data demonstration. Predictions support human review; they do not make claims decisions.")

with st.form("claim-form"):
    claim_amount = st.number_input("Claim amount", min_value=1.0, value=125000.0, step=5000.0)
    policy_tenure_months = st.number_input("Policy tenure (months)", min_value=1, value=18)
    customer_age = st.number_input("Customer age", min_value=18, max_value=100, value=42)
    vehicle_age_years = st.number_input("Vehicle age (years)", min_value=0, max_value=50, value=4)
    prior_claims = st.number_input("Prior claims", min_value=0, max_value=50, value=1)
    claim_hour = st.slider("Incident hour", min_value=0, max_value=23, value=23)
    incident_type = st.selectbox("Incident type", ["collision", "theft", "fire", "weather"])
    documentation_complete = st.checkbox("Documentation complete", value=False)
    police_report_filed = st.checkbox("Police report filed", value=True)
    submitted = st.form_submit_button("Assess claim")

if submitted:
    payload = {
        "claim_amount": claim_amount,
        "policy_tenure_months": policy_tenure_months,
        "customer_age": customer_age,
        "vehicle_age_years": vehicle_age_years,
        "prior_claims": prior_claims,
        "claim_hour": claim_hour,
        "incident_type": incident_type,
        "documentation_complete": documentation_complete,
        "police_report_filed": police_report_filed,
    }
    try:
        response = requests.post("http://127.0.0.1:8000/predict", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        st.metric("Fraud risk", f"{result['fraud_risk_probability']:.1%}", result["fraud_risk_band"].upper())
        st.metric("Predicted claim severity", f"{result['predicted_claim_severity']:,.0f}")
        st.info(result["recommendation"])
        st.caption(f"Model: {result['model_version']}")
    except requests.RequestException as exc:
        st.error(f"Prediction service unavailable: {exc}")

