"""Validate required columns and numeric values in tabular data."""

import logging

import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Return a copy containing the required columns and valid numeric data."""
    # Finding required column names that are missing from the table
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]
    # Reporting missing required columns and stopping validation
    if missing_columns:
        message = f"Required columns are missing: {missing_columns}"
        logger.error(message)
        raise ValueError(message)

    # Copying the table before changing column types or removing rows
    validated = df.copy()
    # Counting starting rows for the validation log
    rows_before = len(validated)

    # Checking each configured numeric column
    for column in numeric_columns:
        # Checking that the configured numeric column exists
        if column not in validated.columns:
            message = f"Numeric column not found: {column}"
            logger.error(message)
            raise ValueError(message)

        # Marking values that cannot be read as numbers
        invalid_mask = []
        # Checking each value while leaving blank cells for missing-data cleaning
        for value in validated[column]:
            invalid = False
            # Trying to read every non-blank value as a number
            if pd.notna(value):
                try:
                    float(value)
                except (TypeError, ValueError):
                    invalid = True
            invalid_mask.append(invalid)

        # Counting bad values and warning before removing their rows
        invalid_count = sum(invalid_mask)
        if invalid_count:
            logger.warning(
                "Removed %s rows with invalid numeric values in %s",
                invalid_count,
                column,
            )
            # Keeping rows by position so repeated index labels remain safe
            validated = validated.iloc[
                [not invalid for invalid in invalid_mask]
            ].copy()

        # Converting the remaining values to a numeric column
        validated[column] = pd.to_numeric(validated[column])

    # Logging the number of rows kept and removed
    logger.debug(
        "Validation: %s -> %s rows (%s removed)",
        rows_before,
        len(validated),
        rows_before - len(validated),
    )
    return validated
