# Feature Engineering Documentation

## Overview

This document describes the engineered features created for the Telco Customer Churn prediction model.

## Feature Categories

### 1. Tenure Features

| Feature | Type | Description | Business Logic |
|---------|------|-------------|----------------|
| `tenure_years` | float | Tenure in years | `tenure_months / 12` |
| `tenure_group` | string | Customer lifecycle stage | new: <12mo, medium: 12-36mo, long_term: >36mo |

**Insights:**
- New customers have 47.44% churn rate vs 11.93% for long-term customers
- 31% of customers are in the "new" category (high risk)

### 2. Financial Features

| Feature | Type | Description | Formula |
|---------|------|-------------|---------|
| `avg_monthly_charges` | decimal | Historical average monthly charges | `total_charges / tenure_months` (or `monthly_charges` for new customers) |
| `charge_velocity` | decimal | Rate of change in charges | `monthly_charges - avg_monthly_charges` |
| `lifetime_value_proxy` | decimal | Customer lifetime value estimate | `monthly_charges * tenure_months` |
| `revenue_per_service` | decimal | Revenue efficiency | `monthly_charges / (total_services_count + 1)` |
| `is_high_value` | boolean | Above-median revenue customer | `monthly_charges > median(monthly_charges)` |

**Insights:**
- Charge velocity indicates pricing changes that may trigger churn
- High-value customers have different churn patterns

### 3. Service Features

| Feature | Type | Description | Logic |
|---------|------|-------------|-------|
| `total_services_count` | integer | Count of premium services | Sum of: online_security, online_backup, device_protection, tech_support, streaming_tv, streaming_movies |
| `has_premium_services` | boolean | Has any premium service | `total_services_count > 0` |
| `has_internet_service` | boolean | Has any internet service | `internet_service != 'No'` |
| `has_fiber_optic` | boolean | Has fiber optic service | `internet_service == 'Fiber optic'` |

**Insights:**
- Average services per customer: 2.04
- More services correlate with lower churn (engagement)
- Fiber optic customers show different behavior patterns

### 4. Contract & Billing Features

| Feature | Type | Description | Logic |
|---------|------|-------------|-------|
| `is_month_to_month` | boolean | Month-to-month contract | `contract_type == 'Month-to-month'` |
| `is_electronic_payment` | boolean | Electronic payment method | `payment_method contains 'Electronic'` |

**Insights:**
- 55% of customers are on month-to-month contracts
- Month-to-month contracts are a strong churn indicator

### 5. Risk & Engagement Scores

#### Churn Risk Score (0-10)
Composite score based on known churn risk factors:

```python
churn_risk_score = (
    is_month_to_month * 3 +      # Flexible contract = high risk
    has_fiber_optic * 2 +         # Premium service expectations
    (tenure_months < 12) * 2 +    # New customer = high risk
    (total_services_count == 0) * 2 +  # Low engagement
    is_paperless_billing * 1      # Digital preference
)
```

**Score Distribution & Churn Rate:**
| Score | Customers | Churn Rate |
|-------|-----------|------------|
| 0 | 559 | 4.11% |
| 3 | 1,157 | 12.36% |
| 6 | 1,268 | 43.45% |
| 8 | 780 | 61.15% |
| 10 | 218 | 70.64% |

#### Engagement Score (0+)
Positive indicator of customer commitment:

```python
engagement_score = (
    has_partner * 1 +           # Family stability
    has_dependents * 1 +        # Household needs
    total_services_count * 1 +  # Service engagement
    (tenure_months >= 24) * 2   # Long-term relationship
)
```

**Insights:**
- Average engagement score: 3.94
- Higher engagement scores correlate with lower churn
- Can be used to identify customers worth retention investment

## Feature Correlation with Churn

### Strong Predictors (High Correlation)
1. **churn_risk_score** - Composite metric, strongest predictor
2. **is_month_to_month** - 3x weight in risk score
3. **tenure_group** - New customers 4x more likely to churn
4. **total_services_count** - Inverse correlation (more services = less churn)

### Moderate Predictors
1. **has_fiber_optic** - Premium expectations
2. **is_paperless_billing** - Digital customer behavior
3. **charge_velocity** - Recent price changes
4. **engagement_score** - Customer commitment level

### Supporting Features
1. **payment_method** - Payment friction
2. **is_high_value** - Customer value segment
3. **revenue_per_service** - Service efficiency
4. **has_premium_services** - Engagement indicator

## Usage in ML Pipeline

### For Training
```python
import polars as pl

# Load features
df = pl.read_parquet("fct_churn_features.parquet")

# Select feature columns
feature_cols = [
    "tenure_months", "tenure_group",
    "monthly_charges", "avg_monthly_charges", "charge_velocity",
    "total_services_count", "has_premium_services",
    "churn_risk_score", "engagement_score",
    # ... other features
]

X = df.select(feature_cols)
y = df.select("has_churned")
```

### For Inference
All features can be computed from the base customer record in real-time.

## Feature Engineering Methodology

### Technology Stack
- **Polars**: High-performance DataFrame operations (10-100x faster than pandas)
- **dbt Python**: Reproducible transformation pipeline
- **DuckDB**: Efficient storage and querying

### Design Principles
1. **Domain-driven**: Features based on telco churn domain knowledge
2. **Explainable**: All features have clear business interpretation
3. **Reproducible**: Deterministic transformations in version control
4. **Testable**: Comprehensive data quality tests
5. **Scalable**: Polars enables efficient processing of large datasets

## Next Steps

### Potential Additional Features
1. **Time-based**: Seasonality, day-of-week patterns
2. **Cohort analysis**: Customer acquisition cohort features
3. **Interaction features**: Cross-products of key features
4. **Aggregations**: Neighborhood/segment statistics
5. **Text features**: If customer notes/feedback available

### Feature Selection
Use the ML experimentation layer to:
- Run feature importance analysis
- Perform recursive feature elimination
- Test feature combinations
- Optimize feature set for model performance
