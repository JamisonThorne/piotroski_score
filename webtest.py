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
    driver = init_driver('/home/jonsnow/my_stockproject/chromedriver-Linux64')
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
    WebDriverWait(driver, 10).until(EC.title_contains("from Morningstar.com"))
    recent_operating_cashflow = driver.find_element_by_xpath('//*[@id="financials"]/table/tbody/tr[22]/td[10]').text
    recent_gross_margin = driver.find_element_by_xpath('//*[@id="tab-profitability"]/table[1]/tbody/tr[6]/td[10]').text
    previous_gross_margin = driver.find_element_by_xpath('//*[@id="tab-profitability"]/table[1]/tbody/tr[6]/td[9]').text
    recent_shares = driver.find_element_by_xpath('//*[@id="financials"]/table/tbody/tr[18]/td[10]').text
    previous_shares = driver.find_element_by_xpath('//*[@id="financials"]/table/tbody/tr[18]/td[9]').text

    #Efficiency turnover tab
    click_checker(driver, '//*[@id="keyStatWrap"]/div/ul/li[5]/a')

    recent_asset_turnover = driver.find_element_by_xpath('//*[@id="tab-efficiency"]/table/tbody/tr[16]/td[10]').text
    previous_asset_turnover = driver.find_element_by_xpath('//*[@id="tab-efficiency"]/table/tbody/tr[16]/td[9]').text

    #Financials Page > Income Statement
    click_checker(driver, '/html/body/div[1]/div[3]/div[1]/div/ul[2]/li[6]/a')

    recent_net_income = driver.find_element_by_xpath('//*[@id="data_i80"]/div[@id="Y_6"]').get_attribute("rawvalue")
    previous_net_income = driver.find_element_by_xpath('//*[@id="data_i80"]/div[@id="Y_5"]').get_attribute("rawvalue")

    #Financials Page > Balance Sheet
    click_checker(driver, '/html/body/div[1]/div[3]/div[1]/div[1]/div/ul[3]/li[2]/a')

    recent_total_current_assets = driver.find_element_by_xpath('//*[@id="data_ttg1"]/div[@id="Y_5"]').get_attribute(
        "rawvalue")
    previous_total_current_assets = driver.find_element_by_xpath('//*[@id="data_ttg1"]/div[@id="Y_4"]').get_attribute(
        "rawvalue")
    recent_total_assets = driver.find_element_by_xpath('//*[@id="data_tts1"]/div[@id="Y_5"]').get_attribute("rawvalue")
    previous_total_assets = driver.find_element_by_xpath('//*[@id="data_tts1"]/div[@id="Y_4"]').get_attribute("rawvalue")
    recent_total_current_liabilities = driver.find_element_by_xpath('//*[@id="data_ttgg5"]/div[@id="Y_5"]').get_attribute(
        "rawvalue")
    previous_total_current_liabilities = driver.find_element_by_xpath(
        '//*[@id="data_ttgg5"]/div[@id="Y_4"]').get_attribute("rawvalue")
    recent_total_liabilities = driver.find_element_by_xpath('//*[@id="data_ttg5"]/div[@id="Y_5"]').get_attribute(
        "rawvalue")
    previous_total_liabilities = driver.find_element_by_xpath('//*[@id="data_ttg5"]/div[@id="Y_4"]').get_attribute(
        "rawvalue")

def click_checker(driver, click_element):
    try:
        driver.find_element_by_xpath(click_element).click()
    except Exception as e:
        logger.error("Something bad happened when hitting morningstar: {name} - {error} - %{num}d"
                     .format(error=e, name="Jamison",num=10))
    #Wait until main title for webpage appears
    WebDriverWait(driver, 10).until(EC.title_contains("from Morningstar.com"))

if __name__ == '__main__':
    main()