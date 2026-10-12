"""
Data Processing Pipeline - CLI Template

DS 3500 - MP1

Usage:
    python pipeline.py --input data.csv --output clean.csv --config config.yaml
"""

import argparse
import logging
import sys
from pathlib import Path

# Reuse the format-specific loaders and configurable cleaning steps.
from data_loaders import load_data
from data_processor import create_cleaning_report, process_data


logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    """Configure logging for the pipeline."""
    # Verbose mode includes detailed messages from the processing module.
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_arguments():
    """Parse command-line arguments."""
    # Keep file paths and verbosity under command-line control.
    parser = argparse.ArgumentParser(
        description="Data processing pipeline"
    )

    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--verbose", "-v", action="store_true")

    return parser.parse_args()


def validate_input(filepath):
    """Check whether the input path exists and is a file."""
    # Reject missing paths and directories before attempting to load them.
    if Path(filepath).is_file():
        logger.info("Input file validated: %s", filepath)
        return True

    logger.error("Input file not found: %s", filepath)
    return False


def main():
    """Main pipeline function."""
    args = parse_arguments()
    setup_logging(args.verbose)

    # Log the selected paths only in verbose mode.
    logger.debug(
        "Arguments parsed: input=%s, config=%s, output=%s",
        args.input,
        args.config,
        args.output,
    )

    # Both the dataset and its processing configuration must exist.
    input_valid = validate_input(args.input)
    config_valid = validate_input(args.config)
    if not input_valid or not config_valid:
        sys.exit(1)

    try:
        # The file extension selects the appropriate loader for each input.
        data = load_data(args.input)
        config = load_data(args.config)
    except ValueError:
        sys.exit(1)

    # Keep the original dimensions for the final cleaning report.
    original_data = data.copy()
    try:
        # Processing errors are reported by the processor and stop the run.
        cleaned_data = process_data(data, config)
    except ValueError:
        sys.exit(1)

    # Report the changes, then write the cleaned table without row indices.
    report = create_cleaning_report(original_data, cleaned_data)
    print(report)
    logger.info(
        "Processing complete: %s -> %s rows",
        report["rows_before"],
        report["rows_after"],
    )

    cleaned_data.to_csv(args.output, index=False)
    logger.info("Saved cleaned data to %s", args.output)


if __name__ == "__main__":
    main()