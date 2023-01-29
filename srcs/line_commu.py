import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import platform, time, re
from multiprocessing import Process
from sqlite_manage import *


server = None
def line_init(open_browser=True):
  global server
  server = Process(target=app.run, kwargs={"host": "localhost", "port": 8080}) # ポート番号を8080に指定 
  server.start() 
  
  if not open_browser: # ブラウザ開かない設定
    return
  
  options = Options()
  options.add_experimental_option('detach', True) # 関数終了後もChromeを開いたままにする
  if platform.system() == "Linux" and platform.machine() == "armv7l":  
    # if raspi(linux 32bitはwebdriver_manager非対応)
    options.BinaryLocation = ("/usr/bin/chromium-browser") # chromium使用
    service = Service("/usr/bin/chromedriver")
  else: # not raspi and use Chrome
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(options=options, service=service)
  driver.get("https://developers.line.biz/console/")

  # try:
  #   while True:
  #     time.sleep(1)
  # except KeyboardInterrupt:
  #   driver.quit() # 終了処理(Chromeの場合)
  

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
        chat_bar_text = "Click here", # 短文じゃないとだめ？
        areas = [
            RichMenuArea(
                bounds = RichMenuBounds(x=0, y=0, width=1250, height=843),
                action = # URIAction(label='Go to line.me', uri='https://line.me')
                    MessageAction(label="バス停スケジュールを確認", text="通知スケジュール確認") # 自分が言ったことになる
            ), RichMenuArea(
                bounds = RichMenuBounds(x=1250, y=0, width=1250, height=843),
                action = MessageAction(label="バス停スケジュールを設定", text="通知スケジュール設定")
            )
        ]
    )
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    with open("imgs/rich_menu.png", "rb") as f: # 実行時，カレントディレクトリはmain.py視点
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
    DB_create_new_row(event.source.user_id) # DBに，ユーザーIDの列を追加する


@handler.add(MessageEvent, message=TextMessage) # テキストメッセージが送られた際の操作
def handle_message(event): # MessageEvent インスタンスが渡される
    if event.reply_token == "00000000000000000000000000000000": # 有効なreplyTokenではない
        return
    req  = request.json["events"][0]
    userMessage = req["message"]["text"]

    (def_outbound_url, def_inbound_url, shedule_list) = try_get_schedule(userMessage) # スケジュール指定方式
    if shedule_list: # マッチした場合
        DB_update_schedule_data(event.source.user_id, def_outbound_url, def_inbound_url, shedule_list)
        replymessage = selectwords(userMessage, True)
    else:
        replymessage = selectwords(userMessage, False)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=replymessage)
    )


@handler.add(UnfollowEvent) #テキストメッセージが送られた際の操作
def handle_unfollow(event): # MessageEvent インスタンスが渡される
    # if event.reply_token == "00000000000000000000000000000000": # 有効なreplyTokenではない
    #     return
    DB_delete_schedule_data(event.source.user_id)

def send_line_message(approach_list, user_id_set):
    for user_id in user_id_set:
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text=f"{approach_list[1]}行のバスがあと{approach_list[-1]}分({approach_list[0]}予定)で到着します。")
        )

def try_get_schedule(commandtext):
    match_data = re.match(r'(\S*),\s*(\S*),\s*(\(\S*,\s*\d,\s*\d,\s*\d+,\s*\d+,\s*\d+,\s*\d+\),?)+$', commandtext)
    if match_data is None: return (None, None, []) # マッチしなかった場合
    return (match_data.group(1),match_data.group(2),re.findall('\(([^,]*),\s*(\d),\s*(\d),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', match_data.group(3)))

def selectwords(commandtext, shedule_ok): # 対応する言葉を選択
    if shedule_ok: # スケジュール指定として評価できた場合
        reply = "スケジュール設定しました。数分後から反映されます。"
    elif commandtext == "通知スケジュール確認":
        reply = "大変申し訳ありません、通知スケジュール確認機能は現在ご使用できません。"
    elif commandtext == "通知スケジュール設定":
        reply = """'[行きのデフォルトURL]','[帰りのデフォルトURL]',('[URL]',[デフォルトを使うなら行き(0)帰り(1)]',[曜日(0~6)],[開始時],[開始分],[終了時],[終了分])... の形式で入力してください。
例：'https://kuruken.jp/Approach?sid=b31e050b-fcb5-4b18-b15e-dbbd8c401583&noribaChange=1','https://kuruken.jp/Approach?sid=8cdf9206-6a32-4ba9-8d8c-5dfdc07219ca&noribaChange=1',(None,0,0,7,30,9,0)(None,1,3,17,30,19,0)
0(月曜日)に7:30から9:00まで行きのバスを確認、3(木曜日)に17:30から19:00まで帰りのバスを確認する設定になります。(URLを個別指定する場合では行き帰り指定は無視されますが0か1を記述する必要があります。)"""
    else:
        reply = "すみません、よくわかりません"
    return reply

if __name__ == "__main__": #最後に置かないと関数エラーが出るので注意！
    app.run(host="localhost", port=8080) # ポート番号を8080に指定

