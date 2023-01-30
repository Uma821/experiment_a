import spidev
from time import sleep
import RPi.GPIO as GPIO
import port_assign            # 何番ポートか参照

def pir_sensing(): # 人感センサーで人を確認
  # 第二回資料を参照のこと
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(port_assign.PIR_PORT, GPIO.IN)
  
  if GPIO.input(port_assign.PIR_PORT): # HIGH or LOW
    # print("PIR: Ture")
    return True
  else:
    print("PIR: False")
    return False # 気配がある時はTrue ない時はFalse

  GPIO.cleanup()

if __name__ == "__main__": # テストするならif文内に
  for _ in range(50):
    pir_sensing()
    sleep(0.5)
