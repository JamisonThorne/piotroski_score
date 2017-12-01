import logging
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import pandas as pd
from urllib.request import urlopen
import urllib.error
import os.path


def main():
    args = parse_args()
    logging.basicConfig(format='%(asctime)s - %(name)s : %(levelname)s - %(lineno)d: %(message)s',
                        level=logging.DEBUG if args.verbose else logging.INFO)
    global logger
    logger = logging.getLogger("webscraper")
    if os.path.exists("stocklist.csv"):
        os.remove("stocklist.csv")
    if os.path.exists("fscore.csv"):
        os.remove("fscore.csv")
        logging.info("Delete Success")
    #gathers AMAX specific stock list
    #csv_creator("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amax&render=download",True)
    #gathers NYSE specific stock list
    #csv_creator("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download",True)
    #gathers NASDAQ specific stock list
    csv_creator("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download",True)
    #creates a dataframe containing the stocklist.csv created in the csv_creator function above
    df = pd.read_csv('stocklist.csv')
    #creates a new dataframe containing only the symbol column and associated rows
    df_new = df[~df['Symbol'].str.contains('\w+\W')]
    #creates an appendable csv file that contains two columns, Symbol from the previous line and a new F_Score column
    df_new.to_csv('fscore.csv', columns=['Symbol','F_Score'], index=True, mode='a', header=None)
    #creates a new dataframe that contains the fscore.csv file
    df_fscore = pd.read_csv('fscore.csv', names=['Symbol', 'F_Score'], nrows=2)
    #creates an empty list that will be used for storing the collected f score information for each stock
    temp = []
    #initialize webdriver
    driver = init_driver('/home/jonsnow/my_stockproject/chromedriver-Linux64')
    #iterate through the number of rows in the df_fscore dataframe
    for index, row in df_fscore.iterrows():
        # Change Chrome Driver Path as Needed
        # Ubunto Users (see tytus's comments):
        # https://stackoverflow.com/questions/22476112/using-chromedriver-with-selenium-python-ubuntu
        logging.info(index)
        logging.info(row)
        #appends the stock ticker and f score calculated from the parse function
        #parse() receives the webdriver and the stock ticker for the given row iteration via .iloc
        temp.append([df_fscore.iloc[index,0], parse(driver, df_fscore.iloc[index,0])])
    driver.close()
    #creates a dataframe using the nested list that was created in the for loop above
    df = pd.DataFrame(temp, columns=['Symbol', 'fscore'])
    #stores the created dataframe in fscore.csv overwriting the previous made file. Uses sep='\t' to separate the two
    #columns
    df.to_csv('fscore.csv', index=False, sep='\t')
    #signals the end of the code eliciting screams of triumph
    logging.info("fin")

"""
init_driver(str) -> selenium.webdriver.chrome.webdriver.WebDriver (session="unique crumb")

creates the selenium webdriver that this code will navigate through.

>>> init_driver('/home/jonsnow/my_stockproject/chromedriver-Linux64')
selenium.webdriver.chrome.webdriver.WebDriver (session="unique crumb")
"""
def init_driver(web_driver_location):
    options = Options()
    #maximizes the webdriver screen so that the entire webpage can be searched and clicked on.
    options.add_argument("--start-maximized")
    options.add_argument('--dns-prefetch-disable')
    driver = webdriver.Chrome(executable_path=web_driver_location, chrome_options=options)
    driver.wait = WebDriverWait(driver, 30)
    return driver

"""
Parse command line arguments
"""
def parse_args():
    parser = argparse.ArgumentParser(description='Webscraper application')
    parser.add_argument('-v', '--verbose', help='Verbose logging', action="store_true")
    return parser.parse_args()

