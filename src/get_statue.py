import time
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from loguru import logger

# --- Constants ---
DEFAULT_LOG_DIR = Path("logs")
DEFAULT_INTERVAL_SECONDS = 60


def get_gpustat_json():
    """Executes 'gpustat --json' and returns the parsed JSON data."""
    try:
        result = subprocess.run(['gpustat', '--json'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except FileNotFoundError:
        logger.error("`gpustat` command not found. Please ensure it is installed and in your PATH.")
        return None
    except Exception as e:
        logger.error(f"Error calling gpustat: {e}")
        return None

def save_log(data: dict, logfile_path: Path):
    """Saves timestamp and gpustat data in JSON Lines format."""
    logfile_path.parent.mkdir(parents=True, exist_ok=True)
    with open(logfile_path, 'a') as f:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "gpustat": data
        }
        f.write(json.dumps(log_entry) + "\n")

def main(logfile_path: Path, interval_seconds: int):
    """Periodically fetches and saves GPU status."""
    logger.info(f"Starting GPU monitoring. Logging to '{logfile_path}' every {interval_seconds} seconds.")
    while True:
        data = get_gpustat_json()
        if data:
            save_log(data, logfile_path)
            logger.success(f"GPU status saved successfully to '{logfile_path}'.")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Periodically log gpustat output to a file.")
    parser.add_argument("--machine-name", type=str, default="A6000", help="Name of the machine being monitored. Used in the log filename.")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS, help=f"Logging interval in seconds (default: {DEFAULT_INTERVAL_SECONDS}).")
    args = parser.parse_args()

    logfile = DEFAULT_LOG_DIR / f"log_gpustat_{args.machine_name}.jsonl"
    main(logfile_path=logfile, interval_seconds=args.interval)
