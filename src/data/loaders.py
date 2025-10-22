"""Data loading utilities."""

from typing import Optional

import polars as pl


def load_features_from_gcs(
    path: str,
    gcs_key_id: Optional[str] = None,
    gcs_secret: Optional[str] = None,
) -> pl.DataFrame:
    """Load features from GCS parquet file.

    Args:
        path: GCS path (gs://...)
        gcs_key_id: GCS access key ID
        gcs_secret: GCS secret key

    Returns:
        Polars DataFrame with features
    """
    storage_options = {}

    if gcs_key_id and gcs_secret:
        storage_options = {
            "gcs_key_id": gcs_key_id,
            "gcs_secret": gcs_secret,
        }

    df = pl.read_parquet(path, storage_options=storage_options)
    return df
