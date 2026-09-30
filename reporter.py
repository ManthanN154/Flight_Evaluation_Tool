"""
reporter.py
Module 3: Output & Reporting Generator

Formats processed flight data into readable terminal tables and
saves structured CSV/JSON report files.
"""

import csv
import json
import os
from datetime import datetime


def print_table(records, max_rows=20):
    """
    Prints a simple readable table of flight records to the terminal.
    Only shows up to 'max_rows' records to avoid flooding the console.
    """
    if not records:
        print("No records to display.")
        return

    headers = [
        "flight_id", "time_of_flight", "max_altitude",
        "average_altitude", "range", "average_speed", "anomaly",
    ]
    col_widths = {h: max(len(h), 10) for h in headers}

    header_row = " | ".join(h.ljust(col_widths[h]) for h in headers)
    print("\n" + header_row)
    print("-" * len(header_row))

    for record in records[:max_rows]:
        row_values = []
        for h in headers:
            value = record.get(h, "")
            if isinstance(value, float):
                value = f"{value:.2f}"
            row_values.append(str(value).ljust(col_widths[h]))
        print(" | ".join(row_values))

    if len(records) > max_rows:
        print(f"... ({len(records) - max_rows} more rows not shown)")


def print_summary(summary):
    """
    Prints the summary statistics dict in a readable format.
    """
    print("\n===== FLIGHT DATA SUMMARY =====")
    print(f"Total flights processed: {summary['total_flights']}")
    print(f"Anomalies detected:      {summary['anomalies_detected']}")

    if summary["metrics"]:
        print(f"\n{'Metric':<20}{'Min':>10}{'Max':>10}{'Avg':>10}")
        print("-" * 50)
        for metric, stats in summary["metrics"].items():
            print(
                f"{metric:<20}{stats['min']:>10}{stats['max']:>10}"
                f"{stats['avg']:>10}"
            )
    print("================================\n")


def save_csv_report(records, output_dir, logger):
    """
    Saves the processed flight records to a CSV file in output_dir.
    Returns the path of the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"flight_report_{timestamp}.csv")

    if not records:
        logger.warning("No records to save to CSV")
        return None

    headers = [
        "flight_id", "time_of_flight", "max_altitude",
        "average_altitude", "range", "average_speed",
        "expected_speed", "anomaly",
    ]

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for record in records:
                writer.writerow({h: record.get(h, "") for h in headers})
        logger.info(f"CSV report saved: {filepath}")
        return filepath
    except OSError as e:
        logger.error(f"Failed to save CSV report: {e}")
        return None


def save_json_report(records, summary, output_dir, logger):
    """
    Saves both the records and the summary into a single JSON report.
    Returns the path of the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"flight_report_{timestamp}.json")

    report_data = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "records": records,
    }

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        logger.info(f"JSON report saved: {filepath}")
        return filepath
    except OSError as e:
        logger.error(f"Failed to save JSON report: {e}")
        return None
