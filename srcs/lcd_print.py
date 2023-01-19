import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
from time import sleep
from LCDLib import LCD1602A

def LCD_print(message, lcd_on): # LCDに文字列表示，message[0]に1行目，message[1]に2行目データ，lcd_onで表示/非表示切り替え
  # 第二回資料を参照のこと
  # 半角カタカナを使いますので，一度試して，うまく行かなかったら言ってください
  # 例：ﾋｮｳｼﾞﾃﾞｷﾃﾙｶｲ

  pass # 何か書くとき消す

if __name__ == "__main__": # テストするならif文内に
  pass
