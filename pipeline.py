"""Command-line entry point for the complete MP1 data pipeline."""

import argparse
import logging
import math
import sys

import pandas as pd

from src import (
    create_cleaning_report,
    load_data,
    process_data,
    save_data,
    setup_logging,
    validate_dataframe,
    validate_input,
)


def validate_config(config):
    """Check that the config has the sections and settings used by the pipeline."""
    if not isinstance(config, dict):
        raise ValueError("Configuration must contain a YAML mapping")

    validation = config.get("validation")
    if not isinstance(validation, dict):
        raise ValueError("Configuration must include a validation mapping")

    for key in ("required_columns", "numeric_columns"):
        columns = validation.get(key)
        if not isinstance(columns, list) or any(
            not isinstance(column, str) for column in columns
        ):
            raise ValueError(f"validation.{key} must be a list of column names")

    processing = config.get("processing")
    if not isinstance(processing, dict):
        raise ValueError("Configuration must include a processing mapping")

    remove_duplicates = processing.get("remove_duplicates", False)
    if not isinstance(remove_duplicates, bool):
        raise ValueError("processing.remove_duplicates must be true or false")

    missing = processing.get("missing", {})
    if not isinstance(missing, dict):
        raise ValueError("processing.missing must be a mapping")
    missing_enabled = missing.get("enabled", False)
    if not isinstance(missing_enabled, bool):
        raise ValueError("processing.missing.enabled must be true or false")
    axis = missing.get("axis")
    if missing_enabled and (
        not isinstance(axis, str) or axis not in {"rows", "columns"}
    ):
        raise ValueError("Enabled missing-value handling needs axis rows or columns")

    outliers = processing.get("outliers", {})
    if not isinstance(outliers, dict):
        raise ValueError("processing.outliers must be a mapping")
    outliers_enabled = outliers.get("enabled", False)
    if not isinstance(outliers_enabled, bool):
        raise ValueError("processing.outliers.enabled must be true or false")
    if outliers_enabled:
        columns = outliers.get("columns")
        method = outliers.get("method")
        threshold = outliers.get("threshold")
        if not isinstance(columns, list) or any(
            not isinstance(column, str) for column in columns
        ):
            raise ValueError("Enabled outlier removal needs a list of column names")
        if not isinstance(method, str) or method not in {"iqr", "zscore"}:
            raise ValueError("Outlier method must be iqr or zscore")
        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or not math.isfinite(threshold)
            or threshold < 0
        ):
            raise ValueError("Outlier threshold must be a finite non-negative number")


def parse_arguments():
    """Parse command-line arguments."""

    # Creating the parser that reads options typed after the script name
    parser = argparse.ArgumentParser(
        description="Data processing pipeline"
    )

    # Reading the data, config, and output paths from the command line
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", "-o", required=True)

    # Turning on detailed log messages when requested
    parser.add_argument("--verbose", "-v", action="store_true")

    # Returning the values entered by the user
    return parser.parse_args()


def main():
    """Main pipeline function."""

    # Reading command-line choices and setting the log level
    args = parse_arguments()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Showing the selected paths when detailed logging is turned on
    logger.debug(
        "Arguments parsed: input=%s, config=%s, output=%s",
        args.input,
        args.config,
        args.output,
    )

    # Checking both paths before loading either file
    input_valid = validate_input(args.input)
    config_valid = validate_input(args.config)

    # Leaving with an error code when either file is missing
    if not input_valid or not config_valid:
        sys.exit(1)

    # Loading the data file and its YAML settings
    try:
        data = load_data(args.input)
        config = load_data(args.config)
    except (OSError, ValueError) as error:
        logger.error("Unable to load input or config: %s", error)

        # Leaving with an error code when a file format is not supported
        sys.exit(1)

    if not isinstance(data, pd.DataFrame):
        logger.error("Input data must be a CSV file containing a table")
        sys.exit(1)

    try:
        validate_config(config)
    except ValueError as error:
        logger.error("Invalid configuration: %s", error)
        sys.exit(1)

    # Reading required and numeric column names from the config
    validation = config["validation"]

    # Counting input rows before checking required and numeric columns
    rows_before_validation = len(data)

    # Checking the configured columns and removing invalid numeric values
    try:
        validated_data = validate_dataframe(
            data,
            required_columns=validation["required_columns"],
            numeric_columns=validation["numeric_columns"],
        )
    except ValueError as error:

        # Leaving with an error code when the table fails validation
        logger.error("Data validation failed: %s", error)
        sys.exit(1)

    # Reporting how many rows passed validation
    logger.info(
        "Validation complete: %s -> %s rows",
        rows_before_validation,
        len(validated_data),
    )

    # Copying validated rows before measuring changes from cleaning
    data_before_processing = validated_data.copy()

    # Cleaning the validated table using the enabled config steps
    try:
        cleaned_data = process_data(validated_data, config)
    except ValueError as error:

        # Leaving with an error code when a cleaning setting is not supported
        logger.error("Data processing failed: %s", error)
        sys.exit(1)

    # Counting rows and columns changed by the cleaning steps
    report = create_cleaning_report(data_before_processing, cleaned_data)

    # Reporting the number of rows before and after cleaning
    logger.info(
        "Processing complete: %s -> %s rows",
        report["rows_before"],
        report["rows_after"],
    )

    # Saving the cleaned table at the output path
    try:
        save_data(cleaned_data, args.output)
    except OSError as error:
        logger.error("Unable to save output file: %s", error)
        sys.exit(1)
    logger.info("Saved cleaned data to %s", args.output)

    if cleaned_data.empty:
        logger.warning("Cleaning finished with no rows remaining")

    # Printing the final row and column counts
    print("\nCleaning report:")
    print(report)

# Running the pipeline only when this file is started directly
if __name__ == "__main__":
    main()
