# Project Statement: Flight Landing Data Evaluation CLI

## 1. Problem Statement

After a flight lands, raw telemetry summarizing its performance
(time of flight, maximum altitude, average altitude, range, and
average speed) needs to be collected, validated, and analyzed to
produce a trustworthy, human-readable evaluation. Manually reviewing
this data is slow and error-prone, especially across many flights.
This project delivers a command-line application that automates
ingestion, validation, processing, and reporting of this data,
producing both terminal-friendly summaries and structured report
files (CSV/JSON) for later use.

## 2. Input Specification

Each flight record must contain the following fields:

| Field              | Type  | Unit    | Description                          |
|---------------------|-------|---------|---------------------------------------|
| flight_id           | str   | -       | Unique identifier for the flight      |
| time_of_flight       | float | seconds | Total duration of the flight          |
| max_altitude        | float | meters  | Highest altitude reached              |
| average_altitude    | float | meters  | Mean altitude across the flight       |
| range               | float | meters  | Total horizontal distance covered     |
| average_speed       | float | m/s     | Mean speed across the flight          |

Accepted input sources:
- **CSV file** (`--csv path/to/file.csv`) with the above columns as headers.
- **JSON file** (`--json path/to/file.json`) containing a list of objects with the above keys.
- **Manual CLI entry** (`--manual`) — one record entered interactively.

Invalid rows (missing fields, non-numeric values, negative numbers) are
skipped with a logged warning rather than stopping the whole run.

## 3. Output Specification

### Terminal Output
- A readable, aligned table of all processed flight records (flight_id,
  metrics, and an `anomaly` flag), capped at `--max-rows` rows for readability.
- A summary block showing total flights processed, anomalies detected,
  and min/max/avg for each metric.
- Total execution time in seconds.

### File Output
- **CSV report** (`output/flight_report_<timestamp>.csv`): one row per
  flight including derived `expected_speed` and `anomaly` fields.
- **JSON report** (`output/flight_report_<timestamp>.json`): contains
  `generated_at` timestamp, the full `summary` object, and the full list
  of processed `records`.
- **app.log**: persistent log of every run (info/warning/error level events).

## 4. Functional Module Breakdown

### Module 1 — Data Ingestion & Validation (`ingestion.py`)
- Reads raw data from CSV, JSON, or manual CLI prompts.
- Validates required fields are present and numeric fields convert
  correctly and are non-negative.
- Streams data in fixed-size batches via generator functions so large
  files do not need to be fully loaded into memory.
- Logs a warning and skips any row that fails validation.

### Module 2 — Processing Engine (`processor.py`)
- Cross-checks reported `average_speed` against an expected speed
  calculated as `range / time_of_flight`.
- Flags records as anomalous if the discrepancy exceeds a 20% tolerance,
  or if `time_of_flight` is zero (division-by-zero guard).
- Aggregates all processed records into summary statistics: count,
  min, max, and average for each numeric metric, plus total anomaly count.

### Module 3 — Output & Reporting Generator (`reporter.py`)
- Prints a formatted table of individual flight records to the terminal.
- Prints a formatted summary statistics block to the terminal.
- Saves a detailed CSV report and a combined JSON report (records + summary)
  to the configured output directory, each timestamped to avoid overwrites.

### Supporting Module — Logging (`logger.py`)
- Central logger configuration shared by all modules.
- Writes DEBUG-and-above messages to `app.log`.
- Prints WARNING-and-above messages to the console for immediate visibility.

### Orchestration (`main.py`)
- Parses CLI arguments (`argparse`) for input source, batch size,
  output directory, and display row limit.
- Runs the sequential pipeline: **Input → Validation → Transformation →
  Analysis → Output Generation**.
- Measures and reports total execution time.

## 5. Logical Workflow Summary

```
 [CLI Args] 
     |
     v
 [Module 1: Ingestion & Validation]
     - read CSV / JSON / manual input
     - validate each row
     - yield clean records in batches
     |
     v
 [Module 2: Processing Engine]
     - compute expected speed per flight
     - flag anomalies
     - aggregate summary statistics
     |
     v
 [Module 3: Output & Reporting]
     - print table + summary to terminal
     - save CSV report
     - save JSON report
     |
     v
 [app.log updated throughout] + [Execution time printed]
```
