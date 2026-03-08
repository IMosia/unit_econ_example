import json
import csv
import os
from datetime import datetime
import math
from dotenv import load_dotenv
load_dotenv()

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

# ── Authentication ───────────────────────────────────────────
APP_PASSWORD = os.environ.get("APP_PASSWORD", "admin")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Enter password", type="password")
    if st.button("Login"):
        import hmac
        if hmac.compare_digest(pwd, APP_PASSWORD):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

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
        cost_per_free_user = st.number_input(
            "Cost / Free User / Month ($)", min_value=0.0, value=defaults["cost_per_free_user"], step=0.1, format="%.2f"
        )

    col3, col4 = st.columns(2)
    with col3:
        cost_per_paying_user = st.number_input(
            "Cost / Paying User / Month ($)", min_value=0.0, value=defaults["cost_per_paying_user"], step=0.1, format="%.2f"
        )
    with col4:
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
            cost_per_free_user=cost_per_free_user,
            cost_per_paying_user=cost_per_paying_user,
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
    r5.metric("Avg Paying Lifetime", f"{result['customer_lifetime_months']:.1f} mo")
    r6.metric("Avg Free Lifetime", f"{result['free_user_lifetime_months']:.1f} mo")

    r7, r8, r9 = st.columns(3)
    r7.metric("Serving Cost / User", f"${result['serving_cost_per_user']:.2f}")
    r8.metric("Payback Period", f"{result['payback_period_months']:.1f} mo")
    r9.metric("Monthly Revenue / User", f"${result['monthly_revenue_per_user']:.2f}")

    healthy = result['ltv_to_cac_ratio'] >= 3
    st.metric("Health Check", "Healthy" if healthy else "Needs Work", delta="LTV/CAC >= 3" if healthy else "LTV/CAC < 3", delta_color="normal" if healthy else "inverse")

    # ── New users needed to cover general spending ───────────
    if general_spending > 0:
        st.divider()
        st.subheader("Spending Coverage")
        delta = result["delta_of_income"]
        if delta > 0:
            new_users_needed = math.ceil(general_spending / delta)

            # Per-user monthly breakdown scaled to required users
            total_revenue = new_users_needed * result["monthly_revenue_per_user"]
            total_marketing = new_users_needed * result["effective_cac"] * conversion_rate
            total_serving = new_users_needed * result["serving_cost_per_user"] / (result["customer_lifetime_months"] if result["customer_lifetime_months"] > 0 else 1)
            total_costs = total_marketing + total_serving + general_spending
            net_income = total_revenue - total_costs

            col_a, col_b = st.columns(2)
            col_a.metric("New Users Needed", f"{new_users_needed:,} / mo")
            col_b.metric("General Spending", f"${general_spending:,.2f} / mo")

            st.divider()
            st.subheader("Monthly Financial Breakdown")
            st.caption(f"Based on {new_users_needed:,} new users / month")

            b1, b2 = st.columns(2)
            with b1:
                st.markdown("**Income**")
                st.write(f"Subscription Revenue: **${total_revenue:,.2f}**")
            with b2:
                st.markdown("**Costs**")
                st.write(f"Marketing (CAC): **${total_marketing:,.2f}**")
                st.write(f"Serving Users: **${total_serving:,.2f}**")
                st.write(f"General Spending: **${general_spending:,.2f}**")
                st.write(f"Total Costs: **${total_costs:,.2f}**")

            net_color = "normal" if net_income >= 0 else "inverse"
            st.metric("Net Income / Month", f"${net_income:,.2f}", delta=f"{'profit' if net_income >= 0 else 'loss'}", delta_color=net_color)
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
        "cost_per_free_user": cost_per_free_user,
        "cost_per_paying_user": cost_per_paying_user,
        "general_spending": general_spending,
        "ltv": result["ltv"],
        "effective_cac": result["effective_cac"],
        "ltv_to_cac_ratio": result["ltv_to_cac_ratio"],
        "delta_of_income": result["delta_of_income"],
        "customer_lifetime_months": result["customer_lifetime_months"],
        "payback_period_months": result["payback_period_months"],
        "monthly_revenue_per_user": result["monthly_revenue_per_user"],
        "serving_cost_per_user": result["serving_cost_per_user"],
    }
    if general_spending > 0 and result["delta_of_income"] > 0:
        trial_row["new_users_needed"] = new_users_needed
    else:
        trial_row["new_users_needed"] = ""

    append_to_trials(trial_row)
