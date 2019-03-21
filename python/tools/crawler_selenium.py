import selenium.webdriver
import time

browser = selenium.webdriver.Chrome()

browser.get(r'https://visualhunt.com/search/instant/?q=fire')
js = "window.scrollTo(0, document.body.scrollHeight);"
while (True):
  if input() == 's':
    browser.execute_script(js)
browser.close() 
