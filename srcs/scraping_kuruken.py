import time, sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import platform
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class Bus_scraping_data:
  depart_stop: str
  approach_list: list[str,str,str,str]


def sort_bus_data(bus_data_list): # Noneの場合補完するようになったが、そのままにしている
  return sorted(bus_data_list, key=lambda x: float('inf') if x[-1] is None else float(x[-1]))

def complement_delay_time(bus_scraping_data): # 3つ分のバス時刻を取得
  from datetime import datetime, timedelta, timezone
  # JSTタイムゾーンを作成
  jst = timezone(timedelta(hours=9), 'JST')

  for approach_list in bus_scraping_data:
    arrive_arrangement = datetime.now(jst).replace(hour=int(approach_list[0][0:-3]), minute=int(approach_list[0][-2:]))-datetime.now(jst) # 予定到着時間
    approach_list[-1] = arrive_arrangement.seconds//60 if approach_list[-1] is None else int(approach_list[-1]) # 到着時刻がないときは到着予定時刻で代替
  return bus_scraping_data

def find_bus_data(page_source):
  bs = BeautifulSoup(page_source, "html.parser")
  daiya_list = bs.find(id="approach_list_for_daiya")
  bus_datas = []
  for daiya in daiya_list.find_all("li", limit=3):
    (time, course_name, delay_minutes) = daiya.tr("td") # 1列目には到着時刻，目的(経由)地，残り時間が示される find_all
    bus_datas.append([
      time.text.strip(), 
      course_name.a.text, 
      dict(enumerate(getattr(course_name.div, "stripped_strings", [None]))).get(1), # course_name.div.stringが存在しないならNone (経由地が存在しない)
      '1' if "soon" in delay_minutes["class"] else dict(enumerate(delay_minutes.div.stripped_strings)).get(1), # 存在しないときにNoneにさせたい
    ]) # (到着時刻，目的地，経由地，目標時間)
  return Bus_scraping_data(bs.find(id="keywordDepartText").string, sort_bus_data(complement_delay_time(bus_datas))) # Noneを補完した後ソートする

def scraping_kuruken(sites):
  print(f"scraping {len(sites)}sites")
  options = Options()
  options.add_argument('--headless')

  if platform.system() == "Linux" and platform.machine() == "armv7l":  
    # if raspi(linux 32bitはwebdriver_manager非対応)
    options.BinaryLocation = ("/usr/bin/chromium-browser") # chromium使用
    service = Service("/usr/bin/chromedriver")             # chromedriverを別途ダウンロードする
  else: # not raspi and use Chrome
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(options=options, service=service)

  # 最大の読み込み時間を設定 今回は最大30秒待機できるようにする
  wait = WebDriverWait(driver=driver, timeout=30)

  page_sources = []
  for site in sites:
    driver.get(site)
    wait.until(EC.presence_of_element_located((By.ID, "approach_list_for_daiya"))) # sleepは使わず，ダイヤリストが検出できるまで待機するようにした
    page_sources.append(driver.page_source)
  
  driver.quit() # 終了処理(Chromeの場合)
  return [find_bus_data(page_source) for page_source in page_sources]

if __name__ == "__main__": # テストするならこのif文の中で
  print(scraping_kuruken(["https://kuruken.jp/Approach?sid=8cdf9206-6a32-4ba9-8d8c-5dfdc07219ca&noribaChange=1"]))
  # from requests_html import HTMLSession
  # session = HTMLSession()
  # url = "https://it-syoya-engineer.com/hello-world/"
  # r = session.get(url)
  # print(r.html.render())
