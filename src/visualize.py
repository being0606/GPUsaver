import time
import json
import wandb
import argparse
from loguru import logger


# entity를 명시하지 않으면 로그인된 사용자의 기본 네임스페이스에 프로젝트가 생성됩니다.
wandb.init(project="gpustat_monitor")
logger.info("wandb.init complete. Starting to monitor log file.")


def follow_jsonl_file(filepath):
    with open(filepath, "r") as f:
        # 파일 끝으로 이동
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(5)  # 새 로그 대기
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

        # 모든 GPU의 메트릭을 하나의 딕셔너리에 수집
        log_data = {}
        for gpu in gpus:
            gpu_index = gpu["index"]
            log_data[f"GPU{gpu_index}/utilization_gpu"] = gpu["utilization.gpu"]
            log_data[f"GPU{gpu_index}/memory_used"] = gpu["memory.used"]
            log_data[f"GPU{gpu_index}/temperature"] = gpu["temperature.gpu"]

        # 모든 GPU 데이터를 한 번에 로그
        wandb.log(log_data)
        logger.debug(f"Logged data for all GPUs at timestamp: {timestamp}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize gpustat logs with wandb.")
    parser.add_argument("--logfile", type=str, default="logs/gpustat_log.jsonl", help="Path to the gpustat log file (JSONL format).")
    args = parser.parse_args()

    main(logfile_path=args.logfile)