import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import port_assign # 何番ポートか参照
import RPi.GPIO as GPIO
from time import sleep
import spidev

def led_brink(quit_flag, duty, mode, color, enable): # LED
  # dutyの値が高いと
  # mode=1なら1秒ごとに点滅切り替え, 2なら0.5秒ごとに点滅切り替え
  # color=[R, G, B] どれかがTrueになっているはず
  # quit_flag, duty, mode, colorはmultiprocessing.Value等で管理する．外部から値を書きかえるため，毎回チェックする．
  GPIO.setmode(GPIO.BCM) # ピン番号の読み方をGPIOピン番号に
  GPIO.setup(port_assign.BLED_PORT, GPIO.OUT) 
  GPIO.setup(port_assign.GLED_PORT, GPIO.OUT)
  GPIO.setup(port_assign.RLED_PORT, GPIO.OUT)
  pwms = [None, None, None] # [R, G, B]

  while True:
    print("led")
    if(color[0]):
      # 外部より指定したPWMのデューティ比で点灯時の明るさを指定
      # GPIO.output(port_assign.RLED_PORT, GPIO.HIGH if enable.value else GPIO.LOW) # pwm 100% になる
      if pwms[0] is None: # まだ一度も赤LEDはPWMをしていない
        pwms[0] = GPIO.PWM(port_assign.RLED_PORT, 100) # (Pin, Hz) 
        pwms[0].start(duty.value if enable.value else 0) # 初期デューティ比
      else:
        pwms[0].ChangeDutyCycle(duty.value if enable.value else 0)
      sleep(1 if mode.value == 1 else 0.5) # modeで指定した一定期間待つ
      # GPIO.output(port_assign.RLED_PORT, GPIO.LOW) 
      pwms[0].ChangeDutyCycle(0) # 0%
      sleep(1 if mode.value == 1 else 0.5)

    elif(color[1]):
      # GPIO.output(port_assign.GLED_PORT, GPIO.HIGH if enable.value else GPIO.LOW)
      if pwms[1] is None:
        pwms[1] = GPIO.PWM(port_assign.GLED_PORT, 100) # (Pin, Hz)
        pwms[1].start(duty.value if enable.value else 0)
      else:
        pwms[1].ChangeDutyCycle(duty.value if enable.value else 0)
      sleep(1 if mode.value == 1 else 0.5)
      # GPIO.output(port_assign.GLED_PORT, GPIO.LOW) 
      pwms[1].ChangeDutyCycle(0) # 0%
      sleep(1 if mode.value == 1 else 0.5)
      
    elif(color[2]):
      # GPIO.output(port_assign.BLED_PORT, GPIO.HIGH if enable.value else GPIO.LOW)
      if pwms[2] is None:
        pwms[2] = GPIO.PWM(port_assign.BLED_PORT, 100) # (Pin, Hz)
        pwms[2].start(duty.value if enable.value else 0)
      else:
        pwms[2].ChangeDutyCycle(duty.value if enable.value else 0)
      sleep(1 if mode.value == 1 else 0.5)
      # GPIO.output(port_assign.BLED_PORT, GPIO.LOW) 
      pwms[2].ChangeDutyCycle(0) # 0%
      sleep(1 if mode.value == 1 else 0.5)
      
    else: # 何色でもないとき
      sleep(0.5) # 高速ループ抑止
      
    if quit_flag.value: # 点滅が終わったらチェックして終了（これは放置）
      for pwm in pwms:
        if pwm is not None:
          pwm.stop()
      GPIO.cleanup()
      break


if __name__ == "__main__": # テストするならif文内に
  from multiprocessing import Value, Array
  led_brink(
    Value('i', 1),       # quit_flag = True
    Value('i', 40),      # pwm_duty = 60[%]
    Value('i', 0),       # mode = 0
    Array('i', [0,1,0]), # [R,G,B] = [0,1,0]
    Value('i', 1)        # enable = True
  ) 
