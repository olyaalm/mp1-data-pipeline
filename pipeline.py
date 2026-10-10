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

from data_loaders import load_data
from data_processor import create_cleaning_report, process_data


logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    """Configure logging for the pipeline."""
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
    if Path(filepath).is_file():
        logger.info("Input file validated: %s", filepath)
        return True

    logger.error("Input file not found: %s", filepath)
    return False


def main():
    """Main pipeline function."""
    args = parse_arguments()
    setup_logging(args.verbose)

    logger.debug(
        "Arguments parsed: input=%s, config=%s, output=%s",
        args.input,
        args.config,
        args.output,
    )

    input_valid = validate_input(args.input)
    config_valid = validate_input(args.config)
    if not input_valid or not config_valid:
        sys.exit(1)

    try:
        data = load_data(args.input)
        config = load_data(args.config)
    except ValueError:
        sys.exit(1)

    original_data = data.copy()
    try:
        cleaned_data = process_data(data, config)
    except ValueError:
        sys.exit(1)

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