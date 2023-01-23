import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import spidev

# GPIO ポート
RLED_PORT = 24 # フルカラー赤
GLED_PORT = 23 # フルカラー緑
BLED_PORT = 18 # フルカラー青
BUZZER_PORT = 21

# ADコンバータ ポート
CDS_PORT = 0 
INFRARED_PORT = None # 人感センサー

# LCD_PORT = None # I2Cのため必要ない

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

# ADコンバータMCP3208からSPI通信で12ビットのデジタル値を取得
def analog_read(channel):
  words = [0x06 | (channel&0x04)>>2, (channel&0x03)<<6, 0x00]
  r = spi.xfer2(words)
  adc_out = ((r[1] & 0x0f) << 8) + r[2]
  return adc_out
