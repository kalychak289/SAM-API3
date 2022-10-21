import bisect
from datetime import datetime, timedelta
from flask import (Flask, jsonify,  request)
import numpy as np
import pandas as pd
import datetime
from pandas.io.formats import style



app = Flask(__name__)

def calc_returns(diffs, prices):
    r= []
    for d, p in zip(diffs, prices[:-1]):
        r.append(1+d/p)
    logs = np.log(r)
    return np.log(r) 

@app.route('/', methods=['GET', 'POST'])
def keepalive():
    return jsonify(status=200, message='Tested Ok')

@app.route('/calcbeta', methods=['GET'])
def calcbeta():
    try:
        stock = request.args.get('ticker')
        benchmark = request.args.get('benchmark')
        sd = pd.to_datetime(request.args.get('startdate'), format = '%m/%d/%Y')
        ed = pd.to_datetime(request.args.get('enddate'), format = '%m/%d/%Y')
        betadurationdays = request.args.get('lookback', type=int)
        S3_BUCKET = "<path to csv file>/TestMarketData.csv"
        aws_credentials = { "key": "<AWS KEY>", "secret": "<Secret Key>" }
        df = pd.read_csv(S3_BUCKET, storage_options=aws_credentials)
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime('%Y%m%d')
        df["Date"] = pd.to_numeric(df["Date"])
        df["Ticker"] = df["Ticker"].astype("str")
        df.reset_index(inplace=True)
        df.set_index("Date", inplace=True)       
        startdate = int(sd.strftime('%Y%m%d'))        
        enddate = int(ed.strftime('%Y%m%d'))
        alldates = sorted(np.unique(np.array(df.index)))
        start_idx = bisect.bisect_left(alldates, startdate)
        startdate =  alldates[start_idx]
        end_idx = bisect.bisect_left(alldates, enddate )
        enddate = alldates[end_idx]
        daterange = [alldates[x] for x in range(start_idx, end_idx+1)]
        df = df.sort_values(by=['Ticker','Date'])
        df_stock = df.query("Ticker==@stock")
        df_benchmark = df.query("Ticker==@benchmark")
        first_day_stock_priced = df_stock.index.values[0]
        first_day_benchmark_priced = df_benchmark.index.values[0]
        print(first_day_stock_priced, first_day_benchmark_priced)
        beta=[]
        for single_date in daterange:
            look_back_todate = (datetime.datetime.strptime(str(single_date),  "%Y%m%d") - timedelta(days= betadurationdays)).strftime('%Y%m%d')
            look_back_date = int(look_back_todate)
            lookback_idx = bisect.bisect_left(alldates, look_back_date)
            if lookback_idx >= 0 and alldates[lookback_idx] > first_day_stock_priced and alldates[lookback_idx] > first_day_benchmark_priced:       
                look_back_date =alldates[lookback_idx]
                stock_close_prices_over_lookbackrange = df_stock.loc[look_back_date:single_date]['ClosePrice'].tolist()              
                benchmark_close_prices_over_lookbackrange = df_benchmark.loc[look_back_date:single_date]['ClosePrice'].tolist() 
                stock_returns_over_beta_duration_days = calc_returns(np.diff(stock_close_prices_over_lookbackrange), stock_close_prices_over_lookbackrange)       
                benchmark_returns_over_beta_duration_days = calc_returns(np.diff(benchmark_close_prices_over_lookbackrange), benchmark_close_prices_over_lookbackrange)    
                var = np.var(stock_returns_over_beta_duration_days, ddof=1)
                covar = np.cov(stock_returns_over_beta_duration_days, benchmark_returns_over_beta_duration_days)[0][1]
                beta.append( (pd.to_datetime(single_date, format = "%Y%m%d"), np.round(covar/var, 4)))
        df_1 = pd.DataFrame(beta, columns=['Date', 'Ticker'])
        my_css = {
        "row_heading": "",
        "col_heading": "",
        "index_name": "",
        "col": "c",
        "row": "r",
        "col_trim": "",
        "row_trim": "",
        "level": "l",
        "data": "",
        "blank": "",
        }
        props = 'font-family: "Times New Roman", Times, serif; color: #e83e8c; font-size:10pt;'
        html = style.Styler(df_1, uuid_len=0, cell_ids=False)
        html.set_table_styles([{'selector': 'td', 'props': props},
                            {'selector': '.c1', 'props': 'color:green;'},
                            {'selector': '.l0', 'props': 'color:blue;'},
                            {"selector": "", "props": [("border", "1px black solid !important;")]},
                            {"selector": "tbody td", "props": [("border", "1px black solid !important;")]},
                            {"selector": "th", "props": [("border", "1px black solid !important;")]}
                            ],
                            css_class_names=my_css)

        return(html.to_html())
    except BaseException as e:
        return jsonify({'error':e})
