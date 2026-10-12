"""Validate required columns and numeric values in tabular data."""

import logging

import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Return a copy containing the required columns and valid numeric data."""
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]
    if missing_columns:
        message = f"Required columns are missing: {missing_columns}"
        logger.error(message)
        raise ValueError(message)

    validated = df.copy()
    rows_before = len(validated)

    for column in numeric_columns:
        if column not in validated.columns:
            message = f"Numeric column not found: {column}"
            logger.error(message)
            raise ValueError(message)

        # Keep missing values for the configured missing-data processing step.
        invalid_mask = []
        for value in validated[column]:
            invalid = False
            if pd.notna(value):
                try:
                    float(value)
                except (TypeError, ValueError):
                    invalid = True
            invalid_mask.append(invalid)

        invalid_count = sum(invalid_mask)
        if invalid_count:
            logger.warning(
                "Removed %s rows with invalid numeric values in %s",
                invalid_count,
                column,
            )
            validated = validated.iloc[
                [not invalid for invalid in invalid_mask]
            ].copy()

        # Convert the surviving values to a numeric dtype for later processing.
        validated[column] = pd.to_numeric(validated[column])

    logger.debug(
        "Validation: %s -> %s rows (%s removed)",
        rows_before,
        len(validated),
        rows_before - len(validated),
    )
    return validated
