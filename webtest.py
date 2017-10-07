import logging
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException

def main():
    args = parse_args()
    logging.basicConfig(format='%(asctime)s - %(name)s : %(levelname)s - %(lineno)d: %(message)s', level=logging.DEBUG if args.verbose else logging.INFO)
    
    global logger
    logger = logging.getLogger("webscraper")
    #Change Chrome Driver Path as Needed
    driver = init_driver('C:/Users/Jon Snow/Documents/chromedriver.exe')
    stock = "AMD"
    Parse(driver, stock)
    driver.close()

"""
Parse command line arguments
"""
def parse_args():
    parser = argparse.ArgumentParser(description='Webscraper application')
    parser.add_argument('-v','--verbose',help='Verbose logging',action="store_true")
    return parser.parse_args()

def init_driver(web_driver_location):
    driver = webdriver.Chrome(web_driver_location)
    driver.wait = WebDriverWait(driver, 5)
    return driver
'''
def wait_for_elements(driver, element_location):
    driver.wait.until(expected_conditions.presence_of_element_located(element_location))

def wait_to_click(driver, click_location):
    driver.wait.until(expected_conditions.element_to_be_clickable(click_location))
'''                   
'''
Parse driver content for stock data
>>>Parse(driver, empty)

'''
def Parse(driver, stock):
    logger.debug("Starting Parse method")
    try:
        driver.get('http://financials.morningstar.com/ratios/r.html?t={stockvar}'.format(stockvar=stock))
    except Exception as e:
        logger.error("Something bad happened when hitting morningstar: {name} - {error} - %{num}d".format(error=e, name="Jamison",num=10))
    logger.debug("URL pinged")
    
    # Operating Cash Flow - Most Recent
    RecentOperatingCashFlow = driver.find_element_by_xpath('//*[@id="financials"]/table/tbody/tr[22]/td[10]').text
    
    logger.info(RecentOperatingCashFlow)

if __name__ == '__main__':
    main()