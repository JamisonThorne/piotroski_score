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
                        level=logging.DEBUG if args.verbose else logging.DEBUG)
    global logger
    logger = logging.getLogger("webscraper")
    if os.path.exists("stocklist.csv"):
        os.remove("stocklist.csv")
    if os.path.exists("fscore.csv"):
        os.remove("fscore.csv")
        logging.info("Delete Success")
    #csv_creator("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amax&render=download",True)
    csv_creator("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download",True)
    #csv_creator("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download",True)
    df = pd.read_csv('stocklist.csv')
    df_new = df[~df['Symbol'].str.contains('\w+\W')]
    df_new.to_csv('fscore.csv', columns=['Symbol','F_Score'], index=True, mode='a', header=None)
    df_fscore = pd.read_csv('fscore.csv', names=['Symbol', 'F_Score'])
    temp = []
    driver = init_driver('/home/jonsnow/my_stockproject/chromedriver-Linux64')
    for index, row in df_fscore.iterrows():
        # Change Chrome Driver Path as Needed
        # Ubunto Users (see tytus's comments):
        # https://stackoverflow.com/questions/22476112/using-chromedriver-with-selenium-python-ubuntu
        logging.info(index)
        logging.info(row)
        temp.append([df.iloc[index,0], Parse(driver, df.iloc[index,0])])
    driver.close()
    df = pd.DataFrame(temp, columns=['Symbol', 'fscore'])
    df.to_csv('fscore.csv', index=False, sep='\t')
    logging.info("fin")


def init_driver(web_driver_location):
    options = Options()
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

'''
Parse driver content for stock data
>>>Parse(driver, empty)

'''
def Parse(driver, stock):
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
        #Net Income
        recent_net_income = float_converter(exception_handling_text_element('//*[@id="financials"]'
                                                                    '/table/tbody/tr[10]/td[10]', driver))
        previous_net_income = float_converter(exception_handling_text_element('//*[@id="financials"]'
                                                                      '/table/tbody/tr[10]/td[9]', driver))
        #Shares
        recent_shares = float_converter(exception_handling_text_element('//*[@id="financials"]'
                                                                '/table/tbody/tr[18]/td[10]', driver))
        previous_shares = float_converter(exception_handling_text_element('//*[@id="financials"]'
                                                                  '/table/tbody/tr[18]/td[9]', driver))
        #Gross Margon
        recent_gross_margin = float_converter(exception_handling_text_element('//*[@id="tab-profitability"]'
                                                                      '/table[1]/tbody/tr[6]/td[10]', driver))
        previous_gross_margin = float_converter(exception_handling_text_element('//*[@id="tab-profitability"]'
                                                                        '/table[1]/tbody/tr[6]/td[9]', driver))
        #Efficiency turnover tab
        human_like_click(driver, wait, '//*[@id="keyStatWrap"]/div/ul/li[5]/a')
        #Asset Turnover
        recent_asset_turnover = float_converter(exception_handling_text_element('//*[@id="tab-efficiency"]'
                                                                        '/table/tbody/tr[16]/td[10]', driver))
        previous_asset_turnover = float_converter(exception_handling_text_element('//*[@id="tab-efficiency"]'
                                                                          '/table/tbody/tr[16]/td[9]', driver))
        #Financials Page > Income Statement
        human_like_click(driver, wait, '/html/body/div[1]/div[3]/div[1]/div/ul[2]/li[6]/a')

        #Revenue
        recent_revenue = float_converter(exception_handling_raw_element('//*[@id="data_i1"]'
                                                                '/div[@id="Y_5"]', driver))
        previous_revenue = float_converter(exception_handling_raw_element('//*[@id="data_i1"]'
                                                                  '/div[@id="Y_4"]', driver))
        #Financials Page > Balance Sheet
        human_like_click(driver, wait, '/html/body/div[1]/div[3]/div[1]/div[1]/div/ul[3]/li[2]/a')
        #Total Current Assets
        recent_tot_current_assets = float_converter(exception_handling_raw_element('//*[@id="data_ttg1"]'
                                                                           '/div[@id="Y_5"]', driver))
        previous_tot_current_assets = float_converter(exception_handling_raw_element('//*[@id="data_ttg1"]'
                                                                             '/div[@id="Y_4"]', driver))
        #Total Assets
        recent_total_assets = float_converter(exception_handling_raw_element('//*[@id="data_tts1"]'
                                                                             '/div[@id="Y_5"]', driver))
        previous_total_assets = float_converter(exception_handling_raw_element('//*[@id="data_tts1"]'
                                                                               '/div[@id="Y_4"]', driver))
        previous_previous_total_assets = float_converter(exception_handling_raw_element('//*[@id="data_tts1"]'
                                                                                '/div[@id="Y_3"]', driver))

        #Total Current Liabilities
        recent_total_current_liabilities = float_converter(exception_handling_raw_element('//*[@id="data_ttgg5"]'
                                                                                  '/div[@id="Y_5"]', driver))
        previous_total_current_liabilities = float_converter(exception_handling_raw_element('//*[@id="data_ttgg5"]'
                                                                                    '/div[@id="Y_4"]', driver))
        #Total Liabilities
        recent_long_term_debt = float_converter(exception_handling_raw_element('//*[@id="data_i50"]'
                                                                               '/div[@id="Y_5"]', driver))
        previous_long_term_debt = float_converter(exception_handling_raw_element('//*[@id="data_i50"]'
                                                                                 '/div[@id="Y_4"]', driver))
        # Financials Page > Cash Flow
        human_like_click(driver, wait, '/html/body/div[1]/div[3]/div[1]/div[1]/div/ul[3]/li[3]/a')
        #Cash Provided by Operations
        recent_operating_cash_flow = float_converter(exception_handling_raw_element('//*[@id="data_tts1"]'
                                                                            '/div[@id="Y_6"]', driver))
        #The following code goes through the math to calculate Piotroski's F Score
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


