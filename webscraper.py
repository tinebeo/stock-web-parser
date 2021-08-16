import gzip
from urllib.request import Request, urlopen
import re
import csv
import time
import math

# opens ticker-list.txt file and returns list of tickers
def open_file():
    file = open("ticker-list.txt", "r")
    tickers = []

    for ticker in file:
        tickers.append(ticker)

    file.close()

    return tickers

# scrapes a website and returns stock data 
def scrape(ticker):
    
    url = "https://ca.finance.yahoo.com/quote/" + ticker
    req = Request(url)
    html = gzip.decompress(urlopen(req).read()).decode('utf-8')

    # name
    name = get_result(re.findall('<h1.*>(.*)<\/h1>', html))

    # price
    price = get_result(re.findall('<span class="Trsdu\(0.3s\) Fw\(b\) Fz\(36px\) Mb\(-4px\) D\(ib\)" data-reactid="\d+">(\d+.\d+)</span>', html))

    # dividend (note: this is in [$ dividend, % dividend] format)
    dividend = get_result(re.findall('data-test="DIVIDEND_AND_YIELD-value" data-reactid="\d+">(\d+.\d+ \(\d+.\d+%\))', html)).split(" ")

    # rating 
    rating = get_result(re.findall('rec-rating-txt.*aria-label="(\d\.?\d?) on a scale of 1 to 5, where 1 is Strong Buy and 5 is Sell', html))

    return StockData(name, ticker, price, dividend, rating)

def get_result(result):
    
    if result == []:
        return ""
    else:
        return result[0]


class StockData:
    def __init__(self, name, ticker, price, dividend, rating):
        self.name = name
        self.ticker = ticker
        self.price = price
        self.dividend_dollar = dividend[0]
        self.dividend_percent = re.sub(r"\((.*?)\)", r"\1", dividend[1]) # remove parenthesis
        self.rating = rating

    def get_shares_per_thousand(self):
        return math.floor(1000 / float(self.price))

    def get_returns_per_year(self):
        return math.floor(float(self.dividend_dollar) * self.get_shares_per_thousand() * 100)/100.0


# main
if __name__ == '__main__':
    # open file and get lits of tickers
    ticker_list = open_file()

    header = [
        'Name',
        'Price',
        'Annual Dividend ($)',
        'Annual Dividend (%)',
        'Rating (1=Strong Buy, 5=Sell)',
        'Est. Shares per $1k',
        'Est. Return per Year'
        ]

    with open('stock_data.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        # go through all the tickers and scrape
        for ticker in ticker_list:
            print(ticker.strip())
            stock_data = scrape(ticker.strip())
            writer.writerow([
                stock_data.name,
                stock_data.price,
                stock_data.dividend_dollar,
                stock_data.dividend_percent,
                stock_data.rating,
                stock_data.get_shares_per_thousand(),
                stock_data.get_returns_per_year()
            ])






