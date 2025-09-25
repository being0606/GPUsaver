import time
import json
import os
import subprocess
import argparse
from datetime import datetime

def get_gpustat_json():
    try:
        # Execute the 'gpustat --json' command
        result = subprocess.run(['gpustat', '--json'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error calling gpustat: {e}")
        return None

def save_log(data, filename):
    # Save timestamp and gpustat data in JSON Lines format.
    # Create the log directory if it doesn't exist.
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'a') as f:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "gpustat": data
        }
        f.write(json.dumps(log_entry) + "\n")

def main(logfile_path, interval_seconds):
    while True:
        data = get_gpustat_json()
        if data:
            save_log(data, filename=logfile_path)
            print(f"[{datetime.now().isoformat()}] GPU status saved successfully.")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Periodically log gpustat output to a file.")
    parser.add_argument("--logfile", type=str, default="logs/gpustat_log.jsonl", help="Path to the log file (JSONL format).")
    parser.add_argument("--interval", type=int, default=60, help="Logging interval in seconds.")
    args = parser.parse_args()

    main(logfile_path=args.logfile, interval_seconds=args.interval)
