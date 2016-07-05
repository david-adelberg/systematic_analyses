#!/usr/bin/env python

"""
Provides definitions for the S&P 500 Trading Model.
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
__status__ = "Development"

from systematic_investment import *
from utils import *

def make_sp_col_handler():
    yale = default_indicator_loader('YALE-datasets-codes.xls')
    def res(col):
        ind_val = col.replace('.', '/').split(' - ')
        indicator = yale.loc[yale['Code']==ind_val[0]]['Name'].iloc[0]
        
        return('%s - %s' % (indicator, ind_val[1]))
    
    return(res)
    
def sp_analyzer_creator(info):
    def func():
        res = reg_create_func(info)() # make sure not normals
        res.add_transformation(lambda x, y: x/y, ('YALE', 'Earnings'), ('YALE', 'S&P Composite'), name=('CALC', 'E/P Ratio'), drop_old=False)
        res.add_transformation(lambda x: 1/x, ('YALE', 'Cyclically Adjusted PE Ratio'), name=('CALC', 'Cyc. Adj. E/P Ratio'), drop_old=False)
        res._to_analyze.drop([('YALE', 'Real Price'), ('YALE', 'Real Earnings'),
                              ('YALE', 'Real Dividend'), ('YALE', 'CPI'),
                              ('YALE', 'Dividend'), ('YALE', 'Earnings'),
                              ('YALE', 'S&P Composite')], axis=1, inplace=True)
        res._to_analyze.drop([('YALE', 'Cyclically Adjusted PE Ratio'),
                              ('YALE', 'Percent change in CPI'),
                              ('YALE', 'Percent change in Earnings'),
                              #('YALE', 'Percent change in Long Interest Rate'),
                              ('YALE', 'Percent change in S&P Composite'),
                              ('YALE', 'Long Interest Rate'),
                              #('YALE', 'S&P Composite'),
                              #('CALC', 'Cyc. Adj. E/P Ratio')
                              ('CALC', 'E/P Ratio')
                              ], axis=1, inplace=True)
        return(res)
        
    return(func)

def get_sp500_info():
    sp_info = Info(data_dir=data_dir, authtoken=david_authtoken, main_db_name='YALE')
    sp_info.dbs.YALE. \
        symbol('yale_sp500.xls', 'Name', 'Code', read_excel). \
        downloader().set(code_builder=identity, name_builder=identity). \
        set(english_to_symbol_indicator=default_english_to_symbol_indicator). \
        set(indicator_handler=make_default_indicator_handler(['CPI', 'Earnings', 'Long Interest Rate', 'S&P Composite'], ['S&P Composite'])). \
        set_path('download_and_save', 'yale_data.csv'). \
        set_path('process', 'yale_processed_data.csv', compute_names=make_default_compute_names([], make_sp_col_handler()), load=False). \
        set(symbol_name='S&P500', date_name='Date'). \
        set_path('downloaded_data', 'yale_data.csv')
    
    sp_info.set_path('combined_df', "combined_sp500_data.csv"). \
        combined_df.set(labels= ['Date'], to_drop=['Dividend', 'Real Dividend', 'Real Earnings', 'Real Price'], names=["DB", "Indicator"], transformer=identity).up(). \
        set_path('analyzer', 'sp500_model.pickle', load=False). \
        create_analyzer(creator=sp_analyzer_creator).set(y_key=('YALE', "Future Percent change in S&P Composite"))
    
    return(sp_info)
    
from systematic_investment import test_data_processing, test_models
from systematic_investment import LongShortTradingModel
import statsmodels.api as sm              
 
def sp_model_test_action(model):
    model.analyzer.print_analysis_results()
    model.analyzer.plot_analysis_results()
    #model.analyzer.make_univariate_plots()
    #model.plot_historic_returns()
    #model.plot_hypothetical_portfolio()

if __name__ == '__main__':
    info = get_sp500_info()
    test_data_processing(info)
    test_models(info, sp_model_test_action, lambda info: LongShortTradingModel(info, normals=False, constructor=sm.RLM))
    print("done")