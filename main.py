"""
main.py
Entry point for the Flight Landing Data Evaluation CLI.

Ties together ingestion -> processing -> reporting in a sequential
workflow, with basic argparse CLI options.
"""

import argparse
import time
import sys

from logger import setup_logger
from ingestion import load_from_csv, load_from_json, get_manual_input
from processor import process_batch, compute_summary
from reporter import print_table, print_summary, save_csv_report, save_json_report


def build_parser():
    """Builds and returns the argparse CLI parser."""
    parser = argparse.ArgumentParser(
        prog="flight_eval",
        description=(
            "Flight Landing Data Evaluation CLI - analyzes post-landing "
            "flight metrics (time of flight, altitude, range, speed)."
        ),
        epilog=(
            "Examples:\n"
            "  python main.py --csv sample_data/flights_sample.csv\n"
            "  python main.py --json data/flights.json --batch-size 100\n"
            "  python main.py --manual\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--csv", metavar="FILE", help="Path to a CSV file of flight data"
    )
    source.add_argument(
        "--json", metavar="FILE", help="Path to a JSON file of flight data"
    )
    source.add_argument(
        "--manual", action="store_true",
        help="Enter one flight record manually via prompts"
    )

    parser.add_argument(
        "--batch-size", type=int, default=50,
        help="Number of records processed per batch (default: 50)"
    )
    parser.add_argument(
        "--output-dir", default="output",
        help="Directory to save report files (default: ./output)"
    )
    parser.add_argument(
        "--max-rows", type=int, default=20,
        help="Max rows to display in the terminal table (default: 20)"
    )

    return parser


def run_pipeline(args, logger):
    """
    Runs the full ingest -> process -> report pipeline based on
    the source chosen (csv, json, or manual).
    """
    all_processed = []

    if args.manual:
        logger.info("Starting manual data entry")
        record = get_manual_input(logger)
        if record:
            batch = process_batch([record], logger)
            all_processed.extend(batch)
        else:
            logger.warning("Manual entry produced no valid record")

    elif args.csv:
        logger.info(f"Loading flight data from CSV: {args.csv}")
        try:
            for batch_num, batch in enumerate(
                load_from_csv(args.csv, logger, args.batch_size), start=1
            ):
                logger.info(f"Processing batch {batch_num} ({len(batch)} records)")
                processed = process_batch(batch, logger)
                all_processed.extend(processed)
        except FileNotFoundError as e:
            logger.error(f"Failed to load CSV: {e}")
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error loading CSV: {e}")
            print(f"Error: {e}")
            sys.exit(1)

    elif args.json:
        logger.info(f"Loading flight data from JSON: {args.json}")
        try:
            for batch_num, batch in enumerate(
                load_from_json(args.json, logger, args.batch_size), start=1
            ):
                logger.info(f"Processing batch {batch_num} ({len(batch)} records)")
                processed = process_batch(batch, logger)
                all_processed.extend(processed)
        except FileNotFoundError as e:
            logger.error(f"Failed to load JSON: {e}")
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error loading JSON: {e}")
            print(f"Error: {e}")
            sys.exit(1)

    return all_processed


def main():
    parser = build_parser()
    args = parser.parse_args()

    logger = setup_logger()
    logger.info("===== Flight Evaluation CLI started =====")

    start_time = time.time()

    all_processed = run_pipeline(args, logger)

    if not all_processed:
        print("No valid flight records were processed. Check app.log for details.")
        logger.warning("Pipeline finished with zero valid records")
        sys.exit(0)

    summary = compute_summary(all_processed, logger)

    # Module 3: Output
    print_table(all_processed, max_rows=args.max_rows)
    print_summary(summary)

    csv_path = save_csv_report(all_processed, args.output_dir, logger)
    json_path = save_json_report(all_processed, summary, args.output_dir, logger)

    elapsed = time.time() - start_time
    print(f"CSV report saved to:  {csv_path}")
    print(f"JSON report saved to: {json_path}")
    print(f"Execution time: {elapsed:.3f} seconds")

    logger.info(f"Execution completed in {elapsed:.3f} seconds")
    logger.info("===== Flight Evaluation CLI finished =====")


if __name__ == "__main__":
    main()
