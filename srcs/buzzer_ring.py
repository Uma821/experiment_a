import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import port_assign # 何番ポートか参照
from time import sleep
import RPi.GPIO as GPIO
import math


def onkai(n):
    a0 = 27.500 # 基準のラ
    return a0*math.pow(math.pow(2,1/12),n) # 半音は2^(1/12)倍

def buzzer_ring(stop_flag): # ブザーを鳴らす
  base_time = 0.2 # 秒
  DO = onkai(39)
  RE = onkai(41)
  MI = onkai(43)
  SO = onkai(46)

  mery_merody = [MI,RE,DO,RE,MI,MI,MI,RE,RE,RE,MI,SO,SO,MI,RE,DO,RE,MI,MI,MI,RE,RE,MI,RE,DO]
  mery_rhythm = [ 3, 1, 2, 2, 2, 2, 4, 2, 2, 4, 2, 2, 4, 3, 1, 2, 2, 2, 2, 4, 2, 2, 3, 1, 6]

  # tones_list = [
  #   (440, 1), # 440Hzを0.5秒
  #   (220, 2), # 220Hzを1秒
  # ]
  tones_list = zip(mery_merody, mery_rhythm)

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(port_assign.BUZZER_PORT, GPIO.OUT)

  p = None
  for (tone, time) in tones_list:
    if p is None:
      p = GPIO.PWM(port_assign.BUZZER_PORT, int(tone))
      p.start(50) # PWM = 50%
    else:
      p.ChangeFrequency(int(tone)) # https://sourceforge.net/p/raspberry-gpio-python/wiki/PWM/
    sleep(time*base_time)
     #HIGH, LOWをちゃんと制御するか，PWMで制御するのもありかもしれない
    if stop_flag.value: # 一音分終わったらチェックして終了（これは放置）
      break

  p.stop()
  GPIO.cleanup()

if __name__ == "__main__": # テストするならif文内に
  from multiprocessing import Value, Array
  try:
    buzzer_ring(Value('i', 0))

  except KeyboardInterrupt:
    pass
