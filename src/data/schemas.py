"""Data schemas for validation using Pandera."""

import pandera as pa
import pandera.polars as ppa
from pandera import Column, DataFrameSchema


class ChurnFeatureSchema:
    """Schema for churn prediction features."""

    # Raw data schema (from dbt staging)
    raw_schema = DataFrameSchema(
        {
            "customer_id": Column(str, nullable=False, unique=True),
            "has_churned": Column(bool, nullable=False),
            # Demographics
            "gender": Column(str, pa.Check.isin(["Male", "Female"])),
            "is_senior_citizen": Column(bool),
            "has_partner": Column(bool),
            "has_dependents": Column(bool),
            # Tenure
            "tenure_months": Column(int, pa.Check.ge(0)),
            "tenure_years": Column(float, pa.Check.ge(0)),
            "tenure_group": Column(str, pa.Check.isin(["new", "medium", "long_term"])),
            # Financial
            "monthly_charges": Column(float, pa.Check.ge(0)),
            "total_charges": Column(float, pa.Check.ge(0)),
            "avg_monthly_charges": Column(float, pa.Check.ge(0)),
            "charge_velocity": Column(float),
            # Contract & Billing
            "contract_type": Column(
                str, pa.Check.isin(["Month-to-month", "One year", "Two year"])
            ),
            "is_paperless_billing": Column(bool),
            "payment_method": Column(str),
            "is_month_to_month": Column(bool),
            "is_electronic_payment": Column(bool),
            # Services
            "has_phone_service": Column(bool),
            "internet_service": Column(str),
            "has_internet_service": Column(bool),
            "has_fiber_optic": Column(bool),
            "online_security": Column(
                str, pa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "online_backup": Column(
                str, pa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "device_protection": Column(
                str, pa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "tech_support": Column(
                str, pa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "streaming_tv": Column(
                str, pa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "streaming_movies": Column(
                str, pa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "multiple_lines": Column(
                str, pa.Check.isin(["Yes", "No", "No phone service"])
            ),
            # Derived features
            "total_services_count": Column(int, pa.Check.in_range(0, 6)),
            "has_premium_services": Column(bool),
            "lifetime_value_proxy": Column(float, pa.Check.ge(0)),
            "revenue_per_service": Column(float, pa.Check.ge(0)),
            "is_high_value": Column(bool),
            "churn_risk_score": Column(int, pa.Check.in_range(0, 20)),
            "engagement_score": Column(int, pa.Check.in_range(0, 20)),
        },
        strict=True,
        coerce=True,  # Automatic type coercion
    )

    # Polars schema for feature loading
    polars_schema = ppa.DataFrameSchema(
        {
            "customer_id": ppa.Column(str, nullable=False, unique=True),
            "has_churned": ppa.Column(bool, nullable=False),
            # Demographics
            "gender": ppa.Column(str, ppa.Check.isin(["Male", "Female"])),
            "is_senior_citizen": ppa.Column(bool),
            "has_partner": ppa.Column(bool),
            "has_dependents": ppa.Column(bool),
            # Tenure
            "tenure_months": ppa.Column(int, ppa.Check.ge(0)),
            "tenure_years": ppa.Column(float, ppa.Check.ge(0)),
            "tenure_group": ppa.Column(
                str, ppa.Check.isin(["new", "medium", "long_term"])
            ),
            # Financial
            "monthly_charges": ppa.Column(float, ppa.Check.ge(0)),
            "total_charges": ppa.Column(float, ppa.Check.ge(0)),
            "avg_monthly_charges": ppa.Column(float, ppa.Check.ge(0)),
            "charge_velocity": ppa.Column(float),
            # Contract & Billing
            "contract_type": ppa.Column(
                str, ppa.Check.isin(["Month-to-month", "One year", "Two year"])
            ),
            "is_paperless_billing": ppa.Column(bool),
            "payment_method": ppa.Column(str),
            "is_month_to_month": ppa.Column(bool),
            "is_electronic_payment": ppa.Column(bool),
            # Services
            "has_phone_service": ppa.Column(bool),
            "internet_service": ppa.Column(str),
            "has_internet_service": ppa.Column(bool),
            "has_fiber_optic": ppa.Column(bool),
            "online_security": ppa.Column(
                str, ppa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "online_backup": ppa.Column(
                str, ppa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "device_protection": ppa.Column(
                str, ppa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "tech_support": ppa.Column(
                str, ppa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "streaming_tv": ppa.Column(
                str, ppa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "streaming_movies": ppa.Column(
                str, ppa.Check.isin(["Yes", "No", "No internet service"])
            ),
            "multiple_lines": ppa.Column(
                str, ppa.Check.isin(["Yes", "No", "No phone service"])
            ),
            # Derived features
            "total_services_count": ppa.Column(int, ppa.Check.in_range(0, 6)),
            "has_premium_services": ppa.Column(bool),
            "lifetime_value_proxy": ppa.Column(float, ppa.Check.ge(0)),
            "revenue_per_service": ppa.Column(float, ppa.Check.ge(0)),
            "is_high_value": ppa.Column(bool),
            "churn_risk_score": ppa.Column(int, ppa.Check.in_range(0, 20)),
            "engagement_score": ppa.Column(int, ppa.Check.in_range(0, 20)),
        },
        strict=True,
        coerce=True,
    )

    @staticmethod
    def get_categorical_columns():
        """Get list of categorical column names."""
        return [
            "gender",
            "tenure_group",
            "contract_type",
            "payment_method",
            "internet_service",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies",
            "multiple_lines",
        ]

    @staticmethod
    def get_feature_columns():
        """Get list of feature column names (excluding ID and target)."""
        all_cols = [
            "gender",
            "is_senior_citizen",
            "has_partner",
            "has_dependents",
            "tenure_months",
            "tenure_years",
            "tenure_group",
            "monthly_charges",
            "total_charges",
            "avg_monthly_charges",
            "charge_velocity",
            "contract_type",
            "is_paperless_billing",
            "payment_method",
            "is_month_to_month",
            "is_electronic_payment",
            "has_phone_service",
            "internet_service",
            "has_internet_service",
            "has_fiber_optic",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies",
            "multiple_lines",
            "total_services_count",
            "has_premium_services",
            "lifetime_value_proxy",
            "revenue_per_service",
            "is_high_value",
            "churn_risk_score",
            "engagement_score",
        ]
        return all_cols
