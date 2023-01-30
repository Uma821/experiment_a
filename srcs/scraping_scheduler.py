import sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
import urlconfig, queue
from threading import Timer, Thread
from time import sleep
from sqlite_manage import find_cursor_people
from scraping_kuruken import scraping_kuruken
from line_commu import send_line_message

FORCE_SCRAPING_INTERVAL = 10 # 必要がなくてもスクレイピングして様子を見るインターバル

def scraper_caller(urls_queue, scheduling_dict):
  while True:
    urls = urls_queue.get()
    bus_datas = scraping_kuruken(urls)
    for url, bus_scraping_data in zip(urls, bus_datas):
      scheduling_dict[url][1] = bus_scraping_data
      scheduling_dict[url][2] = 0 # スクレイピング完了
    urls_queue.task_done()

def gen_scraping_urls(scheduling_dict):
  scraping_urls = []
  for url,(current_set, bus_data, scraping_space) in scheduling_dict.items():
    if not current_set: continue # このデータを必要とする人がいない
    if bus_data is None or not bus_data.approach_list:
      if scraping_space == FORCE_SCRAPING_INTERVAL: # バスデータがないとき、一定時間調査してなければ調査させる
        scraping_urls.append(url)
      continue
    if int(bus_data.approach_list[0][-1]) in [0,1,2,4,6]: # 一番早く来るバスが、後0,1,2,4,6分後に来るらしいとき、一回チェックする
      scraping_urls.append(url)
  return scraping_urls

def scheduler_check_DB(): # データベースの値を読み取る(たまに更新されてるかもしれないので今は1分毎に確認するようにしてる(排他制御は大丈夫かわからん))
  cursor_dict = {urlconfig.OUTBOUND_URL:{0}, urlconfig.INBOUND_URL:{0}} # 今注目している人がいるか(userIDの集合、0はラズパイ自身)
  find_cursor_people(cursor_dict)

  for url in scraping_scheduler.scheduling_dict: # もともと収集中
    scraping_scheduler.scheduling_dict[url][0] = cursor_dict.get(url, {}) # todo:注目する人がいないなら、そのアイテム削除
  for url in cursor_dict.keys() - scraping_scheduler.scheduling_dict.keys(): # 新規追加
    scraping_scheduler.scheduling_dict[url] = [cursor_dict[url],None,FORCE_SCRAPING_INTERVAL] # スクレイピング必要

def scraping_scheduler_init():
  # (人数, データ) # 1人以上ならスクレイピングを定期的に行う必要がある # 文字列の共有ならできそうだが、タプルは無理そうなのでとりあえずthreadingでやらせる
  scraping_scheduler.scheduling_dict = {
      urlconfig.OUTBOUND_URL: [{0},None,FORCE_SCRAPING_INTERVAL], # スクレイピングさせる
      urlconfig.INBOUND_URL : [{0},None,FORCE_SCRAPING_INTERVAL]  # 必要としてる人のUserIDの集合とした(ラズパイは0)
    }

def send_line_management_caller():
  send_line_management_caller.timer = Timer(10, send_line_management_caller)
  send_line_management_caller.timer.start()
  send_line_management()

def send_line_management():
  for url, (current_set,bus_data,scraping_space) in scraping_scheduler.scheduling_dict.items():
    # 注目されてない、まだスクレイピングされてない
    if not (current_set-{0}) or bus_data is None: continue
    for approach_list in bus_data.approach_list:
      if approach_list[-1] == 5: # 先頭要素じゃなくてもいいからバス停車5分前にlineする
        send_id = {userid for userid in current_set-{0} if send_line_management.isSended.get((url, userid),False) == False}
        send_line_message(approach_list, send_id) # 0番はラズパイ自身なので該当しない
        for userid in send_id:
          send_line_management.isSended[(url, userid)] = True # DBから追加されるタイミングの影響で微妙に通知するタイミングが異なったとしても、最終的に全部Trueになると予想する
        break
    else: # (一回そのバスの分の通知を行い、)そのバスは通り過ぎた
      for userid in current_set-{0}:
        send_line_management.isSended[(url, userid)] = False # また通知できる

def scraping_scheduler():
  urls_queue = queue.Queue() # 同期キューの作成

  try:
    thread = Thread(target=scraper_caller, args=(urls_queue, scraping_scheduler.scheduling_dict), daemon=True) # デーモンスレッドでプロセス終了時に勝手に終わらせる
    thread.start()
    send_line_management.isSended={}
    send_line_management_caller()

    while True:
      scheduler_check_DB()
      urls_queue.put(gen_scraping_urls(scraping_scheduler.scheduling_dict))

      sleep(60) # 大体1分経ったとき(常のスクレイピングするわけではないのでそもそも精度は低い)
      for url, (current_set,bus_data,scraping_space) in scraping_scheduler.scheduling_dict.items():
        scraping_scheduler.scheduling_dict[url][2] += 1 # スクレイピングせず更に1分経過
        if bus_data is None: continue
        for approach_list in bus_data.approach_list:
          if approach_list[-1] not in [0,6]: # 0に1分引かれるとスクレイピングされなくなる&5分前通知なので6分のときはスクレイピングして残り5分を得たい
            approach_list[-1] -= 1

  except KeyboardInterrupt:
    print("只今終了処理中です...")
    send_line_management_caller.timer.cancel()
    urls_queue.join() # キューに入れたすべてのアイテムが消費されるまで待つ
    raise KeyboardInterrupt
