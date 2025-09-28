import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def find_slack_user_ids():
    """
    Slack 워크스페이스의 모든 사용자의 이름과 ID를 출력합니다.
    .env 파일에서 SLACK_BOT_API_GARDIAN 토큰을 사용합니다.
    """
    # .env 파일에서 환경 변수를 로드합니다.
    load_dotenv()
    token = os.getenv("SLACK_BOT_API_GARDIAN")

    if not token:
        print("오류: SLACK_BOT_API_GARDIAN 환경 변수가 .env 파일에 설정되지 않았습니다.")
        return

    client = WebClient(token=token)

    try:
        print("Slack 워크스페이스 사용자 목록을 조회합니다...")
        # users.list API 호출
        result = client.users_list()

        print("-" * 30)
        for member in result["members"]:
            # 실제 이름이 없으면 사용자 이름(name)을 사용
            name = member.get("real_name", member.get("name"))
            uid = member["id"]
            print(f"이름: {name}, 사용자 ID: {uid}")
        print("-" * 30)

    except SlackApiError as e:
        print(f"API 오류 발생: {e.response['error']}")

if __name__ == "__main__":
    find_slack_user_ids()
