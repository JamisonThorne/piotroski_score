import re
import os.path
from urllib.request import urlopen
import urllib.error
import time
import csv


def main():
    if os.path.exists("temptest.csv"):
        os.remove("temptest.csv")
    if os.path.exists("temptest2.csv"):
        os.remove("temptest2.csv")
    ticker_extractor("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amax&render=download")
    ticker_extractor("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download")
    ticker_extractor("http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download")
    column_keeper("temptest.csv", ("Symbol", "MarketCap"), "temptest2.csv")
    print("finished")


def ticker_extractor(url):
    data = urlread_keep_trying(url)
    output = data.read().decode('utf-8').split("\n")
    with open("temptest.csv", 'a', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        for i in output:
            wr.writerow(re.findall(r'"([^"]*)"', i))


def urlread_keep_trying(url):
    for i in range(3):
        try:
            return urlopen(url)
        except urllib.error.HTTPError as error:
            if error.code in (403, 404):
                raise
            else:
                print('error:', error.code, error.msg)
            pass
        print(url, "failed")
        time.sleep(5)
        print("trying again")


def column_keeper(old_file, keep_these, new_file):
    columns = [keep_these]
    with open(old_file) as infile, open(new_file, "w", newline="") as outfile:
        r = csv.DictReader(infile)
        w = csv.DictWriter(outfile, columns, extrasaction="ignore")
        w.writeheader()
        for row in r:
            w.writerow(row)

'''
def csv_writer(list):
    with open('filename', 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(mylist)
'''

if __name__ == '__main__':
    main()