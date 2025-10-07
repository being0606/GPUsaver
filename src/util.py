import os
import json
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from loguru import logger


def get_last_log_line(filepath):
    """파일의 마지막 줄을 읽어옴"""
    try:
        with open(filepath, 'rb') as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
            return f.readline().decode('utf-8')
    except (FileNotFoundError, OSError, IndexError):
        logger.warning(f"로그 파일({filepath})을 읽을 수 없거나 비어있습니다.")
        return None

def read_notification_state(filepath: str) -> int:
    """알림 상태 파일에서 마지막으로 알려진 가용 GPU 수를 읽습니다."""
    try:
        with open(filepath, 'r') as f:
            state = json.load(f)
            return state.get("last_available_gpus", -1)
    except (FileNotFoundError, json.JSONDecodeError):
        # 파일이 없거나 비어있으면, 첫 실행 시 알림을 보내도록 -1을 반환합니다.
        logger.info("알림 상태 파일을 찾을 수 없거나 비어있습니다. 새로 생성합니다.")
        return -1

def write_notification_state(filepath: str, num_available_gpus: int):
    """현재 가용 GPU 수를 알림 상태 파일에 씁니다."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump({"last_available_gpus": num_available_gpus}, f)
        logger.info(f"알림 상태 업데이트 완료: 사용 가능 GPU {num_available_gpus}개.")
    except Exception as e:
        logger.error(f"알림 상태 파일 작성 중 에러 발생: {e}")



def send_dm(client: WebClient, user_map: dict, user_name: str, text: str):
    """username 기반으로 Slack DM 전송"""
    user_id = user_map.get(user_name)
    if not user_id:
        logger.warning(f"⚠️ {user_name}의 Slack ID를 찾을 수 없음.")
        return
    try:
        dm = client.conversations_open(users=[user_id])
        channel = dm["channel"]["id"]
        client.chat_postMessage(channel=channel, text=text)
        logger.info(f"📩 DM 전송 완료 → {user_name}: {text}")
    except SlackApiError as e:
        logger.error(f"⚠️ Slack API 에러 ({user_name}): {e.response['error']}")
    except Exception as e:
        logger.error(f"⚠️ DM 전송 중 알 수 없는 에러 ({user_name}): {e}")


def analyze_gpu_log_and_notify(last_line: str, client: WebClient, user_map: dict, num_total_gpus: int, check_interval_seconds: int, reference_link: str, status_file: str):
    """
    최신 GPU 로그 라인을 분석하고, 사용자에게 DM을 보냅니다.
    """
    # 머신별로 상태 파일을 다르게 지정
    state_file = status_file.replace(".jsonl", "_notification_state.json")

    try:
        record = json.loads(last_line)
        timestamp_iso = record.get("timestamp")
        gpus = record.get("gpustat", {}).get("gpus", [])

        # GPU별 사용자 집계
        gpu_users = {i: set() for i in range(num_total_gpus)}
        for gpu in gpus:
            gpu_index = gpu.get("index")
            if gpu_index is None or gpu_index not in gpu_users:
                continue
            
            for process in gpu.get("processes", []):
                username = process.get("username")
                if username:
                    logger.debug(f"GPU {gpu_index}에서 사용자 '{username}' 감지됨.")
                    gpu_users[gpu_index].add(username)
        
        # 사용자별 GPU 집계
        user_gpu_map = {} # {username: set_of_gpu_indices}
        for gpu_index, users_on_gpu in gpu_users.items():
            for user in users_on_gpu:
                if user not in user_gpu_map:
                    user_gpu_map[user] = set()
                user_gpu_map[user].add(gpu_index)

        # 사용 중인 GPU 수 계산 및 메시지 헤더 생성
        all_used_gpus = {gpu for gpus_set in user_gpu_map.values() for gpu in gpus_set}
        num_available_gpus = num_total_gpus - len(all_used_gpus)

        # --- 상태 변경 확인 로직 ---
        last_available_gpus = read_notification_state(state_file)

        if num_available_gpus == last_available_gpus:
            logger.info(f"사용 가능한 GPU 수({num_available_gpus}개)에 변경이 없어 알림을 보내지 않습니다.")
            return
        # --------------------------

        if num_available_gpus == 0:
            status_emoji = "😭"
        elif num_available_gpus <= 2:
            status_emoji = "🤔"
        else:
            status_emoji = "😊"

        dt_object = datetime.fromisoformat(timestamp_iso)
        formatted_time = dt_object.strftime("%Y년 %m월 %d일 %H시 %M분")
        
        guardian_header = f"[ GPU_Guardian 작동중 ]\n{check_interval_seconds / 3600}시간마다 GPU status를 확인하여 변화를 발견하면 알려드립니다.\n"

        message_header = f"{guardian_header}\n#--------------{status_emoji}--------------#\n\n[A6000서버 GPU 사용 현황]\n - {formatted_time} 기준 \n - 사용 가능: {num_available_gpus} / {num_total_gpus}대"

        # 사용자별 메시지 생성 및 전송
        if user_gpu_map:
            usage_messages = []
            for user in sorted(user_gpu_map.keys()):
                gpus_used_by_user = sorted(list(user_gpu_map[user]))
                usage_messages.append(f"  - {user} 님: GPU {', '.join(map(str, gpus_used_by_user))}번 사용 중")
            
            message = f"{message_header}\n\n[A6000서버 사용자별 현황]\n" + "\n".join(usage_messages)
            
        else:
            # 사용자가 없을 때도 상태를 알림
            message = f"{message_header}\n\n모든 GPU가 사용 가능합니다."

        # 참조 링크 추가
        if reference_link:
            message += f"\n\n[GPU캘린더링크]\nlink: {reference_link}"
            
        # user_map에 등록된 모든 사용자에게 알림 전송
        for user in user_map.keys():
            send_dm(client, user_map, user, message)
        
        # 알림 성공 후 상태 저장
        write_notification_state(state_file, num_available_gpus)

    except json.JSONDecodeError:
        logger.error(f"로그 파일 파싱 오류: {last_line}")
    except Exception as e:
        logger.error(f"GPU 로그 분석 및 알림 중 에러 발생: {e}")