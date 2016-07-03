#!/usr/bin/env python

"""
In progress

Provides definitions for the equity trading model.
"""

__author__ = "David Adelberg"
__copyright__ = "Copyright 2016, David Adelberg"
__credits__ = ["David Adelberg"]

__license__ = """May be used by members of the Yale College Student Investment
                 Group for education, research, and management of the  
                 organization's portfolio. All other uses require the express
                 permission of the copyright holder. Other interested persons
                 should contact the copyright holder."""
__version__ = "0.1.0"
__maintainer__ = "David Adelberg"
__email__ = "david.adelberg@yale.edu"
__status__ = "Prototype"

from systematic_investment import *
from utils import *
from pandas import DataFrame

def load_SF0_qd_codes():
    return(fix_read_excel('SF0-datasets-codes.xls')[['Name', 'Code']])

def make_SF0_compute_names():
    codes = load_SF0_qd_codes()
    def res(col_name):
        qd_code = col_name.split(' - ')[0].replace('.', '/')
        name = codes.loc[codes['Code']==qd_code]['Name'].iloc[0]
        return('SF0 - %s' % name)
    return(res)
    
def equity_creator(info):
    def res():
        return(QuandlBulkDBLoader())
    return(res)
    
def make_SF0_col_handler():
    indicators = fix_read_excel('SF0-indicators.xls')[['Code', 'Name']]
    indicators.set_index('Code', inplace=True)
    indicators.sort_index(inplace=True)
    
    tickers = read_csv('data/SF0-tickers.csv')[['Ticker', 'Name']]
    tickers.set_index('Ticker', inplace=True)
    tickers.sort_index(inplace=True)
    
    def res(col_name):
        tick, fld = col_name.split('_')[0:2]
        sec = None
        ind = None
        try:
            sec = tickers.loc[tick]['Name']
            ind = indicators.loc[fld]['Name']
        except:
            sec = tick
            ind = fld
        
        return(sec + " - " + ind)
    
    return(res)
    
#def make_SF0_col_handler():
#    codes = load_SF0_qd_codes()
#    codes.set_index('Code', inplace=True)
#    codes.sort_index(inplace=True)
#    def res(col_name):
#        qd_code = 'SF0/%s' % col_name
#        try:
#            name = codes.loc[qd_code]['Name']
#        except:
#            name = "%s: %s" % (qd_code, "Missing")
#        return(name)
#    return(res)
    
def make_yahoo_col_handler():
    codes = read_csv('data/SF0-tickers.csv')[['Ticker', 'Name']]
    codes.set_index('Ticker', inplace=True)
    codes.sort_index(inplace=True)
    def res(col_name):
        code, ind = col_name.split('.')[1].split(' - ')
        name = None
        try:
            name = codes.loc[code]['Name']
        except:
            name = code + ": Missing"
        return('%s - %s' % (name, ind))
    return(res)
    
def equity_english_to_symbol_indicator(english):
    sp = None
    if ': Missing' in english:
        sp = english.split(': ')
    else:
        sp = english.split(' - ')
    symbol = sp[0]
    ind = sp[1]
    return symbol, ind
    
def load_yahoo_codes():
    all_yahoo_codes = read_csv('data/yahoo_codes.csv')['Code']
    all_sf0_codes = read_csv('data/SF0-tickers.csv')['Ticker']
    all_sf0_codes = 'YAHOO/'+all_sf0_codes
    res = list(set(all_yahoo_codes).intersection(set(all_sf0_codes)))
    res = DataFrame(res)
    res.columns=['Code']
    return(res)
    
def equity_transformer(df):
    res = df.dropna(how='all')
    is_good = [Timestamp(idx[0]) < Timestamp('2016-01-01') for idx in res.index.tolist()]
    res = res.loc[is_good]
    res = default_multi_index_resample_method(res)
    return(res)

def get_equity_info():
    equity_info = Info(data_dir=data_dir, authtoken=david_authtoken, main_db_name='YAHOO')
        
    equity_info.dbs.SF0. \
        set_path('downloaded_data', 'SF0-bulk-download.csv'). \
        set_path('download_and_save', 'SF0-bulk-download.csv'). \
        downloader(creator=equity_creator). \
        set(english_to_symbol_indicator=equity_english_to_symbol_indicator). \
        set(indicator_handler=make_default_indicator_handler([], [])). \
        set_path('process', 'SF0-processed_data.csv',
                compute_names=make_default_compute_names([], make_SF0_col_handler()),
                    load=True). \
        set(symbol_name='Security', date_name='Date'). \
        set(idx_to_datetime=multi_idx_to_datetime, resample_method=default_multi_index_resample_method)
        
#        #set_path('downloaded_data', 'SF0-data.csv')
        #        set(no_compute_codes=True). \
         #       set(code_builder=None, name_builder=None, symbols=None). \
    
    equity_info.dbs.YAHOO. \
        symbol('yahoo_codes.csv', 'Name', 'Code'). \
        set_path('download_and_save', 'YAHOO-data.csv'). \
        set_path('downloaded_data', 'YAHOO-data.csv'). \
        compute_wanted_codes.set(data=load_yahoo_codes()).up(). \
        downloader().set(code_builder=identity, name_builder=identity). \
        set(english_to_symbol_indicator=default_english_to_symbol_indicator, indicator_handler=make_default_indicator_handler([],['Adjusted Close'])). \
        set_path('process', 'YAHOO_processed_data.csv',
                 compute_names=make_default_compute_names([], make_yahoo_col_handler()),
                  load=True). \
        set(symbol_name='Security', date_name='Date')
    
    equity_info.set_path('combined_df', 'combined_equity_data.csv'). \
        combined_df.set(labels=['Date'], to_drop=[],names=['DB', 'Indicator'], transformer=equity_transformer).up(). \
        set_path('analyzer', 'equity_model.pickle', load=False). \
        create_analyzer().set(y_key=('YAHOO', "Future Percent change in Adjusted Close"))
        
    return(equity_info)
    
from systematic_investment import LongShortTradingModel, test_data_processing, test_models
    
def equity_model_test_action(model):
    #model.analyzer.print_analysis_results()
    model.analyzer.plot_analysis_results()
    #model.analyzer.make_univariate_plots()
    #model.plot_historic_returns()
    #model.plot_hypothetical_portfolio()
    
if __name__ == '__main__': 
    info = get_equity_info()
    test_data_processing(info)
    test_models(info, equity_model_test_action, LongShortTradingModel)
    print("done")