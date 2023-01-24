import time, sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import platform, time
from multiprocessing import Process


server = None
def line_init():
  global server
  server = Process(target=app.run, kwargs={"host": "localhost", "port": 8080}) # ポート番号を8080に指定 
  server.start() 
    
  options = Options()
  if platform.system() == "Linux" and platform.machine() == "armv7l":  
    # if raspi(linux 32bitはwebdriver_manager非対応)
    options.BinaryLocation = ("/usr/bin/chromium-browser") # chromium使用
    service = Service("/usr/bin/chromedriver")
  else: # not raspi and use Chrome
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(options=options, service=service)
  driver.get("https://developers.line.biz/console/")

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    driver.quit() # 終了処理(Chromeの場合)

def line_fin():
  server.terminate()
  server.join()


import lineconfig   #環境変数のインポート
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FollowEvent, UnfollowEvent, 
)
from linebot.models.rich_menu import (
    RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, 
)
from linebot.models.actions import (
    URIAction, MessageAction
)
app = Flask(__name__)

line_bot_api = LineBotApi(lineconfig.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(lineconfig.LINE_CHANNEL_SECRET)

def createRichmenu():
    rich_menu_to_create = RichMenu(
        size = RichMenuSize(width=2500, height=843),
        selected = False,
        name = "Nice richmenu",
        chat_bar_text = "バス情報登録・確認方法チェックはこちらから！",
        areas = [
            RichMenuArea(
                bounds = RichMenuBounds(x=0, y=0, width=1250, height=843),
                action = # URIAction(label='Go to line.me', uri='https://line.me')
                    MessageAction(label="バス停スケジュールを確認", text="「通知スケジュール」や「通知スケジュール確認」と送信してください")
            ), RichMenuArea(
                bounds = RichMenuBounds(x=1250, y=0, width=1250, height=843),
                action = MessageAction(label="バス停スケジュールを設定", text="「通知スケジュール設定」と送信してください")
            )
        ]
    )
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    with open("../imgs/rich_menu.png", "rb") as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
    
    line_bot_api.set_default_rich_menu(rich_menu_id)


@app.route("/callback", methods=['POST']) # LINE Messaging API の githubよりコピペ
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(FollowEvent) # 友達登録されたとき，ブロック解除されたとき
def handle_follow(event): # MessageEvent インスタンスが渡される
    # if event.reply_token == "00000000000000000000000000000000": # 有効なreplyTokenではない
    #     return

    if event.type == "follow": # フォロー時のみメッセージを送信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="フォローありがとうございます！")
        )
    
    createRichmenu() # リッチメニュー設定


@handler.add(MessageEvent, message=TextMessage) # テキストメッセージが送られた際の操作
def handle_message(event): # MessageEvent インスタンスが渡される
    if event.reply_token == "00000000000000000000000000000000": # 有効なreplyTokenではない
        return
    req  = request.json["events"][0]
    userMessage = req["message"]["text"]


    replymessage = selectwords(userMessage)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=replymessage)
    )


@handler.add(UnfollowEvent) #テキストメッセージが送られた際の操作
def handle_unfollow(event): # MessageEvent インスタンスが渡される
    # if event.reply_token == "00000000000000000000000000000000": # 有効なreplyTokenではない
    #     return

    pass

def selectwords(commandtext): #対応する言葉を選択
    reply = "こんにちは"
    return reply

if __name__ == "__main__": #最後に置かないと関数エラーが出るので注意！
    app.run(host="localhost", port=8080) # ポート番号を8080に指定

