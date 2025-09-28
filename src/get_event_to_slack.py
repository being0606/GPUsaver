from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import os
from dotenv import load_dotenv

# .env 로드
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_API_GARDIAN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Slack App 초기화
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# Flask 서버 초기화
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# ✅ DM 또는 Mentions 이벤트 감지
@app.event("message")
def handle_message_events(body, say, event):
    user = event.get("user")
    text = event.get("text", "")
    channel = event.get("channel")

    # 봇 자신의 메시지는 무시
    if event.get("subtype") == "bot_message":
        return

    print(f"📩 {user}가 보낸 메시지: {text}")

    # 간단한 응답 로직
    if "GPU" in text:
        say(channel=channel, text=f"<@{user}> GPU 상태를 확인해드릴게요 🧠")
    else:
        say(channel=channel, text=f"<@{user}> 안녕하세요! 👋")

# Slack Event 엔드포인트
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=3000)