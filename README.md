# Flight_Evaluation_Tool
A python CLI that can be used to evaluate and store the raw data of recorded flights.
# Flight Landing Data Evaluation CLI

A command-line tool that ingests post-landing flight metrics
(time of flight, max/average altitude, range, average speed),
validates and processes the data, and generates readable reports
in the terminal and as CSV/JSON files.

## Project Structure

```
flight_eval_cli/
├── main.py              # CLI entry point, orchestrates the workflow
├── logger.py            # Logging setup (writes to app.log)
├── ingestion.py         # Module 1: input reading + validation
├── processor.py         # Module 2: metrics + anomaly detection
├── reporter.py          # Module 3: terminal output + saved reports
├── requirements.txt
├── README.md
├── statement.md
└── sample_data/
    └── flights_sample.csv
```

## Setup

### 1. Requirements
- Python 3.8 or higher
- No third-party packages needed (standard library only)

### 2. Create a virtual environment (recommended)

```bash
# Create venv
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# (Optional) install requirements — none needed, but kept for consistency
pip install -r requirements.txt
```

### 3. Run the CLI

Show help:
```bash
python main.py --help
```

Analyze a CSV file:
```bash
python main.py --csv sample_data/flights_sample.csv
```

Analyze a JSON file:
```bash
python main.py --json data/flights.json --batch-size 100
```

Enter a single flight manually:
```bash
python main.py --manual
```

Custom output directory and table row limit:
```bash
python main.py --csv sample_data/flights_sample.csv --output-dir reports --max-rows 10
```

## Example Output

```
flight_id  | time_of_flight | max_altitude | average_altitude | range      | average_speed | anomaly
------------------------------------------------------------------------------------------------------
FL001      | 120.00         | 1500.00      | 900.00           | 12000.00   | 100.00         | False
FL002      | 95.00          | 1200.00      | 700.00           | 9500.00    | 100.00         | False
...

===== FLIGHT DATA SUMMARY =====
Total flights processed: 6
Anomalies detected:      1

Metric                     Min       Max       Avg
--------------------------------------------------
time_of_flight            95.0     150.0     116.67
max_altitude             1200.0    1800.0    1533.33
...
================================

CSV report saved to:  output/flight_report_20260930_120000.csv
JSON report saved to: output/flight_report_20260930_120000.json
Execution time: 0.004 seconds
```

## Non-Technical Requirements — How They're Addressed

### Usability
- `argparse` provides `--help` with usage examples.
- Mutually exclusive `--csv`, `--json`, `--manual` flags make the intended input source explicit and prevent conflicting inputs.
- Clear, aligned terminal tables and a labeled summary block.
- Manual mode uses simple, labeled prompts (e.g. "Time of flight (seconds):").

### Logging & Monitoring
- `logger.py` configures a logger writing to `app.log` (DEBUG level and up: info on pipeline steps, warnings on skipped/invalid rows, errors on failures).
- Console only shows WARNING and above, keeping normal runs clean while `app.log` keeps a full audit trail.

### Scalability
- `ingestion.py` uses generator functions (`load_from_csv`, `load_from_json`) that `yield` fixed-size batches (`--batch-size`, default 50) instead of loading the entire file into memory at once.
- `main.py` processes and discards each batch in a loop, so memory use stays roughly constant regardless of file size.

### Performance
- Uses simple, lightweight built-in data structures (lists of dicts) — no heavy external dependencies.
- Execution time is measured with `time.time()` and printed at the end of every run.
- Validation short-circuits early on bad rows (skip immediately) instead of doing wasted downstream work.

## Error Handling

- Missing files raise a clear `FileNotFoundError` with a logged error and friendly console message.
- Malformed rows (missing fields, non-numeric values, negative numbers) are skipped individually with a warning — the program does not crash on bad data.
- Division-by-zero (e.g. `time_of_flight == 0`) is checked explicitly before computing expected speed.
