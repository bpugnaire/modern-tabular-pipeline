"""Example client for interacting with the Churn Prediction API."""

import json
from typing import Dict, List

import requests


class ChurnPredictionClient:
    """Client for making predictions using the Churn Prediction API."""

    def __init__(self, api_url: str):
        """Initialize client.

        Args:
            api_url: Base URL of the API (e.g., 'http://localhost:8000' or Cloud Run URL)
        """
        self.api_url = api_url.rstrip("/")
        self.session = requests.Session()

    def health_check(self) -> Dict:
        """Check API health status.

        Returns:
            Health status response
        """
        response = self.session.get(f"{self.api_url}/health")
        response.raise_for_status()
        return response.json()

    def predict_single(self, customer: Dict) -> Dict:
        """Predict churn for a single customer.

        Args:
            customer: Customer features dictionary

        Returns:
            Prediction response with churn probability
        """
        response = self.session.post(
            f"{self.api_url}/predict/single",
            json=customer,
        )
        response.raise_for_status()
        return response.json()

    def predict_batch(self, customers: List[Dict]) -> Dict:
        """Predict churn for multiple customers.

        Args:
            customers: List of customer features dictionaries

        Returns:
            Batch prediction response
        """
        response = self.session.post(
            f"{self.api_url}/predict",
            json={"customers": customers},
        )
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close the session."""
        self.session.close()


def main():
    """Example usage of the client."""
    # Initialize client (update with your API URL)
    api_url = "http://localhost:8000"  # or "https://your-api-url.run.app"
    client = ChurnPredictionClient(api_url)

    try:
        # Check health
        print("Checking API health...")
        health = client.health_check()
        print(f"✓ API Status: {health['status']}")
        print(f"  Model Loaded: {health['model_loaded']}")
        print(f"  Model Version: {health.get('model_version', 'N/A')}")
        print()

        # Load sample customer
        with open("examples/sample_customer.json") as f:
            customer = json.load(f)

        # Single prediction
        print("Making single prediction...")
        result = client.predict_single(customer)
        print("✓ Prediction Result:")
        print(f"  Churn Probability: {result['churn_probability']:.2%}")
        print(f"  Will Churn: {result['will_churn']}")
        print(f"  Risk Level: {result['risk_level']}")
        print()

        # Batch prediction
        print("Making batch prediction...")
        with open("examples/sample_batch.json") as f:
            batch = json.load(f)

        batch_result = client.predict_batch(batch["customers"])
        print("✓ Batch Prediction Results:")
        print(f"  Total Customers: {batch_result['total_customers']}")
        print(f"  Model Version: {batch_result['model_version']}")
        print()

        for pred in batch_result["predictions"]:
            print(f"  Customer {pred['customer_index']}:")
            print(f"    - Churn Probability: {pred['churn_probability']:.2%}")
            print(f"    - Risk Level: {pred['risk_level']}")

    except requests.exceptions.RequestException as e:
        print(f"✗ API Error: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
