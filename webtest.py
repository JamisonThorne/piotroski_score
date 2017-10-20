import logging
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def main():
    args = parse_args()
    logging.basicConfig(format='%(asctime)s - %(name)s : %(levelname)s - %(lineno)d: %(message)s',
                        level=logging.DEBUG if args.verbose else logging.INFO)
    
    global logger
    logger = logging.getLogger("webscraper")
    #Change Chrome Driver Path as Needed
    #Ubunto Users (see tytus's comments):
    #https://stackoverflow.com/questions/22476112/using-chromedriver-with-selenium-python-ubuntu
    driver = init_driver('/home/jonsnow/my_virtualenv/chromedriver-Linux64')
    stock = "AMD"
    Parse(driver, stock)
    driver.close()


def init_driver(web_driver_location):
    driver = webdriver.Chrome(executable_path=web_driver_location)
    driver.wait = WebDriverWait(driver, 5)
    return driver

"""
Parse command line arguments
"""
def parse_args():
    parser = argparse.ArgumentParser(description='Webscraper application')
    parser.add_argument('-v','--verbose',help='Verbose logging',action="store_true")
    return parser.parse_args()

'''
Parse driver content for stock data
>>>Parse(driver, empty)

'''
def Parse(driver, stock):
    logger.debug("Starting Parse method")
    try:
        driver.get('http://financials.morningstar.com/ratios/r.html?t={stock_var}'.format(stock_var=stock))
    except Exception as e:
        logger.error("Something bad happened when hitting morningstar: {name} - {error} - %{num}d"
                     .format(error=e, name="Jamison",num=10))
    logger.debug("URL pinged")
    
    # Operating Cash Flow - Most Recent
    WebDriverWait(driver, 10).until(EC.title_contains("from Morningstar.com"))
    recentoperatingcashflow = driver.find_element_by_xpath('//*[@id="financials"]/table/tbody/tr[22]/td[10]').text
    logger.info(recentoperatingcashflow)

if __name__ == '__main__':
    main()