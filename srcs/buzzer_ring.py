import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import port_assign # 何番ポートか参照
from time import sleep
import RPi.GPIO as GPIO
import math



def onkai(n):
    return a0*math.pow(math.pow(2,1/12),n)

#for i,oto in enumerate(mery_merody):
#    p.start(50)
#    sleep(mery_rhythm[i])
#    p.stop()
#    sleep(0.03)

#p.stop()    
#GPIO.cleanup()

def buzzer_ring(stop_flag): # ブザーを鳴らす
  base_time = 0.5 # 秒
  DO = onkai(27)
  RE = onkai(29)
  MI = onkai(31)
  SO = onkai(34)

  mery_merody = [MI,RE,DO,RE,MI,MI,MI,RE,RE,MI,SO,SO,MI,RE,DO,RE,MI,MI,MI,RE,RE,MI,RE,DO]
  mery_rhythm = [0.9,0.3,0.6,0.6,0.6,0.6,1.2,0.6,0.6,1.2,0.6,0.6,1.2,0.6,0.6,1.2,0.9,0.3,0.6,0.6,0.6,0.6,1.2,0.6,0.6,0.9,0.3,1.8]

  tones_list = [
    (440, 1), # 440Hzを0.5秒
    (220, 2), # 220Hzを1秒
  ] 

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(port_assign.BUZZER_PORT, GPIO.OUT)

  for (tone, time) in tones_list:
    p = GPIO.PWM(port_assign.BUZZER_PORT, int(tone))
    p.start(50) # PWM = 50%
    sleep(time*base_time)
    p.stop()
     #HIGH, LOWをちゃんと制御するか，PWMで制御するのもありかもしれない
    if stop_flag: # 一音分終わったらチェックして終了（これは放置）
      break

  GPIO.stop()

if __name__ == "__main__": # テストするならif文内に
  try:

    buzzer_ring()

  except KeyboardInterrupt:
    pass
