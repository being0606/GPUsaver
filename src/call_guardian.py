import os
import time
import json
from dotenv import load_dotenv
from slack_sdk import WebClient
from loguru import logger

# 유틸리티 함수 임포트
from util import get_last_log_line, analyze_gpu_log_and_notify

# -----------------------------
# 환경 변수 로드 및 검증
# -----------------------------
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_API_GARDIAN")
SLACK_USER_MAP_JSON = os.getenv("SLACK_USER_MAP")

client = None
try:
    client = WebClient(token=SLACK_BOT_TOKEN)
except Exception as e:
    logger.error(f"Slack 클라이언트 초기화 실패: {e}. SLACK_BOT_API_GARDIAN 환경변수를 확인하세요.")

# -----------------------------
# 설정
# -----------------------------
USER_MAP = {}
if SLACK_USER_MAP_JSON:
    try:
        USER_MAP = json.loads(SLACK_USER_MAP_JSON)
    except json.JSONDecodeError:
        logger.error("SLACK_USER_MAP 환경 변수의 JSON 형식이 잘못되었습니다. 프로그램을 종료합니다.")
        exit()
else:
    logger.warning("SLACK_USER_MAP 환경 변수가 설정되지 않았습니다. 알림을 보낼 사용자가 없습니다.")

STATUS_FILE = "logs/gpustat_log.jsonl"
NUM_TOTAL_GPUS = 6 # 전체 GPU 개수
CHECK_INTERVAL_SECONDS = 1800 # 0.5시간

# -----------------------------
# 메인 루프
# -----------------------------
def main_loop():
    """GPU 상태를 체크하여 사용자에게 한 번 알림"""
    if not client:
        logger.error("Slack 클라이언트가 초기화되지 않아 프로그램을 종료합니다.")
        return
    
    if not USER_MAP:
        logger.warning("알림을 보낼 사용자가 설정되지 않았습니다. SLACK_USER_MAP 환경 변수를 확인하세요.")
        return

    logger.info("🔍 GPU 상태를 확인하고 알림을 보냅니다...")
    last_line = get_last_log_line(STATUS_FILE)

    if not last_line:
        logger.info("처리할 최신 GPU 로그가 없습니다.")
        return
    
    # 로그 분석 및 알림 로직을 유틸리티 함수로 위임
    analyze_gpu_log_and_notify(last_line, client, USER_MAP, NUM_TOTAL_GPUS, CHECK_INTERVAL_SECONDS)

# -----------------------------
# 실행 진입점
# -----------------------------
if __name__ == "__main__":
    while True:
        main_loop()
        logger.info(f"다음 확인까지 {CHECK_INTERVAL_SECONDS / 3600}시간 대기합니다...")
        time.sleep(CHECK_INTERVAL_SECONDS)