"""Functions for writing processed data to disk."""

import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def save_data(df, filepath):
    """Save a DataFrame as CSV and return its output path."""
    path = Path(filepath)
    # Create missing folders so output paths such as output/clean.csv work on a new checkout.
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.debug("Saved %s rows to %s", len(df), path)
    return path
