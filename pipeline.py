"""
Data Processing Pipeline - CLI Template

DS 3500 - MP1

Usage:
    python pipeline.py --input data.csv --output clean.csv
    python pipeline.py --input data.csv --output results.json --format json --verbose
"""

import argparse
import logging
import sys
from pathlib import Path

from data_loaders import load_data


logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    """Configure logging for the pipeline."""
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Data processing pipeline"
    )

    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
    )
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
        "Arguments parsed: input=%s, output=%s, format=%s",
        args.input,
        args.output,
        args.format,
    )

    if not validate_input(args.input):
        sys.exit(1)

    try:
        data = load_data(args.input)
    except ValueError:
        sys.exit(1)


if __name__ == "__main__":
    main()