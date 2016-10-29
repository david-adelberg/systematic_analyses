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
from systematic_investment.models import Info, MultiModel
from systematic_investment.models.multimodel import multi_model_create_info_interop
import numpy as np
from sklearn.linear_model import LassoLarsCV
from pandas import Series, DataFrame
        
def create_analyzer_filterer(to_keep_func):
    def filter_analyzer(analyzer):
        goods = []
        analyzer._to_analyze = analyzer._to_analyze.T
        for col in analyzer._to_analyze:
            goods.append(to_keep_func(col))#col.apply(to_keep_func))
        
        analyzer._to_analyze = analyzer._to_analyze.T
        analyzer._to_analyze = analyzer._to_analyze.loc[goods]
        return(analyzer)
    return(filter_analyzer)
    
industry_table = read_csv("data/SF0-tickers.csv")
    
def make_equity_filter(industry=None, sector=None):
    def equity_filter(col):
        row = industry_table.loc[industry_table['Name'] == col[1]]
        #ticker = col.name[1]
        #row = industry_table[ticker]
        if (industry is None or row['Industry'].iloc[0] == industry) and (sector is None or row['Sector'].iloc[0] == sector):
            return(True)
        else:
            return(False)
    return(equity_filter)
    
def lasso_constructor(y,x):
    return(SKLearnInterop(y,x, LassoLarsCV))
    
def equity_analyzer_creator(info, filter_func=identity):
    def func():
        res = reg_create_func(info, constructor=lasso_constructor)()
        res = filter_func(res)
        
        res.add_transformation(smart_divide, ('SF0', 'Earnings per Basic Share (USD)'), ('YAHOO', 'Adjusted Close'), name=('CALC', 'E/P'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Book Value per Share'), ('YAHOO', 'Adjusted Close'), name=('CALC', 'B/P'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Inventory'), ('SF0', 'Total Assets'), name=('CALC', 'Inventory/Assets'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Research and Development Expense'), ('SF0', 'Revenues (USD)'), name=('CALC', 'R&D Intensity Ratio'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Capital Expenditure'), ('SF0', 'Total Assets'), name=('CALC', 'Capital Intensity Ratio'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Issuance (Purchase) of Equity Shares'), ('SF0', 'Revenues (USD)'), name=('CALC', 'Share Issuance/Revenues'), drop_old=False)
        res.add_transformation(lambda x,y,z: smart_divide(x-y, z), ('SF0', 'Net Income'), ('SF0', 'Payment of Dividends & Other Cash Distributions'), ('SF0', 'Invested Capital'), name=('CALC', 'ROIC'), drop_old=False)
        #Doing this differently: res.add_transformation(identity, ('INDUSTRY', 'Sector'), name=('CALC', 'Sector'), drop_old=False)        
        
        #res.add_transformation(log, ('SF0', 'Revenues (USD)'), name=('CALC', 'size'), drop_old=False)
        res.add_transformation(identity, ('SF0', 'Current Ratio'), name=('CALC', 'Current Ratio'), drop_old=False)
        res.add_transformation(identity, ('SF0', 'Debt to Equity Ratio'), name=('CALC', 'Debt to Equity Ratio'), drop_old=False)        
        res.add_transformation(smart_divide, ('SF0', 'Gross Profit'), ('SF0', 'Revenues (USD)'), name=('CALC', 'Gross Margin'), drop_old=False)
        res.add_transformation(smart_divide, ('SF0', 'Payment of Dividends & Other Cash Distributions'), ('SF0', 'Net Income Common Stock'), name=('CALC', 'Dividend Payout Ratio'), drop_old=False)
        
        res.add_transformation(identity, ('YAHOO', 'Future Percent change in Adjusted Close'), name=('CALC', 'Future Percent Change in Adjusted Close'), drop_old=False)
        res._to_analyze = res._to_analyze[['CALC']]
        res.add_transformation(identity, ('CALC', 'Future Percent Change in Adjusted Close'), name=('YAHOO', 'Future Percent change in Adjusted Close'), drop_old=True)
        return(res)
    return(func)
    
def equity_combine_func(transformed_dfs):
    #indus = transformed_dfs["INDUSTRY"]
    #del transformed_dfs["INDUSTRY"]
    combined = default_combine_func(transformed_dfs)
    combined.drop_duplicates(inplace=True)
    #ncol = indus.loc[combined.index.map(lambda x: x[1])]['Sector']
    #ncol.index=combined.index
    #combined['INDUSTRY', 'Sector'] = ncol
    #combined.drop_duplicates(inplace=True)
    return(combined)
    
class SKLearnInterop:
    def __init__(self, lm_y, lm_x, constructor):
        self._lm_x = lm_x
        self._lm_y = lm_y
        self._obj = constructor()
        self._score = None
        
    def summary(self, xname, yname):
        coefs_to_print = DataFrame(self._obj.coef_)
        coefs_to_print.index = xname
        coefs_to_print.columns = (yname,)
        
        intercept_to_print = Series(self._obj.intercept_)
        intercept_to_print.index=(yname,)
        
        score_to_print = self._obj.score(self._lm_x, self._lm_y)
        self._score = score_to_print
        
        return("Coefficients:\n%s\nIntercepts:\n%s\nR^2:\n%s" % 
            (coefs_to_print, intercept_to_print, score_to_print))
        
    def fit(self):
        self._obj.fit(self._lm_x, self._lm_y)
        self._obj.__setattr__('summary', self.summary)
        return(self._obj)

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

    models = {}
    split_date='2013-01-01'
    sectors = np.array(list(set(industry_table['Sector'])))
    i = 0
    #crit = np.logical_or(sectors == 'Services', sectors == 'Financial')#for debugging purposes
    crit = np.logical_and.reduce([sectors != v for v in ['None', 'Oil & Gas Drilling & Exploration']])
    for sector in sectors[crit]:
        i += 1
        print("sector %s, %i out of %i" % (sector, i, len(sectors)))
        equity_filter = make_equity_filter(industry=None, sector=sector)
        filter_analyzer = create_analyzer_filterer(equity_filter)
        analyzer_creator = lambda info: equity_analyzer_creator(info, filter_analyzer)
        equity_info.create_analyzer(analyzer_creator).set(y_key=('YAHOO', 'Future Percent change in Adjusted Close'))
        model = LongShortTradingModel(equity_info, split_date=split_date, constructor = lambda y,x: SKLearnInterop(y,x, LassoLarsCV))
        models[sector] = model
    equity_info._models = models
        
    return(equity_info)
    
from systematic_investment.models import LongShortTradingModel
    
def equity_model_test_action(model):
    #model.print_tear_sheet() Would need to download daily data to do this
    model.print_analysis_results()
    #model.analyzer.plot_analysis_results()
    #model.analyzer.make_univariate_plots()
    #model.plot_historic_returns()
    model.plot_hypothetical_portfolio()

lengths = None
scores = None
sectors = None
d = None
if __name__ == '__main__': 
    info = get_equity_info()
    #test_data_processing(info)
    mm_c = lambda info: multi_model_create_info_interop(info, split_date='2013-01-01')
    sectors, lengths, scores = test_models(info, equity_model_test_action, mm_c)
    d = DataFrame([sectors, lengths, scores]).T
    print(d.sort_values([1]))
    print("done")