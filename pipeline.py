"""Command-line entry point for the complete MP1 data pipeline."""

import argparse
import logging
import sys

from src import (
    create_cleaning_report,
    load_data,
    process_data,
    save_data,
    setup_logging,
    validate_dataframe,
    validate_input,
)


def parse_arguments():
    """Parse command-line arguments."""
    # These options let the same program work with different files and settings.
    parser = argparse.ArgumentParser(
        description="Data processing pipeline"
    )

    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--verbose", "-v", action="store_true")

    return parser.parse_args()


def main():
    """Main pipeline function."""
    args = parse_arguments()
    setup_logging(args.verbose)

    logging.getLogger(__name__).debug(
        "Arguments parsed: input=%s, config=%s, output=%s",
        args.input,
        args.config,
        args.output,
    )

    # Check both paths first so a missing file gets a clear message before loading.
    input_valid = validate_input(args.input)
    config_valid = validate_input(args.config)
    if not input_valid or not config_valid:
        sys.exit(1)

    try:
        # The file endings tell load_data whether to use the CSV or YAML loader.
        data = load_data(args.input)
        config = load_data(args.config)
    except ValueError:
        sys.exit(1)

    # The config lists which columns must exist and which columns should be numbers.
    validation = config["validation"]
    rows_before_validation = len(data)
    try:
        validated_data = validate_dataframe(
            data,
            required_columns=validation["required_columns"],
            numeric_columns=validation["numeric_columns"],
        )
    except ValueError:
        sys.exit(1)
    logger = logging.getLogger(__name__)
    logger.info(
        "Validation complete: %s -> %s rows",
        rows_before_validation,
        len(validated_data),
    )

    # Save the validated data so the report measures cleaning, not validation.
    data_before_processing = validated_data.copy()
    try:
        cleaned_data = process_data(validated_data, config)
    except ValueError:
        sys.exit(1)

    report = create_cleaning_report(data_before_processing, cleaned_data)
    logger.info(
        "Processing complete: %s -> %s rows",
        report["rows_before"],
        report["rows_after"],
    )

    save_data(cleaned_data, args.output)
    logger.info("Saved cleaned data to %s", args.output)

    print("\nCleaning report:")
    print(report)


if __name__ == "__main__":
    main()