"""
parse(selenium.webdriver.chrome.webdriver.WebDriver, str) -> int

navigates through the morningstar financials pages for any given stock financial data and calculates the
priotroski score.

>>> parse(driver, "AMD")
4
>>> parse(driver, "NVDA")
6
"""
def parse(driver, stock):
    logger.debug("Starting Parse method")
    try:
        #driver.get('http://www.morningstar.com/stocks/xnas/{stock_var}/quote.html'.format(stock_var=stock))
        driver.get('http://financials.morningstar.com/ratios/r.html?t={stock_var}&region=USA&culture=en_US'
                   .format(stock_var=stock))
    except Exception as e:
        logger.error("Something bad happened ed when hitting morningstar: {name} - {error} - %{num}d"
                     .format(error=e, name="Jamison", num=10))
    wait = WebDriverWait(driver, 5)
    if driver.current_url == 'http://www.morningstar.com/back_soon.html':
        return 0
    else:
        #retrieves most recent reported net income
        recent_net_income = float_converter(exception_handling_text_element('//*[@id="financials"]'
                                                                            '/table/tbody/tr[10]/td[10]', driver))
        #retrieves previous years reported net income
        previous_net_income = float_converter(exception_handling_text_element('//*[@id="financials"]'
                                                                              '/table/tbody/tr[10]/td[9]', driver))
        #retrieves most recent reported shares
        recent_shares = float_converter(exception_handling_text_element('//*[@id="financials"]'
                                                                        '/table/tbody/tr[18]/td[10]', driver))
        #retrieves previous years reported shares
        previous_shares = float_converter(exception_handling_text_element('//*[@id="financials"]'
                                                                          '/table/tbody/tr[18]/td[9]', driver))
        #retrieves most recent reported gross margin
        recent_gross_margin = float_converter(exception_handling_text_element('//*[@id="tab-profitability"]'
                                                                              '/table[1]/tbody/tr[6]/td[10]', driver))
        #retrieves previous years reported gross margin
        previous_gross_margin = float_converter(exception_handling_text_element('//*[@id="tab-profitability"]'
                                                                                '/table[1]/tbody/tr[6]/td[9]', driver))
        '''
        #clicks on efficiency turnover tab
        human_like_click(driver, wait, '//*[@id="keyStatWrap"]/div/ul/li[5]/a')
        #retrieves most recent asset turnover
        recent_asset_turnover = float_converter(exception_handling_text_element('//*[@id="tab-efficiency"]'
                                                                        '/table/tbody/tr[16]/td[10]', driver))
        #retrieves previous years asset turnover
        previous_asset_turnover = float_converter(exception_handling_text_element('//*[@id="tab-efficiency"]'
                                                                          '/table/tbody/tr[16]/td[9]', driver))
        '''
        #clicks on the financials page which takes you to the income statement
        human_like_click(driver, wait, '/html/body/div[1]/div[3]/div[1]/div/ul[2]/li[6]/a')

        #retrieves the most recent reported revenue
        recent_revenue = float_converter(exception_handling_raw_element('//*[@id="data_i1"]'
                                                                        '/div[@id="Y_5"]', driver))
        #retrieves previous years reported revenue
        previous_revenue = float_converter(exception_handling_raw_element('//*[@id="data_i1"]'
                                                                          '/div[@id="Y_4"]', driver))
        #clicks on the balance sheet page
        human_like_click(driver, wait, '/html/body/div[1]/div[3]/div[1]/div[1]/div/ul[3]/li[2]/a')
        #retrieves most recent reported total current assets
        recent_tot_current_assets = float_converter(exception_handling_raw_element('//*[@id="data_ttg1"]'
                                                                                   '/div[@id="Y_5"]', driver))
        #retrives last years reported total current assets
        previous_tot_current_assets = float_converter(exception_handling_raw_element('//*[@id="data_ttg1"]'
                                                                                     '/div[@id="Y_4"]', driver))
        #retrieves most recent reported total assets
        recent_total_assets = float_converter(exception_handling_raw_element('//*[@id="data_tts1"]'
                                                                             '/div[@id="Y_5"]', driver))
        #retrieves previous years reported total assets
        previous_total_assets = float_converter(exception_handling_raw_element('//*[@id="data_tts1"]'
                                                                               '/div[@id="Y_4"]', driver))
        #retrieves previous years previous reported total assets
        previous_previous_total_assets = float_converter(exception_handling_raw_element('//*[@id="data_tts1"]'
                                                                                        '/div[@id="Y_3"]', driver))
        #retrieves most recent reported total current liabilities
        recent_total_current_liabilities = float_converter(exception_handling_raw_element('//*[@id="data_ttgg5"]'
                                                                                          '/div[@id="Y_5"]', driver))
        #retrieves previous years reported total current liabilities
        previous_total_current_liabilities = float_converter(exception_handling_raw_element('//*[@id="data_ttgg5"]'
                                                                                            '/div[@id="Y_4"]', driver))
        #retrieves most recent reported total liabilities
        recent_long_term_debt = float_converter(exception_handling_raw_element('//*[@id="data_i50"]'
                                                                               '/div[@id="Y_5"]', driver))
        #retrieves previous years reported total liabilities
        previous_long_term_debt = float_converter(exception_handling_raw_element('//*[@id="data_i50"]'
                                                                                 '/div[@id="Y_4"]', driver))
        #clicks on the cash flow page
        human_like_click(driver, wait, '/html/body/div[1]/div[3]/div[1]/div[1]/div/ul[3]/li[3]/a')
        #retrieves most recent reported operating cash flow
        recent_operating_cash_flow = float_converter(exception_handling_raw_element('//*[@id="data_tts1"]'
                                                                                    '/div[@id="Y_6"]', driver))
        """
        The rest of this function calculates Piotroski's F-Score (a value out of 9, see the readme for this code for more
        info)
        """
        f_score = []
        recent_avg_total_assets = (recent_total_assets + previous_total_assets) / 2
        previous_avg_total_assets = (previous_total_assets + previous_previous_total_assets) / 2
        #Profitability
        #ROA - current net income / total assets - 1 if pos 0 if neg
        ROA = division_by_zero_check(recent_net_income, recent_total_assets)
        f_score.append(sign_check(ROA))
        #CFROA  - Cash Flow from operations / tot assets - 1 if pos 0 if neg
        CFO = division_by_zero_check(recent_operating_cash_flow, recent_total_assets)
        f_score.append(sign_check(CFO))
        #DeltaROA - net inc / tot asset (this year) - net inc / tot asset (last year) - 1 if pos, 0 if neg
        previous_ROA = division_by_zero_check(previous_net_income, previous_total_assets)
        DeltaROA = ROA - previous_ROA
        f_score.append(sign_check(DeltaROA))
        ACCRUAL = CFO - ROA
        #Accrual: Cash Flow From Operations Less Return on Assets : 1 if pos, 0 if neg
        f_score.append(sign_check(ACCRUAL))
        #Funding
        # DeltaLever: Gearing (last year) - Gearing (this year): Score 0 if this year's gearing is higher, 1 otherwise.
        previous_gearing = division_by_zero_check(previous_long_term_debt, previous_avg_total_assets)
        current_gearing = division_by_zero_check(recent_long_term_debt, recent_avg_total_assets)
        DeltaLever = previous_gearing - current_gearing
        f_score.append(sign_check(DeltaLever))
        # DeltaLiquid: This years current ratio less last years current ratio: Score 1 if postive, else 0
        Recent_DeltaLiquid = division_by_zero_check(recent_tot_current_assets, recent_total_current_liabilities)
        Previous_DeltaLiquid = division_by_zero_check(previous_tot_current_assets, previous_total_current_liabilities)
        DeltaLiquid = Recent_DeltaLiquid - Previous_DeltaLiquid
        f_score.append(sign_check(DeltaLiquid))
        #EQ_Offer: Last years number of shares in issue less this years. 1 if positive, else 0.
        EQ_Offer = previous_shares - recent_shares
        f_score.append(sign_check(EQ_Offer))
        #Efficiency
        #DeltaMargin: Gross Margin (this year) - Gross Margin (last year): 1 if pos, 0 if neg
        DeltaMargin = recent_gross_margin - previous_gross_margin
        f_score.append(sign_check(DeltaMargin))
        recent_delta_turn = division_by_zero_check(recent_revenue, previous_total_assets)
        previous_delta_turn = division_by_zero_check(previous_revenue, previous_previous_total_assets)
        # DeltaTurn: Year's asset turnover ratio less last year's asset turnover ratio. 1 if positive, else 0.
        DeltaTurn = recent_delta_turn - previous_delta_turn
        f_score.append(sign_check(DeltaTurn))
        return sum(f_score)


