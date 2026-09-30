"""
ingestion.py
Module 1: Data Ingestion & Validation

Handles reading raw flight data from CSV, JSON, or manual CLI entry.
Validates each record and yields clean data in small batches so large
files do not need to be loaded fully into memory at once.
"""

import csv
import json
import os

# fields every flight record must contain
REQUIRED_FIELDS = [
    "flight_id",
    "time_of_flight",
    "max_altitude",
    "average_altitude",
    "range",
    "average_speed",
]

# numeric fields that must convert to float
NUMERIC_FIELDS = [
    "time_of_flight",
    "max_altitude",
    "average_altitude",
    "range",
    "average_speed",
]


def validate_row(row, logger, row_number=None):
    """
    Validates a single row (dict) of flight data.
    Returns a cleaned dict if valid, or None if the row should be skipped.
    """
    location = f"row {row_number}" if row_number is not None else "manual entry"

    # check all required fields are present
    for field in REQUIRED_FIELDS:
        if field not in row or row[field] in (None, ""):
            logger.warning(f"Skipping {location}: missing field '{field}'")
            return None

    cleaned = {"flight_id": str(row["flight_id"]).strip()}

    # try to convert numeric fields, skip row if any conversion fails
    for field in NUMERIC_FIELDS:
        try:
            value = float(row[field])
            if value < 0:
                logger.warning(
                    f"Skipping {location}: negative value in '{field}'"
                )
                return None
            cleaned[field] = value
        except (ValueError, TypeError):
            logger.warning(
                f"Skipping {location}: '{field}' is not a valid number "
                f"(got '{row[field]}')"
            )
            return None

    return cleaned


def load_from_csv(filepath, logger, batch_size=50):
    """
    Reads flight data from a CSV file in small batches (generator).
    Yields a list of validated records each time (a 'batch').
    This keeps memory usage low even for large files.
    """
    if not os.path.exists(filepath):
        logger.error(f"CSV file not found: {filepath}")
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    batch = []
    row_number = 0

    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_number += 1
                cleaned = validate_row(row, logger, row_number)
                if cleaned:
                    batch.append(cleaned)

                # once batch is full, yield it and start a new one
                if len(batch) >= batch_size:
                    yield batch
                    batch = []

        # yield any leftover rows that didn't fill a full batch
        if batch:
            yield batch

    except csv.Error as e:
        logger.error(f"CSV parsing error: {e}")
        raise


def load_from_json(filepath, logger, batch_size=50):
    """
    Reads flight data from a JSON file (expects a list of objects).
    Yields validated records in batches, same as load_from_csv.
    """
    if not os.path.exists(filepath):
        logger.error(f"JSON file not found: {filepath}")
        raise FileNotFoundError(f"JSON file not found: {filepath}")

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        raise

    if not isinstance(data, list):
        logger.error("JSON file must contain a list of flight records")
        raise ValueError("JSON root element must be a list")

    batch = []
    for i, row in enumerate(data, start=1):
        cleaned = validate_row(row, logger, i)
        if cleaned:
            batch.append(cleaned)
        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch


def get_manual_input(logger):
    """
    Prompts the user in the terminal to type in one flight record.
    Returns a validated dict, or None if input was invalid.
    """
    print("\nEnter flight data (press Ctrl+C to cancel):")
    raw = {}
    try:
        raw["flight_id"] = input("Flight ID: ").strip()
        raw["time_of_flight"] = input("Time of flight (seconds): ").strip()
        raw["max_altitude"] = input("Max altitude (meters): ").strip()
        raw["average_altitude"] = input("Average altitude (meters): ").strip()
        raw["range"] = input("Range (meters): ").strip()
        raw["average_speed"] = input("Average speed (m/s): ").strip()
    except KeyboardInterrupt:
        print("\nManual entry cancelled.")
        return None

    return validate_row(raw, logger)
