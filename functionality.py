def calculate_unit_economics(
    churn_rate: float, 
    conversion_rate: float, 
    virality_rate: float, 
    cac: float, 
    subscription_price: float
) -> dict:
    """
    Calculates the unit economics for an app including LTV, LTV/CAC ratio, 
    and the income delta per paying unit.
    """
    # Prevent division by zero errors
    if churn_rate <= 0 or conversion_rate <= 0:
        raise ValueError("Churn rate and conversion rate must be strictly greater than 0.")
        
    # 1. Calculate the lifetime of a paying user
    customer_lifetime = 1.0 / churn_rate
    
    # 2. Calculate Lifetime Value (LTV)
    ltv = subscription_price * customer_lifetime
    
    # 3. Calculate Effective Customer Acquisition Cost (CAC)
    # Adjust for conversion rate to get cost per paying user
    # Adjust for virality rate (k-factor) dividing the cost across organic growth
    effective_cac = (cac / conversion_rate) / (1.0 + virality_rate)
    
    # 4. Calculate LTV to CAC Ratio
    ltv_to_cac = ltv / effective_cac if effective_cac > 0 else float('inf')
    
    # 5. Calculate Delta of Income for the unit
    income_delta = (ltv - effective_cac) * conversion_rate  # Income per user considering conversion rate
    
    return {
        "customer_lifetime_months": round(customer_lifetime, 1),
        "ltv": round(ltv, 2),
        "effective_cac": round(effective_cac, 2),
        "ltv_to_cac_ratio": round(ltv_to_cac, 2),
        "delta_of_income": round(income_delta, 2),
        "monthly_revenue_per_user": round(subscription_price * conversion_rate, 2),
        "payback_period_months": round(effective_cac / (subscription_price if subscription_price > 0 else 1), 1),
    }

# Example Usage:
# Churn: 5% monthly, Conversion: 10%, Virality: 0.2 (2 referrals per 10 users), CAC: $2.00, Price: $9.99
# result = calculate_unit_economics(0.05, 0.10, 0.2, 2.00, 9.99)
# print(result)