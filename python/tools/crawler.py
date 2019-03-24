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
    self.xpath = xpath
    self.pics = []
    self.directory = directory
    self.total = 1
    self.__stop = False

    if not os.path.exists(directory):
      os.makedirs(directory)

  SCROLL_DOWN = 'document.documentElement.scrollTop={}'

  def wait(self, t: int = 1):
    time.sleep(t)

  def wait_ready(self):
    state = ''
    while state != 'complete':
      self.wait()
      state = self.driver.execute_script('return document.readyState')

  RETRY_TIMES = 10

  def fetch(self, text: str, number: int):
    def __fetch(text: str, number: int):
      for t in range(Crawler.RETRY_TIMES):
        try:
          self.driver.maximize_window()
          self.driver.get(self.site.format(text))
          self.wait_ready()
          break
        except:
          if t < Crawler.RETRY_TIMES:
            print(f'retry... [{t}/{Crawler.RETRY_TIMES}]')
          else:
            print(f'{t} times error... stop, please check internet connection')
            return
      pos = 0
      self.total = 1
      while self.total < number:
        pos += 500
        self.driver.execute_script(Crawler.SCROLL_DOWN.format(pos))
        while True:
          try:
            e = self.driver.find_element_by_xpath(self.xpath.format(self.total))
            self.pics.append(e.get_attribute('src'))
            self.total += 1
          except:
            break
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
      print(f'{count}/{self.total}: {url}')
      try:
        result = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        if result.status_code == 200:
          with open(f'{self.directory}/{count}.jpg', 'wb') as f:
            result.raw.decode_content = True
            shutil.copyfileobj(result.raw, f)
      except KeyboardInterrupt:
        print('stop...')
        break
      except Exception as e:
        print(e)
        return
      count += 1
    self.__stop = False

  def quit(self):
    self.driver.quit()

params = [
  {
    'site': r'https://stocksnap.io/search/{}',
    'xpath': r'//*[@id="main"]/a[{}]/img',
    'directory': 'imgs/{}/stocksnap',
  },
  {
    'site': r'https://visualhunt.com/search/instant/?q={}',
    'xpath': r'//*[@id="layout"]/div[3]/div/div[1]/div[{}]/a[1]/img',
    'directory': 'imgs/{}/visualhunt',
  },
]

def main(search: str, number: int):
  for param in params:
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
  if len(argv) == 3:
    search = argv[1]
    number = int(argv[2])
    if len(search) != 0 and number > 0:
      main(search, number)
