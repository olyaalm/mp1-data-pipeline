"""Reusable data-cleaning operations for tabular datasets."""

import logging

import pandas as pd


logger = logging.getLogger(__name__)


# Dropping exact duplicate rows and keeping the first copy
def remove_duplicates(df):
    """Remove duplicate rows."""
    # Dropping rows whose values match across every column
    cleaned = df.drop_duplicates()
    logger.debug("remove_duplicates: %s -> %s rows", len(df), len(cleaned))
    return cleaned


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    # Checking that the requested direction is rows or columns
    if axis not in {"rows", "columns"}:
        logger.error("Unsupported missing-value axis: %s", axis)
        raise ValueError(f"Unsupported missing-value axis: {axis}")

    # Dropping rows or columns that contain any blank value
    cleaned = df.dropna(axis=0 if axis == "rows" else 1)
    # Counting removed rows or columns for the debug message
    if axis == "rows":
        removed = len(df) - len(cleaned)
    else:
        removed = len(df.columns) - len(cleaned.columns)
    logger.debug("handle_missing (%s): removed %s", axis, removed)
    return cleaned


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    # Checking that the method is iqr or zscore
    if method not in {"iqr", "zscore"}:
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    # Copying the table before removing any rows
    cleaned = df.copy()
    # Checking each configured column for values to remove
    for column in columns:
        # Skipping a column when it is not in the table
        if column not in cleaned.columns:
            logger.warning("Column not found: %s", column)
            continue
        # Checking that the column contains numbers
        if not pd.api.types.is_numeric_dtype(cleaned[column]):
            logger.warning("Column is not numeric: %s", column)
            continue

        # Reading the values that are being checked for outliers
        values = cleaned[column]
        # Choosing the requested calculation for this column
        if method == "iqr":
            # Finding the first and third quartiles around the middle half
            first_quartile = values.quantile(0.25)
            third_quartile = values.quantile(0.75)
            # Calculating the range between those two quartiles
            spread = third_quartile - first_quartile
            # Setting the lower limit from the first quartile and threshold
            lower = first_quartile - threshold * spread
            # Setting the upper limit from the third quartile and threshold
            upper = third_quartile + threshold * spread
            # Marking values outside the limits as outliers
            outliers = (values < lower) | (values > upper)
            logger.debug(
                "%s (iqr, threshold=%s): lower=%s, upper=%s, removed=%s",
                column,
                threshold,
                lower,
                upper,
                int(outliers.sum()),
            )
        else:
            # Finding the average and standard deviation for the column
            mean = values.mean()
            standard_deviation = values.std()
            # Checking whether all values are the same
            if pd.isna(standard_deviation) or standard_deviation == 0:
                # Marking no outliers when the column has no spread
                outliers = pd.Series(False, index=cleaned.index)
            else:
                # Marking values farther from the average than the threshold
                outliers = ((values - mean).abs() / standard_deviation) > threshold
            logger.debug(
                "%s (zscore, threshold=%s): removed=%s",
                column,
                threshold,
                int(outliers.sum()),
            )

        # Keeping rows that were not marked as outliers
        cleaned = cleaned.loc[~outliers]

    logger.debug(
        "remove_outliers (%s, threshold=%s): removed %s rows",
        method,
        threshold,
        len(df) - len(cleaned),
    )
    return cleaned


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    # Reading the settings that choose which cleaning steps are running
    settings = config["processing"]
    cleaned = df

    # Removing duplicate rows when that step is enabled
    if settings.get("remove_duplicates", False):
        cleaned = remove_duplicates(cleaned)

    missing = settings.get("missing", {})
    # Removing missing values when that step is enabled
    if missing.get("enabled", False):
        cleaned = handle_missing(cleaned, axis=missing["axis"])

    outliers = settings.get("outliers", {})
    # Removing outliers when that step is enabled
    if outliers.get("enabled", False):
        cleaned = remove_outliers(
            cleaned,
            columns=outliers["columns"],
            method=outliers["method"],
            threshold=outliers["threshold"],
        )

    return cleaned


def create_cleaning_report(df_before, df_after):
    """Return a summary of the rows and columns removed during cleaning."""
    # Counting rows and columns before and after processing
    rows_before = len(df_before)
    rows_after = len(df_after)
    columns_before = len(df_before.columns)
    columns_after = len(df_after.columns)
    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after,
    }