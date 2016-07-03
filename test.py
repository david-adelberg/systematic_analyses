#!/usr/bin/env python

"""
Deprecated

Used this to test ideas as data was downloading
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

def load_SF0_qd_codes():
    return(fix_read_excel('SF0-datasets-codes.xls')[['Name', 'Code']])

def make_SF0_col_handler():
    codes = load_SF0_qd_codes()
    codes.set_index('Code', inplace=True)
    codes.sort_index(inplace=True)
    def res(col_name):
        qd_code = 'SF0/%s' % col_name
        try:
            name = codes.loc[qd_code]['Name']
        except:
            name = "%s - %s" % (qd_code, "Missing")
        return(name)
    return(res)

def equity_test_data_processing():
    dd = 'data/SF0-test-downloaded_data.csv'
    loader = QuandlBulkDBLoader('data/SF0-bulk-download.csv')
    #loader.download_and_save('data/SF0-test-downloaded_data.csv', 
    #                         compute_names=make_default_compute_names([], make_SF0_col_handler()))
     
    loader.load_downloaded_data(dd, load=lambda p: read_csv(p, index_col=[0,1]))
    loader.process('data/SF0-test-processed_data.csv',
                   compute_names=make_default_compute_names([], identity),
                   english_to_symbol_indicator=default_english_to_symbol_indicator,
                   indicator_handler=make_default_indicator_handler([], []),
                   symbol_name='Security',
                   date_name='Date',
                   idx_to_datetime=multi_idx_to_datetime,
                   resample_method=default_multi_index_resample_method)

    to_drop = []
    combined_names = ["DB", "Indicator"]
    path= "data/SF0-test-combined_data.csv"
    combiner = DBCombiner({'SF0': loader._processed_data})
    return(combiner.combine(to_drop=to_drop, combined_names=combined_names, path=path, transformer=identity))
               
def equity_creator(info):
    def res():
        return(QuandlBulkDBLoader('data/SF0-bulk-download.csv'))
    return(res)

#def get_equity_info():
#    equity_info = Info(data_dir=data_dir, main_db_name='YAHOO')
#    equity_info.dbs.SF0. \
#        set_path('download_and_save', 'SF0-test-downloaded_data.csv', english_to_symbol_indicator=make_SF0_col_handler()). \
#        set(no_compute_codes=True). \
#        downloader(creator=equity_creator). \
#        set(code_builder=None, name_builder=None, symbols=None). \
#        set(english_to_symbol_indicator=make_SF0_col_handler()). \
#        set(indicator_handler=make_default_indicator_handler([], [])). \
#        set_path('process', 'SF0-test-processed_data.csv',
#                 compute_names=make_default_compute_names([], identity),
#                    load=False). \
#        set(symbol_name='Security', date_name='Date'). \
#        set(idx_to_datetime=multi_idx_to_datetime, resample_method=default_multi_index_resample_method)
#        #set_path('downloaded_data', 'SF0-data.csv')
#    
#    equity_info.set_path('combined_df', 'combined_equity_data.csv'). \
#        combined_df.set(labels=['Date'], to_drop=[],names=['DB', 'Indicator'], transformer=identity). \
#        set_path('analyzer', 'equity_model.pickle', load=False). \
#        create_analyzer().set(y_key="To Be Determined")
#        
#    return(equity_info)
    
from systematic_investment import LongShortTradingModel, test_data_processing, test_models
    
def equity_model_test_action(model):
    model.analyzer.print_analysis_results()
    model.analyzer.plot_analysis_results()
    #model.analyzer.make_univariate_plots()
    #model.plot_historic_returns()
    #model.plot_hypothetical_portfolio()
    
if __name__ == '__main__': 
    #info = get_equity_info()
    #test_data_processing(info)
    #equity_test_data_processing()
    info = Info(y_key="YKEY", data_dir=data_dir).set_path('combined_df', 'SF0-test-combined_data.csv')
    info.set_path("analyzer", 'equity_model.pickle', load=False).create_analyzer().set(y_key="Y_KEY")
    test_models(info, equity_model_test_action, LongShortTradingModel)
    print("done")