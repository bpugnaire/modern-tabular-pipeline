{{
    config(
        materialized='table',
        tags=['staging', 'gcs'],
        pre_hook=[
            "CREATE OR REPLACE SECRET gcs_secret (TYPE GCS, KEY_ID '{{ env_var('GCS_KEY_ID') }}', SECRET '{{ env_var('GCS_SECRET') }}')"
        ]
    )
}}

with source_data as (
    select *
    from read_csv_auto(
        'gs://modern-tabular-dev/data/raw/Telco-Customer-Churn.csv',
        header=true,
        delim=',',
        quote='"'
    )
)

select
    -- Primary key
    "customerID" as customer_id,

    -- Demographics
    "gender" as gender,
    cast("SeniorCitizen" as boolean) as is_senior_citizen,
    case
        when "Partner" = 'Yes' then true
        when "Partner" = 'No' then false
        else null
    end as has_partner,
    case
        when "Dependents" = 'Yes' then true
        when "Dependents" = 'No' then false
        else null
    end as has_dependents,

    -- Service information
    cast("tenure" as integer) as tenure_months,

    -- Phone service
    case
        when "PhoneService" = 'Yes' then true
        when "PhoneService" = 'No' then false
        else null
    end as has_phone_service,
    "MultipleLines" as multiple_lines,

    -- Internet service
    "InternetService" as internet_service,
    "OnlineSecurity" as online_security,
    "OnlineBackup" as online_backup,
    "DeviceProtection" as device_protection,
    "TechSupport" as tech_support,
    "StreamingTV" as streaming_tv,
    "StreamingMovies" as streaming_movies,

    -- Contract information
    "Contract" as contract_type,
    case
        when "PaperlessBilling" = 'Yes' then true
        when "PaperlessBilling" = 'No' then false
        else null
    end as is_paperless_billing,
    "PaymentMethod" as payment_method,

    -- Financial
    cast("MonthlyCharges" as decimal(10,2)) as monthly_charges,
    cast(
        case
            when trim("TotalCharges") = '' then null
            when "TotalCharges" = ' ' then null
            else "TotalCharges"
        end as decimal(10,2)
    ) as total_charges,

    -- Target variable
    case
        when "Churn" = 'Yes' then true
        when "Churn" = 'No' then false
        else null
    end as has_churned

from source_data
