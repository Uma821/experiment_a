import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome import service as fs
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def find_bus_data(page_source):
  return [()] # (後なん分，時間，目標時間) 

def scraping_kuruken(sites):
  options = Options()
  chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
  driver = webdriver.Chrome(options=options, service=chrome_service)
  return [find_bus_data([driver.get(site), time.sleep(1), driver.page_source][2]) for site in sites]

if __name__ == "__main__": # テストするならこのif文の中で
  print(scraping_kuruken(["https://kuruken.jp/Approach?sid=8cdf9206-6a32-4ba9-8d8c-5dfdc07219ca&noribaChange=1"]))