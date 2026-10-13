"""Shared logging and input-path utilities for the pipeline."""

import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    """Configure pipeline logging at the requested detail level."""

    # Choosing detailed messages or normal progress messages
    level = logging.DEBUG if verbose else logging.INFO

    # Setting the level and layout used by every pipeline module
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def validate_input(filepath):
    """Return whether filepath exists and is a regular file."""

    # Checking that the path points to a file
    if Path(filepath).is_file():
        logger.info("Input file validated: %s", filepath)
        return True

    logger.error("Input file not found: %s", filepath)
    return False
