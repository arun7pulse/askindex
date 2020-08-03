#Author ArunSK.
import os
import datetime
import logging
import requests
import pandas as pd  # Higher-level numerical Python library.
import numpy as np  # Low-level numerical Python library.

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
           'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'}

np.warnings.filterwarnings('ignore')
pd.set_option('expand_frame_repr', False)
pd.set_option('display.precision', 4)
pd.set_option('display.max_columns', 18)
pd.set_option('display.max_rows', 40)
pd.set_option('display.width', 15)
pd.options.display.float_format = '{:.2f}'.format

# CRITICAL	50 ERROR	40 WARNING	30 INFO	20 DEBUG	10
try:
    LOGFILE = "{}.log".format(os.path.basename(__file__))
    logging.basicConfig(level=logging.INFO, filename=LOGFILE, filemode='a')
    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter("%(asctime)s %(name)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s")
    fileHandler = logging.FileHandler(LOGFILE)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
except NameError:
    pass

def last_thursday():
    today = datetime.datetime.today().date()
    offset = (today.weekday() - 3) % 7
    return today - datetime.timedelta(days=offset)
    
def split_date_range(start, end, pdays=92):
    firstDate = datetime.datetime.strptime(start, "%d-%m-%Y")
    lastDate = datetime.datetime.strptime(end, "%d-%m-%Y")
    startdate = firstDate
    startdatelist = []
    enddatelist = []
    while startdate <= lastDate:
        enddate = startdate + datetime.timedelta(days=pdays - 1)
        startdatelist.append(startdate.strftime("%d-%m-%Y"))
        if enddate > lastDate:
            enddatelist.append(lastDate.strftime("%d-%m-%Y"))
        enddatelist.append(enddate.strftime("%d-%m-%Y"))
        startdate = enddate + datetime.timedelta(days=1)
    for sdate, edate in zip(startdatelist, enddatelist):
        yield sdate, edate


def get_hist_index_data(symbol="NIFTY 50"):
    if symbol.upper() == "NIFTY 50":
        # file = "https://raw.githubusercontent.com/arun7pulse/askindex/master/NIFTY%2050_01-01-2000_31-12-2019.csv"
        file = "https://raw.githubusercontent.com/arun7pulse/askindex/master/NIFTY%2050.csv"
    if symbol.upper() == "NIFTY BANK":
        # file = "https://raw.githubusercontent.com/arun7pulse/askindex/master/NIFTY%20BANK_01-01-2000_31-12-2019.csv"
        file = "https://raw.githubusercontent.com/arun7pulse/askindex/master/NIFTY%20BANK.csv"
    df = pd.read_csv(file, parse_dates=True, index_col='date',
                     dayfirst=True, error_bad_lines=False).replace("-", method='bfill')
    df = df.astype({"symbol": "category", "open": "float64", "high": "float64",
                    "low": "float64", "close": "float64", "volume": "float64", "value": "float64"})
    return df

def get_daily_index_data(symbol="NIFTY 50", start=None, end=None):
    end = (datetime.datetime.today().date()).strftime('%d-%m-%Y') if end == None else end
    start = (datetime.datetime.today().date()-datetime.timedelta(days=99)).strftime('%d-%m-%Y') if start ==  None else start
    if start != end:
        url1 = "https://www1.nseindia.com/products/dynaContent/equities/indices/historicalindices.jsp?indexType="
        url2 = symbol.replace(" ", "%20").replace("&", "%26").upper()
        url3 = "&fromDate=" + start + "&toDate=" + end
        url = url1+url2+url3
        print(url)
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                dat = pd.read_html(response.text, header=2)
                df = pd.DataFrame.from_records(dat[0], index='Date')
                df.index.names = ['date']
                df = df[:-1]
                df = df.dropna(axis='rows')
                df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Shares Traded': 'volume', 'Turnover ( Cr)': 'value'}, inplace=True)
                df['symbol'] = symbol
                df.index = pd.to_datetime(df.index)
                df.sort_index(inplace=True)
                return df
        except:
            return None
    print("start date and end date is same")
    return None

