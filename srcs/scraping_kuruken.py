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


def sort_bus_data(bus_data_list):
  return sorted(bus_data_list, lambda x: float('inf') if x[-1] is None else x[-1])

def find_bus_data(page_source):
  daiya_list = BeautifulSoup(page_source, "html.parser").find(id="approach_list_for_daiya")
  bus_datas = []
  for daiya in daiya_list.find_all("li", limit=3):
    (time, course_name, delay_minutes) = daiya.tr("td") # 1列目には到着時刻，目的(経由)地，残り時間が示される find_all
    bus_datas.append((
      time.text.strip(), 
      course_name.a.text, 
      dict(enumerate(getattr(course_name.div, "stripped_strings", [None]))).get(1), # course_name.div.stringが存在しないならNone (経由地が存在しない)
      '1' if "soon" in delay_minutes["class"] else dict(enumerate(delay_minutes.div.stripped_strings)).get(1), # 存在しないときにNoneにさせたい
    )) # (到着時刻，目的地，経由地，目標時間) 
  return bus_datas

def scraping_kuruken(sites):
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
  return [sort_bus_data(find_bus_data(page_source)) for page_source in page_sources]

if __name__ == "__main__": # テストするならこのif文の中で
  print(scraping_kuruken(["https://kuruken.jp/Approach?sid=8cdf9206-6a32-4ba9-8d8c-5dfdc07219ca&noribaChange=1"]))
  # from requests_html import HTMLSession
  # session = HTMLSession()
  # url = "https://it-syoya-engineer.com/hello-world/"
  # r = session.get(url)
  # print(r.html.render())
