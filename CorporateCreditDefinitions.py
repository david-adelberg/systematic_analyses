#!/usr/bin/env python

"""
In progress

Provides definitions for the corporate credit model.
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

from systematic_investment import Info, identity, reg_create_func
from utils import *
import statsmodels.api as sm

def load_ML_qd_codes():
    return(fix_read_excel('ML-datasets-codes.xls')[['Name', 'Code']])
    
cc_indicator_to_percentages = ['Emerging Markets Corporate Bond Total Return Index',
             'Europe/Middle East/Africa (EMEA) Corporate Bond Total Return Index',
             'IG Emerging Markets Corporate Bond Total Return Index',
             'US AA Rated Total Return Index',
             'US AAA Corporate Bond Total Return Index',
             'US B Corporate Bond Total Return Index',
             'US BB Bond Total Return Index',
             'US CCC Bond Total Return Index',
             'US Corporate BBB Total Return Index',
             'US Corporate Bond A Total Return Index',
             'US Corporate Bonds Total Return Index']

def make_ML_col_handler():
    codes = load_ML_qd_codes()
    def res(col_name):
        qd_code = col_name.split(' - ')[0].replace('.', '/')
        name = codes.loc[codes['Code']==qd_code]['Name'].iloc[0]
        return('ML - %s' % name)
    return(res)
    
def ml_analyzer_creator(info):
    def func():
        res = reg_create_func(info, drop_observations=False)()
        
        res._to_analyze.drop([('ML', val) for val in cc_indicator_to_percentages], axis=1)
        return(res)
    return(func)

def get_cc_info():
    cc_info = Info(data_dir=data_dir, authtoken=david_authtoken, main_db_name='ML')
    cc_info.dbs.ML. \
        symbol('ML-datasets-codes.xls', 'Name', 'Code', read_excel). \
        downloader().set(code_builder=identity, name_builder=identity). \
        set(english_to_symbol_indicator=default_english_to_symbol_indicator). \
        set(indicator_handler=make_default_indicator_handler(cc_indicator_to_percentages, cc_indicator_to_percentages)). \
        set_path('download_and_save', 'ML_data.csv'). \
        set_path('process', 'ML_processed_data.csv', 
                 compute_names=make_default_compute_names([], make_ML_col_handler()),
                 load=False). \
        set(symbol_name='ML', date_name='Date'). \
        set_path('downloaded_data', 'ML_data.csv')
        
    cc_info.set_path('combined_df', 'combined_cc_data.csv'). \
        combined_df.set(labels=['Date'], to_drop=[],
                        names=['DB', 'Indicator'], transformer=identity).up(). \
        set_path('analyzer', 'cc_model.pickle', load=False). \
        create_analyzer(creator=ml_analyzer_creator).set(y_key=[('ML', 'Future Percent change in %s' % name)
            for name in cc_indicator_to_percentages])
        
    return(cc_info)
    
from pandas import Series
from sklearn.linear_model import MultiTaskLasso
from systematic_investment import LongShortTradingModel

def cc_model_test_action(model):
    model.analyzer.print_analysis_results()
    #model.plot_hypothetical_portfolio()
    
class MultiTaskLassoInterop:
    def __init__(self, lm_y, lm_x):
        self._lm_x = lm_x
        self._lm_y = lm_y
        self._obj = MultiTaskLasso()
        
    def summary(self, xname, yname):
        coefs_to_print = DataFrame(self._obj.coef_)
        coefs_to_print.index = yname
        coefs_to_print.columns = xname
        
        intercept_to_print = Series(self._obj.intercept_)
        intercept_to_print.index=yname
        
        score_to_print = self._obj.score(self._lm_x, self._lm_y)
        
        return("Coefficients:\n%s\nIntercepts:\n%s\nR^2:\n%s" % 
            (coefs_to_print, intercept_to_print, score_to_print))
        
    def fit(self):
        self._obj.fit(self._lm_x, self._lm_y)
        self._obj.__setattr__('summary', self.summary)
        return(self._obj)
        
    
if __name__ == '__main__':
    info = get_cc_info()
    test_data_processing(info)
    test_models(info, cc_model_test_action, lambda info: LongShortTradingModel(info, constructor = MultiTaskLassoInterop))
    print("done")
    