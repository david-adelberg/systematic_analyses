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

from equity_definitions_aux import *
from systematic_investment.models import Info, LongShortTradingModel, MultiModel
from systematic_investment.models.multimodel import multi_model_create_info_interop
import numpy as np
from sklearn.linear_model import LassoLarsCV
from pandas import Series, DataFrame
from scipy.stats import ttest_1samp
    
def equity_analyzer_creator(info, filter_func=identity):
    def func():
        res = reg_create_func(info, constructor=lasso_constructor)()
        res = filter_func(res)
        
        res.add_transformation(smart_divide, ('SF0', 'Earnings per Basic Share (USD)'), ('YAHOO', 'Adjusted Close'), name=('CALC', 'E/P'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Book Value per Share'), ('YAHOO', 'Adjusted Close'), name=('CALC', 'B/P'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Research and Development Expense'), ('SF0', 'Revenues (USD)'), name=('CALC', 'R&D Intensity Ratio'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Revenues (USD)'),('YAHOO', 'Adjusted Close') , name=('CALC', 'S/P'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Capital Expenditure'), ('SF0', 'Total Assets'), name=('CALC', 'Capital Intensity Ratio'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Issuance (Purchase) of Equity Shares'), ('SF0', 'Revenues (USD)'), name=('CALC', 'Share Issuance/Revenues'), drop_old=False)
        res.add_transformation(lambda x,y,z: smart_divide(x-y, z), ('SF0', 'Net Income'), ('SF0', 'Payment of Dividends & Other Cash Distributions'), ('SF0', 'Invested Capital'), name=('CALC', 'ROIC'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Payment of Dividends & Other Cash Distributions'), ('SF0', 'Net Income Common Stock'), name=('CALC', 'Dividend Payout Ratio'), drop_old=False)
        
        res.add_transformation(identity, ('YAHOO', 'Future Percent change in Adjusted Close'), name=('CALC', 'Future Percent Change in Adjusted Close'), drop_old=False)
        res._to_analyze = res._to_analyze[['CALC']]
        res.add_transformation(identity, ('CALC', 'Future Percent Change in Adjusted Close'), name=('YAHOO', 'Future Percent change in Adjusted Close'), drop_old=True)
        return(res)
    return(func)
    
def industry_models_create_func(equity_info):
    models = {}
    industries = np.array(list(set(industry_table['Industry'])))
    i = 0
    crit = np.array([np.sum(industry_table['Industry'] == ind) > 20 for ind in industries])
    #crit = np.array([False if i < 170 else v for i,v in enumerate(crit)]) # For debugging purposes
    for industry in industries[crit]:
        try:
            i += 1
            print("Industry %s, %i out of %i" % (industry, i, np.sum(crit)))
            equity_filter = make_equity_filter(industry=industry, sector=None)
            filter_analyzer = create_analyzer_filterer(equity_filter)
            analyzer_creator = lambda info: equity_analyzer_creator(info, filter_analyzer)
            equity_info.create_analyzer(analyzer_creator).set(y_key=('YAHOO', 'Future Percent change in Adjusted Close'))
            model = LongShortTradingModel(equity_info, split_date=equity_info._split_date, constructor = lambda y,x: SKLearnInterop(y,x, LassoLarsCV))
            models[industry] = model
        except:
            print("Not enough data for industry %s" % industry)
    return(models)
        
def sector_models_create_func(equity_info):
    models = {}
    sectors = np.array(list(set(industry_table['Sector'])))
    i = 0
    #debug
    #crit = np.logical_or.reduce([sectors == v for v in ['Utilities', 'Consumer Goods']]) # 1 top + 1 other   
    crit = np.logical_and.reduce([sectors != v for v in ['None', 'Oil & Gas Drilling & Exploration']])
    for sector in sectors[crit]:
        i += 1
        print("sector %s, %i out of %i" % (sector, i, np.sum(crit)))
        equity_filter = make_equity_filter(industry=None, sector=sector)
        filter_analyzer = create_analyzer_filterer(equity_filter)
        analyzer_creator = lambda info: equity_analyzer_creator(info, filter_analyzer)
        equity_info.create_analyzer(analyzer_creator).set(y_key=('YAHOO', 'Future Percent change in Adjusted Close'))
        model = LongShortTradingModel(equity_info, split_date=equity_info._split_date, constructor = lambda y,x: SKLearnInterop(y,x, LassoLarsCV))
        models[sector] = model
    return(models)

def get_equity_info():
    equity_info = Info(data_dir=data_dir, authtoken=david_authtoken, main_db_name='YAHOO')
    equity_info._split_date = ['2013-01-01']
        
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
        set(english_to_symbol_indicator=default_english_to_symbol_indicator, indicator_handler=make_default_indicator_handler(['Adjusted Close'],['Adjusted Close'])). \
        set_path('process', 'YAHOO_processed_data.csv',
                 compute_names=make_default_compute_names([], make_yahoo_col_handler()),
                  load=True). \
        set(symbol_name='Security', date_name='Date')
        
    lasso_constructor = lambda y,x: SKLearnInterop(y,x, LassoLarsCV)
    
    equity_info.set_path('combined_df', 'combined_equity_data.csv'). \
        combined_df.set(labels=['Date'], to_drop=[],names=['DB', 'Indicator'], min_date=to_datetime('2010-01-01'), transformer=equity_transformer, combine_func=equity_combine_func).up(). \
        set_path('analyzer', 'equity_model.pickle', load=False). \
        create_analyzer(equity_analyzer_creator).set(y_key=('YAHOO', "Future Percent change in Adjusted Close"))

    equity_info._models = industry_models_create_func(equity_info)
        
    return(equity_info)

def drop_model_crit(m, score_thresh=0.3**2, len_thresh=30):
    return(m.analyzer._obj._score > score_thresh and m.analyzer._data_len > len_thresh)
    
def equity_model_test_action(model, crit = drop_model_crit):
    #model.print_tear_sheet() Would need to download daily data to do this
    res = Info()
    res.initial_results = model.summarize()
    model.print_models()
    print("Dropping bad models.")
    model.drop_bad_models(drop_model_crit)
    model.print_models()
    res.drop_1 = model.summarize()
    
    print("Dropping models that underperformed in period 2")

    def g_crit(m):
        return(m.compute_returns_by_period()[1]>0.0)
    
    rets = np.array([m.compute_returns_by_period()[1] for m in model._models.values()])
    t, two_pval = ttest_1samp(rets, 0.0)
    print("Analyzing out-of-sample returns:")
    one_pval = two_pval / 2.0 if t > 0 else (1.0 - (two_pval / 2.0))
    print("T-statistic: %f, one-sided p-value: %f" % (t, one_pval))
    res.t_val = t
    res.p_val = one_pval
    
    model.drop_bad_models(g_crit)
    res.drop_2 = model.summarize()
    model.print_models()
    model.print_analysis_results()
    #model.analyzer.plot_analysis_results()
    #model.analyzer.make_univariate_plots()
    #model.plot_historic_returns()
    model.plot_hypothetical_portfolio()
    model.print_models()
    return(res)

d = None
if __name__ == '__main__': 
    info = get_equity_info()
    #test_data_processing(info)
    mm_c = lambda info: multi_model_create_info_interop(info, info._split_date)
    d = test_models(info, equity_model_test_action, mm_c)[0]
    print("done")