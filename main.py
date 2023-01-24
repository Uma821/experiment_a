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

timers = {}
led_process = {"quit_flag": Value('i', 0), # quit_flag = false
               "duty": Value('i', 0), "mode": Value('i', 0),
               "color": Array('i', [0,0,0]), "enable": Value('i', 1)} # [R,G,B]=[F,F,F]

def multiprocess_caller():
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

if __name__ == "__main__":
  try: # 初期化処理
    line_init() # これが一番初め
    cds_caller()
    infrared_caller()
    multiprocess_caller()

    while True:
      print("aaaaa")
      sleep(3)
      # cds_sensing()
      
  except KeyboardInterrupt:
    line_fin()
    for timer in timers.values():
      timer.cancel()
    led_process["quit_flag"].value = 1 # 脱出
    led_process["led"].join()
