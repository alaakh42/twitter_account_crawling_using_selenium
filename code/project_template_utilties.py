from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import datetime


def init_driver(browser= "htmlunit"):
    if browser == "htmlunit":
        driver = webdriver.Remote(
           command_executor='http://127.0.0.1:4444/wd/hub',
           desired_capabilities=DesiredCapabilities.HTMLUNIT)
        driver.implicitly_wait(3) # implicit waits to reduce chance of timeouts
    if browser == "chrome":
        driver = webdriver.Chrome("../selenium_server&chrome_driver/chromedriver")
#        driver = webdriver.Remote(
#           command_executor='http://127.0.0.1:4444/wd/hub',
#           desired_capabilities=DesiredCapabilities.CHROME)
    # set a default wait time for the browser [5 seconds here]:
#    driver.wait = WebDriverWait(driver, 1)
    return driver
    
def close_driver(driver):
    # close the driver
    driver.close()

def format_day(date):
    day = '0' + str(date.day) if len(str(date.day)) == 1 else str(date.day) # put day in format 01 & 24
    month = '0' + str(date.month) if len(str(date.month)) == 1 else str(date.month) # put month in format 03 & 11
    year = str(date.year)
    return '-'.join([year, month, day])

def form_url(since, until, user="saudigosi", user_='SA'):#tweets_type='specific',
#    if (tweets_type  == 'specific'):
    user = user.lower()
    p1 = 'https://twitter.com/search?f=tweets&vertical=default&q=from%3A'
    p2 =  user + '%20since%3A' + since + '%20until%3A' + until + 'include%3Aretweets&src=typd'
#    elif (tweets_type == 'general'):
#        user = user_.lower()
#        p1 = "https://twitter.com/search?f=tweets&vertical=default&l=ar&"
#        p2 = "q=near%3A\"Jeddah%2C%20Kingdom%20of%20Saudi%20Arabia\"%20within%3A150mi"+"%20since%3A"+since+"%20until%3A"+until+"&src=typd&lang=en"
    return p1 + p2

def increment_day(date, i):
    return date + datetime.timedelta(days=i)
     