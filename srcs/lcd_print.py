import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
from time import sleep
import port_assign
from LCDLib import LCD1602A

lcd = LCD1602A(i2c_addr=port_assign.LCD_ADDRESS)
lcd.setup()

def LCD_print(message): # LCDに文字列表示，message[0]に1行目，message[1]に2行目データ，lcd_onで表示/非表示切り替え
  # 第二回資料を参照のこと

  # lcd.clear()
  # sleep(0.3)
  lcd.write_string(message[0])
  lcd.newline()
  lcd.write_string(message[1])
  # sleep(0.7)

def LCD_clear():
  lcd.clear()

if __name__ == "__main__": # テストするならif文内に
  LCD_print(["ｱｱｱWelcome to", "Jikken Alphal!"], True)
