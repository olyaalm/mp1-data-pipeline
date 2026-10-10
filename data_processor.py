"""Reusable data-cleaning operations for tabular datasets."""

import logging

import pandas as pd


logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    cleaned = df.drop_duplicates()
    logger.debug("remove_duplicates: %s -> %s rows", len(df), len(cleaned))
    return cleaned


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis not in {"rows", "columns"}:
        logger.error("Unsupported missing-value axis: %s", axis)
        raise ValueError(f"Unsupported missing-value axis: {axis}")

    cleaned = df.dropna(axis=0 if axis == "rows" else 1)
    if axis == "rows":
        removed = len(df) - len(cleaned)
    else:
        removed = len(df.columns) - len(cleaned.columns)
    logger.debug("handle_missing (%s): removed %s", axis, removed)
    return cleaned


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in {"iqr", "zscore"}:
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    cleaned = df.copy()
    for column in columns:
        if column not in cleaned.columns:
            logger.warning("Column not found: %s", column)
            continue
        if not pd.api.types.is_numeric_dtype(cleaned[column]):
            logger.warning("Column is not numeric: %s", column)
            continue

        values = cleaned[column]
        if method == "iqr":
            first_quartile = values.quantile(0.25)
            third_quartile = values.quantile(0.75)
            spread = third_quartile - first_quartile
            lower = first_quartile - threshold * spread
            upper = third_quartile + threshold * spread
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
            mean = values.mean()
            standard_deviation = values.std()
            if pd.isna(standard_deviation) or standard_deviation == 0:
                outliers = pd.Series(False, index=cleaned.index)
            else:
                outliers = ((values - mean).abs() / standard_deviation) > threshold
            logger.debug(
                "%s (zscore, threshold=%s): removed=%s",
                column,
                threshold,
                int(outliers.sum()),
            )

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
    settings = config["processing"]
    cleaned = df

    if settings.get("remove_duplicates", False):
        cleaned = remove_duplicates(cleaned)

    missing = settings.get("missing", {})
    if missing.get("enabled", False):
        cleaned = handle_missing(cleaned, axis=missing["axis"])

    outliers = settings.get("outliers", {})
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