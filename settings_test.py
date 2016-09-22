# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 13:33:59 2016

@author: davidadelberg
"""

from systematic_investment import Settings

created = Settings.create('test_settings')

def get_sp500_info():
    sp_info = Settings(data_dir=data_dir, authtoken=david_authtoken, main_db_name='YALE')
    sp_info.dbs.YALE. \
        symbol('yale_sp500.xls', 'Name', 'Code', read_excel). \
        downloader().set(indicator_handler=make_default_indicator_handler(['CPI', 'Earnings', 'Long Interest Rate', 'S&P Composite'], ['S&P Composite'])). \
        set_path('download_and_save', 'yale_data.csv'). \
        set_path('process', 'yale_processed_data.csv', compute_names=make_default_compute_names([], make_sp_col_handler()), load=False). \
        set(symbol_name='S&P500', date_name='Date'). \
        set_path('downloaded_data', 'yale_data.csv')
    
    sp_info.set_path('combined_df', "combined_sp500_data.csv"). \
        combined_df.set(labels= ['Date'], to_drop=['Dividend', 'Real Dividend', 'Real Earnings', 'Real Price'], names=["DB", "Indicator"], transformer=identity).up(). \
        set_path('analyzer', 'sp500_model.pickle', load=False). \
        create_analyzer(creator=sp_analyzer_creator).set(y_key=('YALE', "Future Percent change in S&P Composite"))
    
    return(sp_info)
    
print('done')