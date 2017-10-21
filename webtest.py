import logging
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv


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
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(executable_path=web_driver_location, chrome_options=options)
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
                     .format(error=e, name="Jamison", num=10))
    wait = WebDriverWait(driver, 5)
    wait.until(EC.title_contains("from Morningstar.com"))
    time.sleep(2)
    x_path = driver.find_element_by_xpath
    recent_operating_cashflow = x_path('//*[@id="financials"]/table/tbody/tr[22]/td[10]').text
    recent_gross_margin = x_path('//*[@id="tab-profitability"]/table[1]/tbody/tr[6]/td[10]').text
    previous_gross_margin = x_path('//*[@id="tab-profitability"]/table[1]/tbody/tr[6]/td[9]').text
    recent_shares = x_path('//*[@id="financials"]/table/tbody/tr[18]/td[10]').text
    previous_shares = x_path('//*[@id="financials"]/table/tbody/tr[18]/td[9]').text

    #Efficiency turnover tab
    human_like_click(driver, wait, '//*[@id="keyStatWrap"]/div/ul/li[5]/a')

    recent_asset_turnover = x_path('//*[@id="tab-efficiency"]/table/tbody/tr[16]/td[10]').text
    logging.info(recent_asset_turnover)
    previous_asset_turnover = x_path('//*[@id="tab-efficiency"]/table/tbody/tr[16]/td[9]').text
    logging.info(previous_asset_turnover)

    #Financials Page > Income Statement
    human_like_click(driver, wait, '/html/body/div[1]/div[3]/div[1]/div/ul[2]/li[6]/a')

    recent_net_income = x_path('//*[@id="data_i80"]/div[@id="Y_6"]').get_attribute("rawvalue")
    logging.info(recent_net_income)
    previous_net_income = x_path('//*[@id="data_i80"]/div[@id="Y_5"]').get_attribute("rawvalue")
    logging.info(previous_net_income)

    #Financials Page > Balance Sheet
    human_like_click(driver, wait, '/html/body/div[1]/div[3]/div[1]/div[1]/div/ul[3]/li[2]/a')

    recent_total_current_assets = x_path('//*[@id="data_ttg1"]/div[@id="Y_5"]').get_attribute("rawvalue")
    previous_total_current_assets = x_path('//*[@id="data_ttg1"]/div[@id="Y_4"]').get_attribute("rawvalue")
    recent_total_assets = x_path('//*[@id="data_tts1"]/div[@id="Y_5"]').get_attribute("rawvalue")
    previous_total_assets = x_path('//*[@id="data_tts1"]/div[@id="Y_4"]').get_attribute("rawvalue")
    recent_total_current_liabilities = x_path('//*[@id="data_ttgg5"]/div[@id="Y_5"]').get_attribute("rawvalue")
    previous_total_current_liabilities = x_path('//*[@id="data_ttgg5"]/div[@id="Y_4"]').get_attribute("rawvalue")
    recent_total_liabilities = x_path('//*[@id="data_ttg5"]/div[@id="Y_5"]').get_attribute("rawvalue")
    logging.info(recent_total_liabilities)
    previous_total_liabilities = x_path('//*[@id="data_ttg5"]/div[@id="Y_4"]').get_attribute("rawvalue")
    logging.info(previous_total_liabilities)


def human_like_click(driver, wait, click_xpath):
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, click_xpath)))
        wait.until(EC.element_to_be_clickable((By.XPATH, click_xpath)))
        driver.find_element_by_xpath(click_xpath).send_keys("\n")
        time.sleep(2)
        wait.until(EC.title_contains("from Morningstar.com"))
    except Exception as e:
        logger.error("Something bad happened when hitting morningstar: {name} - {error} - %{num}d"
                     .format(error=e, name="Jamison",num=20))


if __name__ == '__main__':
    main()