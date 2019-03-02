import requests
import re
import shutil
import os

class Crawler:
  def __init__(self, site: str):
    self.__content = None
    self.__result = None
    self.site = site

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

  def download(self, directory: str):
    print('downloading...')
    if self.result is None:
      return
    if not os.path.exists(directory):
      os.mkdir(directory)
    for url, name in self.result:
      try:
        result = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        if result.status_code == 200:
          with open(f'{directory}/{name}.jpg', 'wb') as f:
            result.raw.decode_content = True
            shutil.copyfileobj(result.raw, f)
      except requests.HTTPError as httpError:
        print(httpError)
      except KeyboardInterrupt as key:
        print('stopping...')
        return

if __name__ == '__main__':
  crawler = Crawler(r'https://visualhunt.com/search/instant/?q={}')
  crawler.fetch('fire')
  crawler.analyse(r'(https://visualhunt\.com/photos/\d+/(.+?)\.jpg\?s=s)')
  crawler.download('imgs')