"""
exception_handling_text_element(str, selenium.webdriver.chrome.webdriver.WebDriver) -> str

checks to see if an exception was thrown when searching for a text formatted element. If no exception was found
then return text element, else return 0.

>>> find_element_by_xpath('//*[@id="tab-profitability"]/table[1]/tbody/tr[6]/td[10]', driver)
Most recent Gross Margin data
>>> find_element_by_xpath('//*[@id="financials"]/table/tbody/tr[10]/td[10]', driver)
Most recent Net Income data
"""
def exception_handling_text_element(text_element, driver):
    try:
        return driver.find_element_by_xpath(text_element).text
    except NoSuchElementException:
        return 0


"""
exception_handling_raw_element(str, selenium.webdriver.chrome.webdriver.WebDriver) -> str

checks to see if an exception was thrown when searching for a raw formatted element. If no exception was thrown
then return raw element, else return zero.

>>> find_element_by_xpath('//*[@id="data_i1"]/div[@id="Y_5"]', driver)
Most Recent Revenue
>>> find_element_by_xpath('//*[@id="data_ttg1"]/div[@id="Y_5"]', driver))
Most Recent Total Current Assets
"""
def exception_handling_raw_element(raw_element, driver):
    try:
        return driver.find_element_by_xpath(raw_element).get_attribute("rawvalue")
    except NoSuchElementException:
        return 0

