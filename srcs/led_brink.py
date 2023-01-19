import port_assign # 何番ポートか参照
from time import sleep

def led_brink(quit_flag, pwm, mode, color): # LED
  # pwmの値が高いと
  # mode=1なら1秒ごとに点滅切り替え, 2なら0.5秒ごとに点滅切り替え
  # color=[R, G, B] どれかがTrueになっているはず

  while True:
    # HIGH, LOWをちゃんと制御するか，PWMで制御するのもありかもしれない
    sleep(0.5) # 適当に書き換えて
    if quit_flag.value: # 点or滅が終わったらチェックして終了（これは放置）
      break

if __name__ == "__main__": # テストするならif文内に
  pass
