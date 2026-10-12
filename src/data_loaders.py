"""Load data files in supported formats."""

import json
import logging
from pathlib import Path

import pandas as pd
import yaml


# Using this module's name in log messages to show where each load is coming from.
logger = logging.getLogger(__name__)


def load_csv(filepath):
    """Load a CSV file into a pandas DataFrame."""
    # Loading CSV inputs as DataFrames for the processing pipeline.
    data = pd.read_csv(filepath)
    logger.info("Loaded CSV file: %s (%s rows)", filepath, len(data))
    return data


def load_json(filepath):
    """Load a JSON file into a Python object."""
    # Reading text-based JSON files using UTF-8 encoding.
    with filepath.open(encoding="utf-8") as file:
        data = json.load(file)
    logger.info("Loaded JSON file: %s", filepath)
    return data


def load_yaml(filepath):
    """Load a YAML file into a Python object."""
    # Parsing YAML safely without constructing arbitrary Python objects.
    with filepath.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)
    logger.info("Loaded YAML file: %s", filepath)
    return data


def load_data(filepath):
    """Load a file using the loader that matches its extension."""
    # Normalizing the suffix to make extension matching case-insensitive.
    path = Path(filepath)
    extension = path.suffix.lower()
    loaders = {
        ".csv": load_csv,
        ".json": load_json,
        ".yaml": load_yaml,
    }

    # Rejecting unsupported formats instead of silently returning invalid data.
    loader = loaders.get(extension)
    if loader is None:
        logger.error("Unsupported file format: %s", extension)
        raise ValueError(f"Unsupported file format: {extension}")

    return loader(path)
