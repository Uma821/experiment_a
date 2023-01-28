from threading import Timer
from multiprocessing import Process, Value, Array
import sys
sys.path.append("srcs") # 相対パスimportしようとしたが，子プログラムからも実行するときにバグるので検索ディレクトリを追加することにした
sys.dont_write_bytecode = True # pycache要らない
import RPi.GPIO as GPIO
import pykakasi, jaconv # 漢字->カタカナ->ｶﾀｶﾅ
import srcs.port_assign as port_assign
import srcs.urlconfig as urlconfig
from srcs.buzzer_ring import *
from srcs.led_brink import *
from srcs.lcd_print import *
from srcs.cds_sensing import *
from srcs.pir_sensing import *
from srcs.line_commu import *
from srcs.utils import clip
from srcs.scraping_kuruken import scraping_kuruken


timers = {}
led_process = {"quit_flag": Value('i', 0), # quit_flag = false
               "duty": Value('i', 0), "mode": Value('i', 1),
               "color": Array('i', [0,1,0]), "enable": Value('i', 1)} # [R,G,B]=[F,T,F] # 初期状態緑点滅

def led_caller():
  led_process["led"] = Process(target=led_brink, kwargs=led_process) # args=(CdS_caller.data)
  led_process["led"].start()

def cds_caller(): # CdSの値によってLEDの明るさが決まる
  timers["CdS"] = Timer(1, cds_caller)
  timers["CdS"].start()
  cds_sensing() # 読み取りデータは0~4095の範囲内
  led_process["duty"].value = 100 - int(clip(cds_sensing.data/18 - 90, 0, 100)) # 任意の最小値・最大値に収める
  # print(cds_sensing.data/18) # 明るい(60)、通常(135) 暗い(210)

def pir_caller():
  timers["pir"] = Timer(10, pir_caller)
  timers["pir"].start()
  led_process["enable"].value = pir_sensing()
  
def change_led_mode(bus_sorted_list):
  # 複数のバスサイトをスクレイピングできるが、ラズパイ側は１サイトだけ([0]の意)
  if (not bus_sorted_list[0].approach_list) or (bus_sorted_list[0].approach_list[0][-1] is None):
    # 深夜などで運行情報がない場合 or 来るけどこの先当分来ない
    led_process["color"][0] = 0
    led_process["color"][1] = 0
    led_process["color"][2] = 0 # 全部消灯
    return

  if int(bus_sorted_list[0].approach_list[0][-1]) <= 5: # 青点滅
    led_process["color"][0] = 0
    led_process["color"][1] = 0
    led_process["color"][2] = 1
    led_process["mode"].value = 1
  elif int(bus_sorted_list[0].approach_list[0][-1]) <= 2: # 赤高速点滅
    led_process["color"][0] = 1
    led_process["color"][1] = 0
    led_process["color"][2] = 0
    led_process["mode"].value = 2
  
def scraping_and_change_led_lcd(direction): # Ture->行き
  def complement_delay_time(bus_datas):
    from datetime import datetime, timedelta, timezone
    # JSTタイムゾーンを作成
    jst = timezone(timedelta(hours=9), 'JST')

    for bus_scraping_data in bus_datas: # 複数URLで3つ分のバス時刻を取得
      for approach_list in bus_scraping_data.approach_list:
        arrive_arrangement = datetime.now(jst).replace(hour=int(approach_list[0][0:-3]), minute=int(approach_list[0][-2:]))-datetime.now(jst) # 予定到着時間
        approach_list[-1] = str(arrive_arrangement.seconds//60) if approach_list[-1] is None else approach_list[-1] # 到着時刻がないときは到着予定時刻で代替
    return bus_datas

  print("start!!!!!")
  bus_datas = scraping_kuruken(
      [urlconfig.OUTBOUND_URL if direction else urlconfig.INBOUND_URL]
      )
  print("end!!!!!")
  bus_datas = complement_delay_time(bus_datas)
  change_led_mode(bus_datas)
  LCD_print(
      [f"{'ｲｷ' if direction else 'ｶｴﾘ'} {jaconv.z2h(''.join(map(lambda x: x['kana'], pykakasi.kakasi().convert(bus_datas[0].depart_stop))), digit=True, ascii=True)[0:12]}", # 目的地 漢字->カタカナ->ｶﾀｶﾅ
       f"{bus_datas[0].approach_list[0][-1]}ﾌﾝｺﾞ{bus_datas[0].approach_list[0][0][-3:]} {bus_datas[0].approach_list[1][-1]+'ﾌﾝｺﾞ'+bus_datas[0].approach_list[1][0][-3:] if len(bus_datas[0].approach_list)>1 else ''}" if bus_datas[0].approach_list else "ﾄｳﾒﾝ ﾅｼ"])
  return bus_datas
  
def set_bus_direction(channel):
  set_bus_direction.direction = GPIO.input(channel)
  scraping_and_change_led_lcd(set_bus_direction.direction)
  

if __name__ == "__main__":
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(port_assign.SWITCH_PORT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  
  try: # 初期化処理
    line_init(False) # line用のwebサーバ(flask)を実行する(Line設定画面表示しない)
    cds_caller()
    pir_caller()
    led_caller()
    # callback関数登録（GPIO.BOTH:立上り立下りエッジ検出、bouncetime:300ms）
    GPIO.add_event_detect(port_assign.SWITCH_PORT, GPIO.BOTH, bouncetime=300,
      callback=set_bus_direction)
    set_bus_direction(port_assign.SWITCH_PORT)

    while True:
      print(scraping_and_change_led_lcd(set_bus_direction.direction))
      sleep(60)
      
  except KeyboardInterrupt:
    line_fin()
    for timer in timers.values():
      timer.cancel()
    led_process["quit_flag"].value = 1 # 脱出
    led_process["led"].join()
  
  GPIO.remove_event_detect(port_assign.SWITCH_PORT)
  GPIO.cleanup()
