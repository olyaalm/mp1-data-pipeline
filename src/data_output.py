"""Functions for writing processed data to disk."""

import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def save_data(df, filepath):
    """Save a DataFrame as CSV and return its output path."""
    # Turning the output name into a path
    path = Path(filepath)
    # Creating any output folders that are missing
    path.parent.mkdir(parents=True, exist_ok=True)
    # Writing the table to CSV without the row index
    df.to_csv(path, index=False)
    logger.debug("Saved %s rows to %s", len(df), path)
    return path
