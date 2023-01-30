from threading import Timer, Thread
from multiprocessing import Process, Value, Array
import sys
sys.path.append("srcs") # 相対パスimportしようとしたが，子プログラムからも実行するときにバグるので検索ディレクトリを追加することにした
sys.dont_write_bytecode = True # pycache要らない
import RPi.GPIO as GPIO
import pykakasi, jaconv # 漢字->カタカナ->ｶﾀｶﾅ
import srcs.port_assign as port_assign
import srcs.urlconfig as urlconfig
from srcs.buzzer_ring import buzzer_ring
from srcs.led_brink import *
from srcs.lcd_print import *
from srcs.cds_sensing import *
from srcs.pir_sensing import *
from srcs.line_commu import *
from srcs.utils import clip
from srcs.scraping_scheduler import (
    scraping_scheduler, scraping_scheduler_init
)


timers = {}
led_process = {"quit_flag": Value('i', 0), # quit_flag = false
               "duty": Value('i', 0), "mode": Value('i', 0),
               "color": Array('i', [0,1,0]), "enable": Value('i', 1)} # [R,G,B]=[F,T,F] # 初期状態緑点滅
buzzer_thread = {"stop_flag": Value('i', 0)} # quit_flag = false

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
  
def change_led_mode(bus_scraping_data):
  if not bus_scraping_data.approach_list:
    # 深夜などで運行情報がない場合
    led_process["color"][0] = 0
    led_process["color"][1] = 0
    led_process["color"][2] = 0 # 全部消灯
    led_process["mode"].value = 0
    return

  if bus_scraping_data.approach_list[0][-1] <= 2: # 赤高速点滅
    led_process["color"][0] = 1
    led_process["color"][1] = 0
    led_process["color"][2] = 0
    led_process["mode"].value = 2
  elif bus_scraping_data.approach_list[0][-1] <= 5: # 青点滅
    if led_process["mode"].value != 1: # 初めてやってきた
      if "buzzer" in buzzer_thread:
        buzzer_thread["stop_flag"].value = 1
        buzzer_thread["buzzer"].join()
      buzzer_thread["stop_flag"].value = 0 # 念の為
      buzzer_thread["buzzer"] = Process(target=buzzer_ring, args=(buzzer_thread["stop_flag"],))
      buzzer_thread["buzzer"].start()

    led_process["color"][0] = 0
    led_process["color"][1] = 0
    led_process["color"][2] = 1
    led_process["mode"].value = 1
  else:
    # 当分来ない場合
    led_process["color"][0] = 0
    led_process["color"][1] = 0
    led_process["color"][2] = 0
  
def display_manager(direction): # Ture->行き
  # scraping_schedulerによって管理されたデータを取得
  bus_scraping_data = scraping_scheduler.scheduling_dict[
      urlconfig.OUTBOUND_URL if direction else urlconfig.INBOUND_URL][1]
  if bus_scraping_data is None: # まだデータがない
    return None
  change_led_mode(bus_scraping_data)
  LCD_print([
      f"{'ｲｷ' if direction else 'ｶｴﾘ'} {jaconv.z2h(''.join(map(lambda x: x['kana'], pykakasi.kakasi().convert(bus_scraping_data.depart_stop))), digit=True, ascii=True)[0:12]}", # 目的地 漢字->カタカナ->ｶﾀｶﾅ
      f"{bus_scraping_data.approach_list[0][-1]}ﾌﾝｺﾞ{bus_scraping_data.approach_list[0][0][-3:]} {f'{bus_scraping_data.approach_list[1][-1]}ﾌﾝｺﾞ{bus_scraping_data.approach_list[1][0][-3:]}' if len(bus_scraping_data.approach_list)>1 else ''}"[:16] if bus_scraping_data.approach_list else "ﾄｳﾒﾝ ﾅｼ"
    ])
  return bus_scraping_data

def display_manager_caller():
  timers["disp"] = Timer(10, display_manager_caller)
  timers["disp"].start()
  display_manager(set_bus_direction.direction)
  
def set_bus_direction(channel):
  sleep(0.1) # チャタリング防止
  set_bus_direction.direction = GPIO.input(channel)
  if timers.get("disp", None) is not None:
    timers["disp"].cancel()
    display_manager_caller()

if __name__ == "__main__":
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(port_assign.SWITCH_PORT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  
  try: # 初期化処理
    line_init(False) # line用のwebサーバ(flask)を実行する(Line設定画面表示しない)
    cds_caller()
    pir_caller()
    led_caller()
    # callback関数登録（GPIO.BOTH:立上り立下りエッジ検出、bouncetime:100ms）
    GPIO.add_event_detect(port_assign.SWITCH_PORT, GPIO.BOTH, bouncetime=100,
      callback=set_bus_direction)
    set_bus_direction(port_assign.SWITCH_PORT)

    scraping_scheduler_init() # こっちが先
    display_manager_caller()
    scraping_scheduler() # 無限ループで次にスクレイピングタイミング管理
      
  except KeyboardInterrupt:
    line_fin()
    LCD_clear()
    for timer in timers.values():
      timer.cancel()
    led_process["quit_flag"].value = 1 # 脱出
    led_process["led"].join()
    buzzer_thread["stop_flag"].value = 1
    if "buzzer" in buzzer_thread:
      buzzer_thread["buzzer"].join()
  
  GPIO.remove_event_detect(port_assign.SWITCH_PORT)
  GPIO.cleanup()
