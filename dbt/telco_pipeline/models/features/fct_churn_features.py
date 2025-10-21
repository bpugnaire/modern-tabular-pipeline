import polars as pl


def model(dbt, session):
    """
    Feature engineering model for churn prediction.
    Creates derived features from the staging table using Polars.
    """
    # Load the staging table - dbt-duckdb returns a DuckDBPyRelation
    stg_churn = dbt.ref("stg_churn")

    # Convert to Polars DataFrame via Arrow
    df = pl.from_arrow(stg_churn.arrow())

    # Feature Engineering
    features = df.select(
        [
            # Original columns
            pl.col("customer_id"),
            pl.col("has_churned"),
            # Demographics features
            pl.col("gender"),
            pl.col("is_senior_citizen"),
            pl.col("has_partner"),
            pl.col("has_dependents"),
            # Tenure-based features
            pl.col("tenure_months"),
            (pl.col("tenure_months") / 12).alias("tenure_years"),
            pl.when(pl.col("tenure_months") <= 12)
            .then(pl.lit("new"))
            .when(pl.col("tenure_months") <= 36)
            .then(pl.lit("medium"))
            .otherwise(pl.lit("long_term"))
            .alias("tenure_group"),
            # Financial features
            pl.col("monthly_charges"),
            pl.col("total_charges"),
            # Average charges per month (handling nulls for new customers)
            (pl.col("total_charges") / pl.col("tenure_months"))
            .fill_null(pl.col("monthly_charges"))
            .alias("avg_monthly_charges"),
            # Revenue velocity (difference between current and average)
            (
                pl.col("monthly_charges")
                - (pl.col("total_charges") / pl.col("tenure_months"))
            )
            .fill_null(0)
            .alias("charge_velocity"),
            # Contract & Billing features
            pl.col("contract_type"),
            pl.col("is_paperless_billing"),
            pl.col("payment_method"),
            # Contract risk indicator
            pl.when(pl.col("contract_type") == "Month-to-month")
            .then(pl.lit(True))
            .otherwise(pl.lit(False))
            .alias("is_month_to_month"),
            # Electronic payment indicator
            pl.when(pl.col("payment_method").str.contains("Electronic"))
            .then(pl.lit(True))
            .otherwise(pl.lit(False))
            .alias("is_electronic_payment"),
            # Service features
            pl.col("has_phone_service"),
            pl.col("internet_service"),
            # Internet service indicator
            pl.when(pl.col("internet_service") == "No")
            .then(pl.lit(False))
            .otherwise(pl.lit(True))
            .alias("has_internet_service"),
            # Fiber optic indicator (premium service)
            pl.when(pl.col("internet_service") == "Fiber optic")
            .then(pl.lit(True))
            .otherwise(pl.lit(False))
            .alias("has_fiber_optic"),
            # Additional services
            pl.col("online_security"),
            pl.col("online_backup"),
            pl.col("device_protection"),
            pl.col("tech_support"),
            pl.col("streaming_tv"),
            pl.col("streaming_movies"),
            pl.col("multiple_lines"),
        ]
    )

    # Count total services subscribed
    service_cols = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
    ]

    # Create service count feature
    features = features.with_columns(
        [
            pl.sum_horizontal(
                [
                    pl.when(pl.col(col) == "Yes").then(1).otherwise(0)
                    for col in service_cols
                ]
            ).alias("total_services_count"),
            # Has any premium services
            pl.when(pl.any_horizontal([pl.col(col) == "Yes" for col in service_cols]))
            .then(pl.lit(True))
            .otherwise(pl.lit(False))
            .alias("has_premium_services"),
        ]
    )

    # Customer lifetime value proxy
    features = features.with_columns(
        [
            (pl.col("monthly_charges") * pl.col("tenure_months")).alias(
                "lifetime_value_proxy"
            ),
            # Revenue per service (efficiency metric)
            (pl.col("monthly_charges") / (pl.col("total_services_count") + 1)).alias(
                "revenue_per_service"
            ),
            # High value customer indicator
            pl.when(pl.col("monthly_charges") > pl.col("monthly_charges").median())
            .then(pl.lit(True))
            .otherwise(pl.lit(False))
            .alias("is_high_value"),
        ]
    )

    # Churn risk indicators
    features = features.with_columns(
        [
            # Risk score based on known churn patterns
            (
                (pl.col("is_month_to_month").cast(pl.Int8) * 3)
                + (pl.col("has_fiber_optic").cast(pl.Int8) * 2)
                + ((pl.col("tenure_months") < 12).cast(pl.Int8) * 2)
                + ((pl.col("total_services_count") == 0).cast(pl.Int8) * 2)
                + (pl.col("is_paperless_billing").cast(pl.Int8) * 1)
            ).alias("churn_risk_score"),
            # Engagement score (positive indicator)
            (
                (pl.col("has_partner").cast(pl.Int8) * 1)
                + (pl.col("has_dependents").cast(pl.Int8) * 1)
                + (pl.col("total_services_count") * 1)
                + ((pl.col("tenure_months") >= 24).cast(pl.Int8) * 2)
            ).alias("engagement_score"),
        ]
    )

    return features.to_arrow()
