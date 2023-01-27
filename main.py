from threading import Timer
from multiprocessing import Process, Value, Array
import sys
sys.path.append("srcs") # 相対パスimportしようとしたが，子プログラムからも実行するときにバグるので検索ディレクトリを追加することにした
sys.dont_write_bytecode = True # pycache要らない
from srcs.buzzer_ring import *
from srcs.led_brink import *
from srcs.cds_sensing import *
from srcs.infrared_sensing import *
from srcs.line_commu import *
from srcs.utils import clip
from srcs.scraping_kuruken import scraping_kuruken

timers = {}
led_process = {"quit_flag": Value('i', 0), # quit_flag = false
               "duty": Value('i', 0), "mode": Value('i', 0),
               "color": Array('i', [0,0,0]), "enable": Value('i', 1)} # [R,G,B]=[F,F,F]

def led_caller():
  led_process["led"] = Process(target=led_brink, kwargs=led_process) # args=(CdS_caller.data)
  led_process["led"].start()

def cds_caller(): # CdSの値によってLEDの明るさが決まる
  timers["CdS"] = Timer(1, cds_caller)
  timers["CdS"].start()
  cds_sensing() # 読み取りデータは0~4095の範囲内
  led_process["duty"].value = 100 - int(clip(cds_sensing.data/30 - 30, 0, 100)) # 任意の最小値・最大値に収める

def infrared_caller():
  timers["inf"] = Timer(10, infrared_caller)
  timers["inf"].start()
  led_process["enable"].value = infrared_sensing()
  
def change_led_mode(bus_sorted_list):
  if not bus_sorted_list: # 深夜などで運行情報がない場合
    led_process["color"][0] = 0
    led_process["color"][1] = 0
    led_process["color"][2] = 0 # 全部消灯
    return
  if bus_sorted_list[0][-1] <= 5: # 青点滅
    led_process["color"][0] = 0
    led_process["color"][1] = 0
    led_process["color"][2] = 1
    led_process["mode"].value = 1
  elif bus_sorted_list[0][-1] <= 2: # 赤高速点滅
    led_process["color"][0] = 1
    led_process["color"][1] = 0
    led_process["color"][2] = 0
    led_process["mode"].value = 2

if __name__ == "__main__":
  try: # 初期化処理
    line_init() # line用のwebサーバ(flask)を実行する
    cds_caller()
    infrared_caller()
    led_caller()

    while True:
      print(d:=scraping_kuruken(["https://kuruken.jp/Approach?sid=8cdf9206-6a32-4ba9-8d8c-5dfdc07219ca&noribaChange=1"]))
      sleep(60)
      change_led_mode(d)
      
  except KeyboardInterrupt:
    line_fin()
    for timer in timers.values():
      timer.cancel()
    led_process["quit_flag"].value = 1 # 脱出
    led_process["led"].join()
