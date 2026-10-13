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


    # Showing the selected paths when detailed logging is turned on
    logging.getLogger(__name__).debug(
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
    except ValueError:

        # Leaving with an error code when a file format is not supported
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
    except ValueError:

        # Leaving with an error code when the table fails validation
        sys.exit(1)
    logger = logging.getLogger(__name__)

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
    except ValueError:

        # Leaving with an error code when a cleaning setting is not supported
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
    save_data(cleaned_data, args.output)
    logger.info("Saved cleaned data to %s", args.output)


    # Printing the final row and column counts
    print("\nCleaning report:")
    print(report)


# Running the pipeline only when this file is started directly
if __name__ == "__main__":
    main()