def get_all_index_data(symbol='NIFTY 50', start='01-01-2010', end=(datetime.datetime.today().date()).strftime('%d-%m-%Y')):
    idx = pd.DataFrame()
    idx = idx.append(get_hist_index_data(symbol=symbol))
    # if idx.index[-1].values 
    start = (idx.index.max()+datetime.timedelta(days=1)).strftime('%d-%m-%Y')
    for sdate, edate in split_date_range(start, end):
        print("Loading Index Data :", symbol, sdate, edate)
        df = get_daily_index_data(symbol=symbol, start=sdate, end=edate)
        idx = idx.append(df, verify_integrity=True)
    try:
        idx = idx.replace("-", method='bfill')
        idx = idx.astype({"symbol": "category", "open": "float64", "high": "float64", "low": "float64", "close": "float64", "volume": "float64", "value": "float64"})
    except:
        pass
    idx.to_csv("{}.csv".format(symbol))
    return idx

def dataframe_target(df, top_percent=5):
    df['ltgt'] = ((1 + round((df[df['high_pct'] < 0].quantile(0.05)['high_pct'])/100, 4)) * df['close'].shift()).fillna(method='bfill')
    df['utgt'] = ((1 + round((df[df['low_pct'] > 0].quantile(0.95)['low_pct'])/100, 4)) * df['close'].shift()).fillna(method='bfill')
    df['stat'] = df['close'].between(df['ltgt'], df['utgt'], inclusive=False)
    df['miss'] = np.where(df['stat'] == False, np.where(df['utgt'] < df['close'], round(df['close'] - df['utgt'], 2), round(df['close'] - df['ltgt'], 2)), "PROFIT")
    return df 

class Indices(object):
    def __init__(self, symbol="NIFTY 50"): # OR "NIFTY BANK"
        self.symbol = symbol
        self.load_histdata()

    def load_histdata(self):
        self.dff = get_hist_index_data(symbol=self.symbol)
        self.df = self.dff.drop('symbol', axis=1)
        self.calc_frequency()
        
    def load_livedata(self):
        self.dff = get_all_index_data(symbol=self.symbol)
        self.df = self.dff.drop('symbol', axis=1)
        self.calc_frequency()

    def calc_frequency(self, sample='W-THU'):
        self.df = self.df.join((self.df.pct_change()*100), rsuffix='_pct').fillna(method='bfill')
        ohlcvv = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'value': 'sum'}
        #Weekly Data Based on Thursday 
        self.dfw = self.df.resample(sample, label='right').agg(ohlcvv)
        self.dfwm = self.dfw.resample("BM", label='right').agg(ohlcvv)
        self.dfw = self.dfw.join((self.dfw.pct_change()*100), rsuffix='_pct').fillna(method='bfill')
        self.dfwm = self.dfwm.join((self.dfwm.pct_change()*100), rsuffix='_pct').fillna(method='bfill')
        #Weekly Data Based on Friday
        nesample = "W-FRI"
        self.dfwf = self.df.resample(nesample, label='right').agg(ohlcvv)
        self.dfwfm = self.dfwf.resample("BM", label='right').agg(ohlcvv)
        self.dfwf = self.dfwf.join((self.dfwf.pct_change()*100), rsuffix='_pct').fillna(method='bfill')
        self.dfwfm = self.dfwfm.join((self.dfwfm.pct_change()*100), rsuffix='_pct').fillna(method='bfill')
        self.calc_targets()
        
    def calc_targets(self):
        self.df = dataframe_target(self.df)
        self.dfw = dataframe_target(self.dfw)
        self.dfwm = dataframe_target(self.dfwm)
        self.dfwf = dataframe_target(self.dfwf)
        self.dfwfm = dataframe_target(self.dfwfm)

if __name__ == '__main__':
    nf = Indices(symbol="NIFTY 50")
    bf = Indices(symbol="NIFTY BANK")