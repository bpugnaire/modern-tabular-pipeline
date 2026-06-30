"""FastAPI application for churn prediction."""

import os
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .model_service import get_model_service
from .schemas import (
    ChurnPrediction,
    CustomerFeatures,
    ErrorResponse,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Load model
    print("Starting up...")
    model_service = get_model_service()

    model_uri = os.getenv("MODEL_URI")
    model_path = os.getenv("MODEL_PATH")

    try:
        if model_uri:
            model_service.load_model(model_uri)
        elif model_path:
            model_service.load_model_from_file(model_path)
        else:
            print(
                "⚠️  No MODEL_URI or MODEL_PATH provided. Model must be loaded manually."
            )
    except Exception as e:
        print(f"⚠️  Failed to load model: {e}")
        print("   Service will start but predictions will fail until model is loaded.")

    yield

    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Churn Prediction API",
    description="API for predicting customer churn using CatBoost model",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Churn Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "predict_single": "/predict/single",
            "docs": "/docs",
        },
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    model_service = get_model_service()

    return HealthResponse(
        status="healthy" if model_service.is_loaded() else "degraded",
        model_loaded=model_service.is_loaded(),
        model_version=model_service.get_version(),
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_batch(request: PredictionRequest):
    """Predict churn for a batch of customers.

    Args:
        request: Batch prediction request with customer features

    Returns:
        Prediction response with churn probabilities and risk levels
    """
    model_service = get_model_service()

    if not model_service.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please check service configuration.",
        )

    try:
        # Convert customers to DataFrame
        customers_data = [customer.model_dump() for customer in request.customers]
        features_df = pd.DataFrame(customers_data)

        # Make predictions
        predictions, probabilities = model_service.predict(features_df)

        # Format results
        results = []
        for idx, (pred, prob) in enumerate(zip(predictions, probabilities)):
            results.append(
                ChurnPrediction(
                    customer_index=idx,
                    churn_probability=float(prob),
                    will_churn=bool(pred),
                    risk_level=model_service.get_risk_level(float(prob)),
                )
            )

        return PredictionResponse(
            predictions=results,
            model_version=model_service.get_version() or "unknown",
            total_customers=len(request.customers),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}",
        )


@app.post("/predict/single", response_model=ChurnPrediction)
async def predict_single(customer: CustomerFeatures):
    """Predict churn for a single customer.

    Args:
        customer: Customer features

    Returns:
        Prediction with churn probability and risk level
    """
    model_service = get_model_service()

    if not model_service.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please check service configuration.",
        )

    try:
        # Make prediction
        prediction, probability = model_service.predict_single(customer.model_dump())

        return ChurnPrediction(
            customer_index=0,
            churn_probability=float(probability),
            will_churn=bool(prediction),
            risk_level=model_service.get_risk_level(float(probability)),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}",
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
        ).model_dump(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
