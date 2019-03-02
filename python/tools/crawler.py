import requests
import re
import shutil
import os
import multiprocessing

class Crawler(object):
  def __init__(self, site: str):
    self.site = site

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

  def fetch(self, text: str):
    print('fetching...')
    try:
      response = requests.get(self.site.format(text), headers={'User-agent': 'Mozilla/5.0'})
      if response.status_code == 200:
        self.content = response.text
    except Exception as e:
      print(e)

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
    except requests.HTTPError as httpError:
      print(httpError)

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

if __name__ == '__main__':
  crawler = Crawler(r'https://visualhunt.com/search/instant/?q={}')
  crawler.fetch('fire')
  crawler.analyse(r'(https://visualhunt\.com/photos/\d+/(.+?)\.jpg\?s=s)')
  crawler.download('imgs', workers=5)