def division_by_zero_check(numerator, denominator):
    """
    (int, int) -> int
    
    Checks to see if the denominator is 0. 
    If true, 0 is returned else return the division of the two integers.
    
    Precondition: len(s1) == len(s2)

    >>> division_by_zero_check(1, 0)
    0
    >>> division_by_zero_check(2,1)
    2
    """
    if denominator == 0:
        return 0
    else:
        return numerator/denominator


def exception_handling_text_element(text_element, driver):
    """
    (string, virtual driver) -> string or integer
    :param text_element:
    :param driver:
    :return:
    """
    try:
        return driver.find_element_by_xpath(text_element).text
    except NoSuchElementException:
        return 0


def exception_handling_raw_element(raw_element, driver):
    try:
        return driver.find_element_by_xpath(raw_element).get_attribute("rawvalue")
    except NoSuchElementException:
        return 0


def float_converter(xpath_to_data):

    if xpath_to_data == "—":
        return 0
    elif xpath_to_data == 0:
        return 0
    else:
        return float(xpath_to_data.replace(",", ""))


def human_like_click(driver, wait, click_xpath):
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, click_xpath)))
        wait.until(EC.visibility_of_element_located((By.XPATH, click_xpath)))
        wait.until(EC.element_to_be_clickable((By.XPATH, click_xpath)))
        driver.find_element_by_xpath(click_xpath).send_keys("\n")
        wait.until(EC.title_contains("from Morningstar.com"))
    except Exception as e:
        logger.error("Something bad happened when hitting morningstar: {name} - {error} - %{num}d"
                     .format(error=e, name="Jamison",num=20))


def sign_check(pos_neg):
    if pos_neg > 0:
        return 1
    else:
        return 0


def csv_creator(url_link, header_setting):
    df = pd.read_csv(urlread_keep_trying(url_link))
    df.to_csv('stocklist.csv', columns=['Symbol'], sep=',', index=False, mode='a',
              header=header_setting, index_label='Symbol')


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