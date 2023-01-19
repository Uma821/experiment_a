# import spidev

CDS_PORT = None
# LCD_PORT = None # I2Cのため必要ない

RLED_PORT = None # フルカラー赤
GLED_PORT = None # フルカラー緑
BLED_PORT = None # フルカラー青
BUZZER_PORT = None

INFRARED_PORT = None # 人感センサー

# ADコンバータMCP3208からSPI通信で12ビットのデジタル値を取得
def analog_read(channel):
  words = [0x06 | (channel&0x04)>>2, (channel&0x03)<<6, 0x00]
  r = spi.xfer2(words)
  adc_out = ((r[1] & 0x0f) << 8) + r[2]
  return adc_out

if __name__ == "__main__": # テストするならif文内に
  pass
