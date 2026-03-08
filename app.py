import json
import csv
import os
from datetime import datetime
import math

import streamlit as st
from functionality import calculate_unit_economics

DEFAULTS_PATH = os.path.join(os.path.dirname(__file__), "defaults.json")
TRIALS_PATH = os.path.join(os.path.dirname(__file__), "trials.csv")

def load_defaults() -> dict:
    with open(DEFAULTS_PATH, "r") as f:
        return json.load(f)

def append_to_trials(row: dict):
    file_exists = os.path.isfile(TRIALS_PATH)
    with open(TRIALS_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Unit Economics Calculator", page_icon="📊", layout="centered")
st.title("📊 Unit Economics Calculator")

defaults = load_defaults()

# ── Input form ───────────────────────────────────────────────
with st.form("unit_form"):
    st.subheader("Input Parameters")

    col1, col2 = st.columns(2)

    with col1:
        churn_rate_pct = st.number_input(
            "Churn Rate (%)", min_value=0.01, value=defaults["churn_rate_pct"], step=0.1, format="%.2f"
        )
        conversion_rate_pct = st.number_input(
            "Conversion Rate (%)", min_value=0.01, value=defaults["conversion_rate_pct"], step=0.1, format="%.2f"
        )
        virality_rate = st.number_input(
            "Virality Rate (k-factor)", min_value=0.0, value=defaults["virality_rate"], step=0.01, format="%.2f"
        )

    with col2:
        cac = st.number_input(
            "CAC ($)", min_value=0.0, value=defaults["cac"], step=0.1, format="%.2f"
        )
        subscription_price = st.number_input(
            "Subscription Price ($)", min_value=0.01, value=defaults["subscription_price"], step=0.5, format="%.2f"
        )
        general_spending = st.number_input(
            "General Monthly Spending ($)", min_value=0.0, value=defaults["general_spending"], step=100.0, format="%.2f"
        )

    submitted = st.form_submit_button("Calculate", use_container_width=True)

# ── Calculation ──────────────────────────────────────────────
if submitted:
    churn_rate = churn_rate_pct / 100.0
    conversion_rate = conversion_rate_pct / 100.0

    try:
        result = calculate_unit_economics(
            churn_rate=churn_rate,
            conversion_rate=conversion_rate,
            virality_rate=virality_rate,
            cac=cac,
            subscription_price=subscription_price,
        )
    except ValueError as e:
        st.error(str(e))
        st.stop()

    # ── Results ──────────────────────────────────────────────
    st.divider()
    st.subheader("Results")

    r1, r2, r3 = st.columns(3)
    r1.metric("LTV", f"${result['ltv']:.2f}")
    r2.metric("Effective CAC", f"${result['effective_cac']:.2f}")
    r3.metric("LTV / CAC", f"{result['ltv_to_cac_ratio']:.2f}")

    r4, r5, r6 = st.columns(3)
    r4.metric("Income Delta / User", f"${result['delta_of_income']:.2f}")
    r5.metric("Avg Lifetime", f"{result['customer_lifetime_months']:.1f} months")
    r6.metric("Payback Period", f"{result['payback_period_months']:.1f} months")

    r7, r8 = st.columns(2)
    r7.metric("Monthly Revenue / User", f"${result['monthly_revenue_per_user']:.2f}")
    healthy = result['ltv_to_cac_ratio'] >= 3
    r8.metric("Health Check", "Healthy" if healthy else "Needs Work", delta="LTV/CAC >= 3" if healthy else "LTV/CAC < 3", delta_color="normal" if healthy else "inverse")

    # ── New users needed to cover general spending ───────────
    if general_spending > 0:
        st.divider()
        st.subheader("Spending Coverage")
        delta = result["delta_of_income"]
        if delta > 0:
            new_users_needed = math.ceil(general_spending / delta)
            col_a, col_b = st.columns(2)
            col_a.metric("General Spending", f"${general_spending:,.2f} / mo")
            col_b.metric("New Users Needed", f"{new_users_needed:,} / mo")
            st.caption(
                f"Each new user generates \${delta:.2f} in income delta. "
                f"You need {new_users_needed:,} new users every month to cover \${general_spending:,.2f} in spending."
            )
        else:
            st.warning(
                "Income delta per user is zero or negative — "
                "general spending cannot be sustained with current parameters."
            )

    # ── Append to trials.csv ─────────────────────────────────
    trial_row = {
        "timestamp": datetime.now().isoformat(),
        "churn_rate_pct": churn_rate_pct,
        "conversion_rate_pct": conversion_rate_pct,
        "virality_rate": virality_rate,
        "cac": cac,
        "subscription_price": subscription_price,
        "general_spending": general_spending,
        "ltv": result["ltv"],
        "effective_cac": result["effective_cac"],
        "ltv_to_cac_ratio": result["ltv_to_cac_ratio"],
        "delta_of_income": result["delta_of_income"],
        "customer_lifetime_months": result["customer_lifetime_months"],
        "payback_period_months": result["payback_period_months"],
        "monthly_revenue_per_user": result["monthly_revenue_per_user"],
    }
    if general_spending > 0 and result["delta_of_income"] > 0:
        trial_row["new_users_needed"] = new_users_needed
    else:
        trial_row["new_users_needed"] = ""

    append_to_trials(trial_row)
