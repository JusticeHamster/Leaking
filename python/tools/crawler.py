import os
import selenium.webdriver
import requests
import shutil
import threading
import time

class Crawler(object):
  def __init__(self, site: str, xpath: str, directory: str):
    self.site = site
    self.driver = selenium.webdriver.Chrome()
    self.xpath, self.xpath_count = xpath
    self.pics = []
    self.directory = directory
    self.total = 1
    self.__stop = False

    if not os.path.exists(directory):
      os.makedirs(directory)

  def wait(self, t: int = 1):
    time.sleep(t)

  def wait_ready(self):
    while True:
      self.wait()
      if self.driver.execute_script('return document.readyState') == 'complete':
        break

  SCROLL_DOWN = 'document.documentElement.scrollTop={}'
  TRY_TIME = 10

  def fetch(self, text: str, number: int):
    def __fetch(text: str, number: int):
      self.driver.maximize_window()
      self.driver.get(self.site.format(text))
      self.wait_ready()
      pos = 0
      self.total = 1
      indexes = [1] * self.xpath_count
      try_time = 0
      while self.total < number and try_time < Crawler.TRY_TIME:
        pos += 500
        self.driver.execute_script(Crawler.SCROLL_DOWN.format(pos))
        curr_index = self.xpath_count - 1
        while True:
          try:
            e = self.driver.find_element_by_xpath(self.xpath.format(*indexes))
            self.pics.append(e.get_attribute('src'))
            try_time = 0
            self.total += 1
            indexes[-1] += 1
          except:
            if curr_index > 0:
              indexes[curr_index] = 1
              curr_index -= 1
              indexes[curr_index] += 1
            else:
              break
        try_time += 1
        self.wait(10)
      self.driver.close()
    try:
      __fetch(text, number)
    except Exception as e:
      print(e)
    finally:
      self.__stop = True

  def download(self):
    count = 1
    while True:
      while len(self.pics) == 0:
        if self.__stop:
          break
        self.wait(5)
      if self.__stop and len(self.pics) == 0:
        break
      url = self.pics.pop(0)
      img_path = f'{self.directory}/{count}.jpg'
      if os.path.exists(img_path):
        print(f'{img_path} already exists.')
      else:
        print(f'{count}/{self.total}: {url}')
        try:
          result = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'}, timeout=60)
          if result.status_code == 200:
            with open(img_path, 'wb') as f:
              result.raw.decode_content = True
              shutil.copyfileobj(result.raw, f)
        except KeyboardInterrupt:
          print('stop...')
          break
        except Exception as e:
          print(e)
      count += 1
    self.__stop = False

  def quit(self):
    self.driver.quit()

params = [
  {
    'site': r'https://stocksnap.io/search/{}',
    'xpath': [r'//*[@id="main"]/a[{}]/img', 1],
    'directory': 'imgs/{}/stocksnap',
  },
  {
    'site': r'https://visualhunt.com/search/instant/?q={}',
    'xpath': [r'//*[@id="layout"]/div[3]/div/div[1]/div[{}]/a[1]/img', 1],
    'directory': 'imgs/{}/visualhunt',
  },
  {
    'site': r'',
    'xpath': [
      r'/html/body/div[2]/div/div[1]/div/div[1]/div[1]/div[3]/div/div/div/div/div[1]/div/div/div[1]/div[{}]/div/div/div/div/div/div[1]/a/div[1]/div[1]/div/div/div/div/img',
      1
    ],
    'directory': 'imgs/{}/pinterest',
  },
#  {
#    'site': r'http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word={}',
#    'xpath': [r'//*[@id="imgid"]/div[{}]/ul/li[{}]/div/a/img', 2],
#    'directory': 'imgs/{}/baidu',
#  },
]

def main(searches: list, number: int):
  for search in searches:
    if len(search) == 0:
      continue
    for param in params:
      param = param.copy()
      param['directory'] = param['directory'].format(search)
      crawler = Crawler(**param)
      fetch = threading.Thread(target=crawler.fetch, args=(search, number, ))
      download = threading.Thread(target=crawler.download)
      fetch.start()
      download.start()
      fetch.join()
      download.join()
      crawler.quit()

if __name__ == '__main__':
  import sys
  argv = sys.argv
  if len(argv) >= 3:
    number = int(argv[1])
    search = argv[2:]
    if number > 0:
      main(search, number)
