import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import spidev
from port_assign import analog_read # 何番ポートか参照

def infrared_sensing(): # 人感センサーで人を確認
  # 第二回，第三回資料を参照のこと
  # 値をアナログ値で受け取り，適切な境界を探す
  return None # 人が近くにいる時はTrue いない時はFalse

if __name__ == "__main__": # テストするならif文内に
  pass
