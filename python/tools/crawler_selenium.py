from selenium import webdriver

browser = webdriver.Chrome()

browser.get("http://www.baidu.com")
js = "window.scrollTo(0,document.body.scrollHeight)"
browser.execute_script(js)
print(browser.page_source)
browser.close() 
