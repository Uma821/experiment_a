import port_assign # 何番ポートか参照
from time import sleep

def buzzer_ring(stop_flag): # 人感センサーで人を確認
  base_time = 0.5 # 秒
  tones_list = [
    (440, 1), # 440Hzを0.5秒
    (220, 2), # 220Hzを1秒
    ]
  for (tone, time) in tones_list:
    # HIGH, LOWをちゃんと制御するか，PWMで制御するのもありかもしれない
    if stop_flag: # 一音分終わったらチェックして終了（これは放置）
      break

if __name__ == "__main__": # テストするならif文内に
  pass
