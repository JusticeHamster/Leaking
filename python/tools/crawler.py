import os
import selenium.webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import pyautogui
import requests
import shutil
import threading
import time
import binascii
from xpinyin import Pinyin
pinyin = Pinyin()

DELAY = 0.1

class Crawler(object):
  def __init__(
        self, site: str, xpath: list, directory: str,
        name: str, close: list = None,
        wait: bool = False, save_type: str = 'url'
      ):
    self.name = name
    self.site = site
    self.driver = selenium.webdriver.Chrome()
    self.xpath, self.xpath_count = xpath
    self.pics = []
    self.directory = directory
    self.total = 1
    self.wait_key = wait
    self.save_type = save_type
    self.close_xpath = close
    self.__stop = False

    if not os.path.exists(directory):
      os.makedirs(directory)

  def wait(self, t: int = 1):
    if t <= 0:
      return
    time.sleep(t)

  def wait_ready(self):
    while True:
      self.wait()
      if self.driver.execute_script('return document.readyState') == 'complete':
        break

  SCROLL_DOWN   = 'document.documentElement.scrollTop={}'
  SCROLL_BOTTOM = 'window.scrollTo(0, document.body.scrollHeight);'
  SCROLL_CENTER = '''var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
var elementTop = arguments[0].getBoundingClientRect().top;
window.scrollBy(0, elementTop - viewPortHeight / 3);'''
  SAVE_AS = [*(['down'] * 7), 'enter']
  INDEX_TRY_TIME = 10
  TRY_TIME = 20

  def close_dialog(self):
    if not self.close_xpath:
      return
    for xpath in self.close_xpath:
      try:
        e = self.driver.find_element_by_xpath(xpath)
      except:
        pass
      else:
        if not e.is_displayed():
          continue
        e.click()

  def fetch(self, text: str, number: int):
    def __fetch(text: str, number: int):
      if self.save_type != 'click':
        self.driver.maximize_window()
      self.driver.get(self.site.format(text))
      self.wait_ready()
      if self.wait_key:
        input('enter to continue')
      pos = 0
      self.total = 1
      indexes = [1] * self.xpath_count
      try_time = 0
      while self.total < number and try_time < Crawler.TRY_TIME:
        if self.save_type == 'screenshot':
          pos += 500
          self.driver.execute_script(Crawler.SCROLL_DOWN.format(pos))
        while self.total < number and try_time < Crawler.TRY_TIME:
          try:
            e = self.driver.find_element_by_xpath(self.xpath.format(*indexes))
            if self.save_type == 'click':
              w = 1 if self.total == 1 else DELAY
              self.wait(w)
              self.close_dialog()
              selenium.webdriver.ActionChains(self.driver).move_to_element(e).context_click().perform()
              self.wait(w)
              self.close_dialog()
              pyautogui.typewrite(Crawler.SAVE_AS)
              self.wait(w)
              cntext = pinyin.get_pinyin(text, '_')
              pyautogui.typewrite(
                f'{cntext}_{self.name}_' + '_'.join(map(str, indexes)),
                interval=0.01
              )
              self.wait(w)
              pyautogui.typewrite(['enter'])
              self.wait(w)
            elif self.save_type == 'screenshot':
              self.pics.append(e)
            else:
              self.pics.append(e.get_attribute('src'))
            try_time = 0
            self.total += 1
            indexes[-1] += 1
            print(indexes)
          except StaleElementReferenceException as ex:
            print(ex)
          except NoSuchElementException:
            for i in range(self.xpath_count - 1, 0, -1):
              if indexes[i] >= Crawler.INDEX_TRY_TIME:
                indexes[i] = 1
                indexes[i - 1] += 1
                break
            else:
              indexes[-1] += 1
              try_time += 1
          except Exception as e:
            print(e)
            break
        try_time += 1
        if self.save_type != 'click':
          self.wait(10)
      print(f'({self.total} >= {number}) || ({try_time} >= {Crawler.TRY_TIME})')
      print(f'{text}: close')
      self.driver.close()
    try:
      __fetch(text, number)
    except Exception as e:
      print(e)
    finally:
      self.__stop = True

  def download(self):
    if self.save_type == 'click':
      self.__stop = False
      return
    count = 1
    while True:
      while len(self.pics) == 0:
        if self.__stop:
          break
        self.wait(5)
      if self.__stop and len(self.pics) == 0:
        break
      data = self.pics.pop(0)
      img_path = f'{self.directory}/{count}.'
      if self.save_type == 'screenshot':
        img_path += 'png'
      else:
        img_path += 'jpg'
      if os.path.exists(img_path):
        print(f'{img_path} already exists.')
        if self.save_type == 'screenshot':
          self.driver.execute_script(Crawler.SCROLL_BOTTOM)
      else:
        print(f'{count}/{self.total}', end=': ')
        def download_url(path, url):
          print(url)
          result = requests.get(
            url, stream=True,
            headers={
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'
            },
            timeout=10
          )
          if result.status_code == 200:
            with open(path, 'wb') as f:
              result.raw.decode_content = True
              shutil.copyfileobj(result.raw, f)
          else:
            print(result.status_code)
        def download_data(path, data):
          # data:image/jpeg;base64,...
          data = data[23:]
          print(len(data))
          binary_data = binascii.a2b_base64(data)
          with open(path, 'wb') as f:
            f.write(binary_data)
        def screenshot(path, element):
          self.driver.execute_script(Crawler.SCROLL_CENTER, element)
          self.wait()
          print('screenshot')
          element.screenshot(path)
        if data:
          if self.save_type == 'screenshot':
            dl = screenshot
          else:
            # 判断data是网址还是图片数据
            dl = download_data if data[:10] == 'data:image' else download_url
          if dl:
            try:
              dl(img_path, data)
            except KeyboardInterrupt:
              print('stop...')
              break
            except Exception as e:
              print(e)
          else:
            print('error type')
            break
        else:
          print('empty data')
      count += 1
    self.__stop = False

  def quit(self):
    self.driver.quit()

'''
  'stocksnap' : {
    'site': r'https://stocksnap.io/search/{0}',
    'xpath': [r'//*[@id="main"]/a[{}]/img', 1],
    'save_type': 'click',
  },
  'visualhunt' : {
    'site': r'https://visualhunt.com/search/instant/?q={0}',
    'xpath': [r'//*[@id="layout"]/div[3]/div/div[1]/div[{}]/a[1]/img', 1],
    'save_type': 'click',
  },
  'pinterest' : {
    'site': r'https://pinterest.com',
    'xpath': [r'/html/body/div[2]/div/div[1]/div/div[1]/div[1]/div[3]/div/div/div/div/div[1]/div/div/div[1]/div[{}]/div/div/div/div/div/div[1]/a/div[1]/div[1]/div/div/div/div/img', 1],
    'wait': True,
    'save_type': 'click',
  }
'''

params = {
  'baidu' : {
    'site': r'http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word={0}',
    'xpath': [r'//*[@id="imgid"]/div[{}]/ul/li[{}]/div/a/img', 2],
    'save_type': 'click',
    'close': [r'//*[@id="fb_close_x"]'],
  },
  'google' : {
    'site': r'https://www.google.com/search?tbm=isch&q={0}',
    'xpath': [r'//*[@id="rg_s"]/div[{}]/a[1]/img', 1],
    'save_type': 'click',
    'close': [r'//*[@id="smb"]'],
  },
}

def main(searches: list, number: int):
  for search in searches:
    if len(search) == 0:
      continue
    for name, param in params.items():
      crawler = Crawler(**param, directory=f'imgs/{search}/{name}', name=name)
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
