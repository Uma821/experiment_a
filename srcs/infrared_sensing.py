import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import spidev
from time import sleep
import port_assign            # 何番ポートか参照
from utils import analog_read # analog_read呼出

def infrared_sensing(): # 人感センサーで人を確認
  print("inf")
  # 第二回，第三回資料を参照のこと
  reading = analog_read(port_assign.INFRARED_PORT)
  infrared_sensing.data = reading # 値を代入して
  # 値をアナログ値で受け取り，適切な境界を探す
  
  if reading > 3900: # 境界
     # print("Ture", reading)
     return True
  else:
    # print("False")
    return False # 気配がある時はTrue ない時はFalse

if __name__ == "__main__": # テストするならif文内に
  for _ in range(50):
    infrared_sensing()
    sleep(0.5)
