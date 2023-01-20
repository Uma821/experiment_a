import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import port_assign # 何番ポートか参照
import RPi.GPIO as GPIO
from time import sleep
import spidev

def led_brink(quit_flag, pwm, mode, color): # LED
  # pwmの値が高いと
  # mode=1なら1秒ごとに点滅切り替え, 2なら0.5秒ごとに点滅切り替え
  # color=[R, G, B] どれかがTrueになっているはず
  GPIO.setmode(GPIO.BCM) # ピン番号の読み方をGPIOピン番号に
  GPIO.setup(18, GPIO.OUT) 
  GPIO.setup(23, GPIO.OUT)
  GPIO.setup(24, GPIO.OUT)
  p0 = GPIO.PWM(18, 50)
  p1 = GPIO.PWM(23, 50)
  p2 = GPIO.PWM(24, 50)

  p0.start(0)
  p1.start(0)
  p2.start(0)
  while True:
    if(color[0]):
      GPIO.output(24, GPIO.HIGH) 
      sleep(1 if mode == 1 else 0.5) # 0.5秒待つ
      GPIO.output(24, GPIO.LOW) 
      sleep(1 if mode == 1 else 0.5) # 0.5秒待つ
    elif(color[1]):
      GPIO.output(23, GPIO.HIGH) 
      sleep(1 if mode == 1 else 0.5) # 0.5秒待つ
      GPIO.output(23, GPIO.LOW) 
      sleep(1 if mode == 1 else 0.5) # 0.5秒待つ
    else:
      GPIO.output(18, GPIO.HIGH) 
      sleep(1 if mode == 1 else 0.5) # 0.5秒待つ
      GPIO.output(18, GPIO.LOW) 
      sleep(1 if mode == 1 else 0.5) # 0.5秒待つ

try:
    while True:
        inputVal0 = analog_read(0)
        duty0 = inputVal0 * 100 / 4095
        inputVal1 = analog_read(1)
        duty1 = inputVal1 * 100 / 4095
        inputVal2 = analog_read(2)
        duty2 = inputVal2 * 100 / 4095
        p0.ChangeDutyCycle(duty0)
        p1.ChangeDutyCycle(duty1)
        p2.ChangeDutyCycle(duty2)
        sleep(0.2)

    
    # HIGH, LOWをちゃんと制御するか，PWMで制御するのもありかもしれない
    #if quit_flag.value: # 点or滅が終わったらチェックして終了（これは放置）
    #  break

if __name__ == "__main__": # テストするならif文内に
  led_brink(None, 0.6, 1, [1,0,0]) 
