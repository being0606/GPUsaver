import time
import json
import wandb
import argparse
from loguru import logger


# If entity is not specified, the project will be created in the default namespace of the logged-in user.
wandb.init(project="gpustat_monitor")
logger.info("wandb.init complete. Starting to monitor log file.")


def follow_jsonl_file(filepath):
    with open(filepath, "r") as f:
        # Move to the end of the file
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(5)  # Wait for new logs
                continue
            yield line



def main(logfile_path):
    logger.info(f"Following log file: {logfile_path}")
    try:
        log_lines = follow_jsonl_file(logfile_path)
    except FileNotFoundError:
        logger.error(f"Log file not found at: {logfile_path}. Please run get_statue.py first.")
        return
    for line in log_lines:
        record = json.loads(line)
        timestamp = record["timestamp"]
        gpus = record.get("gpustat", {}).get("gpus", [])

        # Collect metrics for all GPUs into a single dictionary
        log_data = {}
        for gpu in gpus:
            gpu_index = gpu["index"]
            log_data[f"GPU{gpu_index}/utilization_gpu"] = gpu["utilization.gpu"]
            log_data[f"GPU{gpu_index}/memory_used"] = gpu["memory.used"]
            log_data[f"GPU{gpu_index}/temperature"] = gpu["temperature.gpu"]

        # Log all GPU data at once
        wandb.log(log_data)
        logger.debug(f"Logged data for all GPUs at timestamp: {timestamp}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize gpustat logs with wandb.")
    parser.add_argument("--logfile", type=str, default="logs/gpustat_log.jsonl", help="Path to the gpustat log file (JSONL format).")
    args = parser.parse_args()

    main(logfile_path=args.logfile)