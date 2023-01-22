import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import spidev
from time import sleep
from port_assign import analog_read # 何番ポートか参照

def CdS_sensing(): # CdSセルで明るさを確認
  print("cds")
  # 第二回，第三回資料を参照のこと
  reading = analog_read(0)
  CdS_sensing.data = reading # 値を代入して
  # 値をアナログ値で受け取り，適切な境界を探す
  
  if reading < 3900: # 境界
     # print("Ture", reading)
     return True
  else:
    # print("False")
    return False # 明るい時はTrue 暗い時はFalse

if __name__ == "__main__": # テストするならif文内に
  for _ in range(50):
    CdS_sensing()
    sleep(0.5)
