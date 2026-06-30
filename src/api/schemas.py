"""Pydantic schemas for API requests and responses."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class CustomerFeatures(BaseModel):
    """Customer features for churn prediction."""

    # Demographics
    gender: str = Field(..., description="Customer gender: Male or Female")
    is_senior_citizen: bool = Field(
        ..., description="Whether customer is a senior citizen"
    )
    has_partner: bool = Field(..., description="Whether customer has a partner")
    has_dependents: bool = Field(..., description="Whether customer has dependents")

    # Tenure
    tenure_months: int = Field(
        ..., ge=0, description="Number of months with the company"
    )
    tenure_years: float = Field(
        ..., ge=0, description="Number of years with the company"
    )
    tenure_group: str = Field(
        ..., description="Tenure group: new, medium, or long_term"
    )

    # Financial
    monthly_charges: float = Field(..., ge=0, description="Monthly charges")
    total_charges: float = Field(..., ge=0, description="Total charges to date")
    avg_monthly_charges: float = Field(..., ge=0, description="Average monthly charges")
    charge_velocity: float = Field(..., description="Change in charges over time")

    # Contract & Billing
    contract_type: str = Field(
        ..., description="Contract type: Month-to-month, One year, or Two year"
    )
    is_paperless_billing: bool = Field(
        ..., description="Whether using paperless billing"
    )
    payment_method: str = Field(..., description="Payment method")
    is_month_to_month: bool = Field(
        ..., description="Whether on month-to-month contract"
    )
    is_electronic_payment: bool = Field(
        ..., description="Whether using electronic payment"
    )

    # Services
    has_phone_service: bool = Field(..., description="Whether has phone service")
    internet_service: str = Field(..., description="Internet service type")
    has_internet_service: bool = Field(..., description="Whether has internet service")
    has_fiber_optic: bool = Field(..., description="Whether has fiber optic internet")
    online_security: str = Field(..., description="Online security status")
    online_backup: str = Field(..., description="Online backup status")
    device_protection: str = Field(..., description="Device protection status")
    tech_support: str = Field(..., description="Tech support status")
    streaming_tv: str = Field(..., description="Streaming TV status")
    streaming_movies: str = Field(..., description="Streaming movies status")
    multiple_lines: str = Field(..., description="Multiple lines status")

    # Derived features
    total_services_count: int = Field(
        ..., ge=0, le=6, description="Count of additional services"
    )
    has_premium_services: bool = Field(
        ..., description="Whether has any premium services"
    )
    lifetime_value_proxy: float = Field(
        ..., ge=0, description="Estimated lifetime value"
    )
    revenue_per_service: float = Field(..., ge=0, description="Revenue per service")
    is_high_value: bool = Field(..., description="Whether is a high-value customer")
    churn_risk_score: int = Field(
        ..., ge=0, le=20, description="Calculated churn risk score"
    )
    engagement_score: int = Field(
        ..., ge=0, le=20, description="Customer engagement score"
    )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Validate gender field."""
        if v not in ["Male", "Female"]:
            raise ValueError('Gender must be "Male" or "Female"')
        return v

    @field_validator("tenure_group")
    @classmethod
    def validate_tenure_group(cls, v: str) -> str:
        """Validate tenure group field."""
        if v not in ["new", "medium", "long_term"]:
            raise ValueError('Tenure group must be "new", "medium", or "long_term"')
        return v

    @field_validator("contract_type")
    @classmethod
    def validate_contract_type(cls, v: str) -> str:
        """Validate contract type field."""
        if v not in ["Month-to-month", "One year", "Two year"]:
            raise ValueError(
                'Contract type must be "Month-to-month", "One year", or "Two year"'
            )
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "gender": "Female",
                "is_senior_citizen": False,
                "has_partner": True,
                "has_dependents": False,
                "tenure_months": 12,
                "tenure_years": 1.0,
                "tenure_group": "new",
                "monthly_charges": 65.0,
                "total_charges": 780.0,
                "avg_monthly_charges": 65.0,
                "charge_velocity": 0.0,
                "contract_type": "One year",
                "is_paperless_billing": True,
                "payment_method": "Electronic check",
                "is_month_to_month": False,
                "is_electronic_payment": True,
                "has_phone_service": True,
                "internet_service": "Fiber optic",
                "has_internet_service": True,
                "has_fiber_optic": True,
                "online_security": "No",
                "online_backup": "Yes",
                "device_protection": "No",
                "tech_support": "No",
                "streaming_tv": "Yes",
                "streaming_movies": "Yes",
                "multiple_lines": "No",
                "total_services_count": 3,
                "has_premium_services": True,
                "lifetime_value_proxy": 780.0,
                "revenue_per_service": 16.25,
                "is_high_value": False,
                "churn_risk_score": 5,
                "engagement_score": 6,
            }
        }


class PredictionRequest(BaseModel):
    """Request for batch prediction."""

    customers: List[CustomerFeatures] = Field(..., min_length=1, max_length=100)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "customers": [CustomerFeatures.Config.json_schema_extra["example"]]
            }
        }


class ChurnPrediction(BaseModel):
    """Single churn prediction result."""

    customer_index: int = Field(..., description="Index of customer in request")
    churn_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Probability of churn"
    )
    will_churn: bool = Field(..., description="Binary prediction (threshold: 0.5)")
    risk_level: str = Field(..., description="Risk level: low, medium, or high")


class PredictionResponse(BaseModel):
    """Response for batch prediction."""

    predictions: List[ChurnPrediction]
    model_version: str = Field(..., description="Version of the model used")
    total_customers: int = Field(..., description="Number of customers processed")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_version: Optional[str] = Field(None, description="Current model version")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
