# Unit Economics Calculator

A Streamlit app for calculating unit economics (LTV, CAC, LTV/CAC ratio, income delta) and determining how many new users per month are needed to cover general spending.

## Quick Start

```bash
make run
```

This installs dependencies from `requirements.txt` and launches the Streamlit app.

## Manual Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Inputs

| Parameter | Default | Description |
|---|---|---|
| Churn Rate (%) | 5.0 | Monthly churn rate |
| Conversion Rate (%) | 3.0 | Free-to-paid conversion rate |
| Virality Rate | 0.15 | K-factor (organic referrals) |
| CAC ($) | 2.50 | Cost to acquire one user |
| Subscription Price ($) | 9.99 | Monthly subscription price |
| General Spending ($) | 0.00 | Monthly operational spending |

Default values are stored in `defaults.json` and can be edited there.

## Outputs

- **LTV** – Lifetime value of a paying customer
- **Effective CAC** – Acquisition cost adjusted for conversion and virality
- **LTV / CAC Ratio** – Profitability indicator (>3 is healthy)
- **Income Delta** – Net income per acquired user
- **New Users Needed** – Monthly users required to cover general spending (shown when spending > 0)

Every calculation is appended to `trials.csv` for tracking.
