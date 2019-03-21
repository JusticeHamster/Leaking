import re
import shutil
import os
import multiprocessing
import selenium.webdriver
import requests
import time

class Crawler(object):
  def __init__(self, site: str):
    self.site = site
    self.driver = selenium.webdriver.Chrome()

    self.__content = None
    self.__result = None
    self.__dir = '.'

  @property
  def content(self):
    return self.__content

  @content.setter
  def content(self, new: str):
    self.__content = new

  @property
  def result(self):
    return self.__result

  @result.setter
  def result(self, new: list):
    self.__result = new

  SCROLL_UP = 'window.scrollTo(0, -100);'
  SCROLL_DOWN = 'window.scrollTo(0, document.body.scrollHeight);'

  def wait_ready(self):
    state = ''
    while state != 'complete':
      time.sleep(1)
      state = self.driver.execute_script('return document.readyState')

  def wait(self, t: int = 1):
    time.sleep(t)

  def fetch(self, text: str, number: int):
    print('fetching...')
    self.driver.get(self.site.format(text))
    self.wait_ready()
    for i in range(number):
      self.wait(1)
      self.driver.execute_script(Crawler.SCROLL_UP)
      self.wait(2)
      self.driver.execute_script(Crawler.SCROLL_DOWN)
      print(f'{i * 100 / number:.2f}%')
    self.content = self.driver.page_source
    self.driver.close()

  '''
    参考
    https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/
  '''
  def analyse(self, pattern: str):
    print('analysing...')
    if self.content is None:
      return
    '''
      参考：
      https://www.cnblogs.com/zhaof/p/6930955.html
    '''
    self.result = re.compile(pattern).findall(self.content)

  def download_one(self, url, name):
    try:
      result = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
      if result.status_code == 200:
        with open(f'{self.__dir}/{name}.jpg', 'wb') as f:
          result.raw.decode_content = True
          shutil.copyfileobj(result.raw, f)
    except KeyboardInterrupt as k:
      raise k
    except Exception as e:
      print(e)

  '''
    pickleable
  '''
  def __call__(self, un):
    return self.download_one(un[0], un[1])

  '''
    并行化
  '''
  def download(self, directory: str, workers: int = 1):
    print('downloading...')
    if self.result is None:
      return
    if not os.path.exists(directory):
      os.mkdir(directory)
    self.__dir = directory
    if workers == 1:
      for url, name in self.result:
        try:
          self.download_one(url, name)
        except KeyboardInterrupt:
          print('stopping')
          return 
    else:
      pool = multiprocessing.Pool(workers)
      pool.map_async(self, self.result)
      pool.close()
      pool.join()

  def quit(self):
    self.driver.quit()

DIR = 'imgs/'

def main(search: str, number: int, workers: int):
  crawler = Crawler(r'https://visualhunt.com/search/instant/?q={}')
  crawler.fetch(search, number)
  crawler.analyse(r'(https://visualhunt\.com/photos/\d+/(.+?)\.jpg\?s=s)')
  if not os.path.exists(DIR):
    os.mkdir(DIR)
  crawler.download(DIR + search, workers=workers)
  crawler.quit()

if __name__ == '__main__':
  import sys
  argv = sys.argv
  search = argv[1]
  number = int(argv[2])
  workers = int(argv[3])
  if len(argv) == 4 and len(search) != 0 and number > 0 and workers > 0:
    main(search, number, workers)