"""
float_converter(str) -> float

converts xpath_to_data from a string to float. xpath_to_data equals a number represented as a string, dash, or zero 
depending on what data was pulled from a given webpage.

>>> float_converter(exception_handling_text_element('//*[@id="financials"]/table/tbody/tr[10]/td[10]', driver))
2.0
>>> float_converter(exception_handling_raw_element('//*[@id="data_ttg1"]/div[@id="Y_5"]', driver))
0.0
"""
def float_converter(xpath_to_data):
    if xpath_to_data == "—":
        return 0.0
    elif xpath_to_data == 0:
        return 0.0
    else:
        return float(xpath_to_data.replace(",", ""))


"""
division_by_zero_check(float, float) -> float

Checks to see if the denominator is 0. If true, 0 is returned else return the division of numerator and denominator.

>>> division_by_zero_check(1, 0)
0
>>> division_by_zero_check(2,1)
2
"""
def division_by_zero_check(numerator, denominator):
    if denominator == 0:
        return 0
    else:
        return numerator / denominator


"""
human_like_click(selenium.webdriver.chrome.webdriver.WebDriver, selenium.webdriver.support.wait.WebDriverWait, str) -> None

Waits for the location where the next click is going to take place to appear and then clicks that location.

>>> human_like_click(driver, wait, '//*[@id="keyStatWrap"]/div/ul/li[5]/a')
None
>>> human_like_click(driver, wait, '/html/body/div[1]/div[3]/div[1]/div/ul[2]/li[6]/a')
None
"""
def human_like_click(driver, wait, click_xpath):
    try:
        #wait.until's for the click location to load
        wait.until(EC.presence_of_element_located((By.XPATH, click_xpath)))
        wait.until(EC.visibility_of_element_located((By.XPATH, click_xpath)))
        wait.until(EC.element_to_be_clickable((By.XPATH, click_xpath)))
        #sends an enter (click) on a desired location on a given webpage.
        driver.find_element_by_xpath(click_xpath).send_keys("\n")
        #wait.until for the next page to load.
        wait.until(EC.title_contains("from Morningstar.com"))
    except Exception as e:
        logger.error("Something bad happened when hitting morningstar: {name} - {error} - %{num}d"
                     .format(error=e, name="Jamison",num=20))


"""
sign_check(float) -> int

Checks to see if pos_or_neg is great than 0. If yes, returns a 1 else returns 0.

>>> 2.0
1
>>> -1.0
0
"""
def sign_check(pos_or_neg):
    if pos_or_neg > 0:
        return 1
    else:
        return 0


"""
csv_creator(str, bool) -> None

converts a csv url into a csv file

>>> csv_creator("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=
                download",True)
None
>>> csv_creator("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=
                download",False)
None
"""
def csv_creator(url_link, header_setting):
    #creates a dataframe that contains the url_link provided to the function
    df = pd.read_csv(urlread_keep_trying(url_link))
    #creates stocklist.csv. If header_setting is true then a header will be created titled "Symbol" else, no header.
    df.to_csv('stocklist.csv', columns=['Symbol'], sep=',', index=False, mode='a',
              header=header_setting, index_label='Symbol')


"""
urlread_keep_trying(str) -> None

uses urlopen to access a given url and error handles any exception encountered.
Tries again 3 times if exceptions are met.

>>> urlread_keep_trying("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amax&render=download")
None
>>> urlread_keep_trying("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download")
None
"""
def urlread_keep_trying(url):
    for i in range(3):
        try:
            return urlopen(url)
        except urllib.error.HTTPError as error:
            if error.code in (403, 404):
                raise
            else:
                logging.info('error:', error.code, error.msg)
            pass
        logging.info(url, "failed")
        time.sleep(5)
        logging.info("trying again")


if __name__ == '__main__':
    main()
