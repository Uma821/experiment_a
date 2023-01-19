# import spidev
from port_assign import analog_read # 何番ポートか参照

def CdS_sensing(): # CdSセルで明るさを確認
  print("cds")
  # 第二回，第三回資料を参照のこと
  CdS_sensing.data = None # 値を代入して
  # 値をアナログ値で受け取り，適切な境界を探す
  return None # 明るい時はTrue 暗い時はFalse

if __name__ == "__main__": # テストするならif文内に
  pass
