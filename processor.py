"""
processor.py
Module 2: Processing Engine

Takes validated flight records and computes derived metrics,
flags anomalies, and builds summary statistics across all flights.
"""


def check_anomaly(record, logger, tolerance=0.20):
    """
    Cross-checks average_speed against range / time_of_flight.
    If the reported speed is off by more than 'tolerance' (20% default),
    flag the record as anomalous instead of throwing it away.
    """
    record["anomaly"] = False

    if record["time_of_flight"] == 0:
        logger.warning(
            f"Flight {record['flight_id']}: time_of_flight is 0, "
            f"cannot cross-check speed"
        )
        record["anomaly"] = True
        record["expected_speed"] = 0.0
        return record

    expected_speed = record["range"] / record["time_of_flight"]
    reported_speed = record["average_speed"]

    if expected_speed == 0:
        diff_ratio = 0
    else:
        diff_ratio = abs(expected_speed - reported_speed) / expected_speed

    if diff_ratio > tolerance:
        logger.warning(
            f"Flight {record['flight_id']}: reported speed "
            f"({reported_speed:.2f} m/s) differs from expected "
            f"({expected_speed:.2f} m/s) by {diff_ratio * 100:.1f}%"
        )
        record["anomaly"] = True

    record["expected_speed"] = round(expected_speed, 2)
    return record


def process_batch(batch, logger):
    """
    Processes one batch (list) of validated flight records.
    Adds derived fields (anomaly flag, expected speed) to each record.
    Returns the processed list.
    """
    processed = []
    for record in batch:
        try:
            record = check_anomaly(record, logger)
            processed.append(record)
        except Exception as e:
            logger.error(
                f"Error processing flight {record.get('flight_id', '?')}: {e}"
            )
    return processed


def compute_summary(all_records, logger):
    """
    Computes summary statistics across every flight record processed.
    Returns a dict with counts, min/max/avg for each numeric metric.
    """
    if not all_records:
        logger.warning("No valid records to summarize")
        return {
            "total_flights": 0,
            "anomalies_detected": 0,
            "metrics": {},
        }

    metrics_to_summarize = [
        "time_of_flight",
        "max_altitude",
        "average_altitude",
        "range",
        "average_speed",
    ]

    summary = {
        "total_flights": len(all_records),
        "anomalies_detected": sum(1 for r in all_records if r["anomaly"]),
        "metrics": {},
    }

    for metric in metrics_to_summarize:
        values = [r[metric] for r in all_records]
        summary["metrics"][metric] = {
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(sum(values) / len(values), 2),
        }

    logger.info(
        f"Summary computed: {summary['total_flights']} flights, "
        f"{summary['anomalies_detected']} anomalies detected"
    )
    return summary
