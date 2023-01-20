import time, sys # これは消さないし，絶対最初に置いとく
sys.dont_write_bytecode = True # これは消さない，絶対最初に置いとく
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import platform
from bs4 import BeautifulSoup


def find_bus_data(page_source):
  daiya_list = BeautifulSoup(page_source, "html.perser").find(id="approach_list_for_daiya")
  for daiya in daiya_list.find_all("li"):
    daiya
  return [()] # (後なん分，時間，目標時間) 

def scraping_kuruken(sites):
  options = Options()
  options.add_argument('--headless')

  if platform.system() == "Linux" and platform.machine() == "armv7l":  
    # if raspi(linux 32bitはwebdriver_manager非対応)
    options.BinaryLocation = ("/usr/bin/chromium-browser") # chromium使用
    service = Service("/usr/bin/chromedriver")
  else: # not raspi and use Chrome
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())

  driver = webdriver.Chrome(options=options, service=service)
  return [[driver.get(site), time.sleep(20), driver.page_source][2] for site in sites]

if __name__ == "__main__": # テストするならこのif文の中で
  print(scraping_kuruken(["https://kuruken.jp/Approach?sid=8cdf9206-6a32-4ba9-8d8c-5dfdc07219ca&noribaChange=1"]))
  # from requests_html import HTMLSession
  # session = HTMLSession()
  # url = "https://it-syoya-engineer.com/hello-world/"
  # r = session.get(url)
  # print(r.html.render())
