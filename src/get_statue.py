import time
import json
import os
import subprocess
import argparse
from datetime import datetime

def get_gpustat_json():
    try:
        # gpustat --json 명령 실행
        result = subprocess.run(['gpustat', '--json'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"gpustat 호출 에러: {e}")
        return None

def save_log(data, filename):
    # JSON Lines 형식으로 시간과 gpustat 데이터를 저장
    # 로그 디렉터리가 없으면 생성
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
            print(f"[{datetime.now().isoformat()}] GPU 상태 저장 완료")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Periodically log gpustat output to a file.")
    parser.add_argument("--logfile", type=str, default="logs/gpustat_log.jsonl", help="Path to the log file (JSONL format).")
    parser.add_argument("--interval", type=int, default=60, help="Logging interval in seconds.")
    args = parser.parse_args()

    main(logfile_path=args.logfile, interval_seconds=args.interval)
