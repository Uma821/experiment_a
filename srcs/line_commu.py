import time, sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome import service as fs
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def line_init():
  options = Options()
  chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
  driver = webdriver.Chrome(options=options, service=chrome_service)
  driver.get("https://account.line.biz/signup")


import lineconfig   #環境変数のインポート
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
app = Flask(__name__)

line_bot_api = LineBotApi(lineconfig.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(lineconfig.LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)#メッセージが送られた際の操作
def handle_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    req  = request.json["events"][0]
    userMessage = req["message"]["text"]


    replymessage = selectwords(userMessage)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=replymessage)
    )

def selectwords(commandtext): #対応する言葉を選択
    reply = "こんにちは"
    return reply

if __name__ == "__main__":#最後に置かないと関数エラーが出るので注意！
    app.run(host="localhost", port=8080) # ポート番号を8080に指定

