import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import port_assign # 何番ポートか参照
import RPi.GPIO as GPIO
from time import sleep
import spidev

def led_brink(quit_flag, duty, mode, color): # LED
  # dutyの値が高いと
  # mode=1なら1秒ごとに点滅切り替え, 2なら0.5秒ごとに点滅切り替え
  # color=[R, G, B] どれかがTrueになっているはず
  # quit_flag, duty, mode, colorはmultiprocessing.Value等で管理する．外部から値を書きかえるため，毎回チェックする．
  GPIO.setmode(GPIO.BCM) # ピン番号の読み方をGPIOピン番号に
  GPIO.setup(port_assign.BLED_PORT, GPIO.OUT) 
  GPIO.setup(port_assign.GLED_PORT, GPIO.OUT)
  GPIO.setup(port_assign.RLED_PORT, GPIO.OUT)

  while True:
    if(color[0]):
      # 外部より指定したPWMのデューティ比で点灯時の明るさを指定
      # GPIO.output(port_assign.RLED_PORT, GPIO.HIGH) # pwm 100% になる
      pwm = GPIO.PWM(port_assign.RLED_PORT, 50) # (Pin, Hz) 
      pwm.start(duty.value) # 初期デューティ比
      sleep(1 if mode == 1 else 0.5) # modeで指定した一定期間待つ
      # GPIO.output(port_assign.RLED_PORT, GPIO.LOW) 
      pwm.ChangeDutyCycle(0) # 0%
      sleep(1 if mode == 1 else 0.5)

    elif(color[1]):
      # GPIO.output(port_assign.GLED_PORT, GPIO.HIGH) 
      pwm = GPIO.PWM(port_assign.GLED_PORT, 50) # (Pin, Hz)
      pwm.start(duty.value)
      sleep(1 if mode == 1 else 0.5)
      # GPIO.output(port_assign.GLED_PORT, GPIO.LOW) 
      pwm.ChangeDutyCycle(0) # 0%
      sleep(1 if mode == 1 else 0.5)
      
    elif(color[2]):
      # GPIO.output(port_assign.BLED_PORT, GPIO.HIGH) 
      pwm = GPIO.PWM(port_assign.BLED_PORT, 50) # (Pin, Hz)
      pwm.start(duty.value)
      sleep(1 if mode == 1 else 0.5)
      # GPIO.output(port_assign.BLED_PORT, GPIO.LOW) 
      pwm.ChangeDutyCycle(0) # 0%
      sleep(1 if mode == 1 else 0.5)

    pwm.stop()
    GPIO.cleanup()
    if quit_flag.value: # 点滅が終わったらチェックして終了（これは放置）
      break


if __name__ == "__main__": # テストするならif文内に
  from multiprocessing import Value, Array
  led_brink(
    Value('i', 1), # quit_flag = True
    Value('i', 40), # pwm = 60[%]
    Value('i', 0), # mode = 0
    Array('i', [0,1,0]) # [R,G,B] = [0,1,0]
  ) 
