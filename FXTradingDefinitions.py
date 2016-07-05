#!/usr/bin/env python

"""
Provides definitions for the FX Trading Model.
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
from fx_trading_defs_aux import *
    
def get_fx_info():
    fx_info = Info(data_dir=data_dir, authtoken=sam_authtoken, main_db_name="WORLDBANK")
    
    fx_info.dbs.WORLDBANK. \
        symbol('iso_codes.xls', 'Country', 'World Bank Code', read_excel). \
        symbol('wb_indicator_codes.xls', 'Indicator Name', 'Code', read_excel). \
        downloader(). \
        set(code_builder=make_default_code_builder('WORLDBANK')). \
        set(name_builder=default_name_builder). \
        set(english_to_symbol_indicator=default_english_to_symbol_indicator). \
        set(indicator_handler=make_default_indicator_handler(*wb_to_handle)). \
        set_path('download_and_save', 'wb_data.csv'). \
        set_path('process', 'wb_processed_data.csv',
                 compute_names=make_default_compute_names(['Date'], make_wb_col_handler()), load=True). \
        set(symbol_name='Country', date_name='Date'). \
        set_path('downloaded_data', 'wb_data.csv')
        #set_path('all_codes', "all_world_bank_codes.csv", loader = read_csv_iso). \
        
    fx_info.dbs.CFTC. \
        symbol('cftc_contracts.xls', 'Name', 'Symbol', read_excel). \
        symbol('cftc_indicators.xls', 'Name', 'Code', read_excel). \
        downloader(). \
        set(code_builder=make_default_code_builder('CFTC')). \
        set(name_builder=default_name_builder). \
        set(english_to_symbol_indicator=default_english_to_symbol_indicator). \
        set(indicator_handler=make_default_indicator_handler([],[])). \
        set_path('download_and_save', 'cftc_data.csv'). \
        set_path('process', 'cftc_processed_data.csv', compute_names=make_default_compute_names(['Date'], cftc_col_handler), load=True). \
        set(symbol_name='Country', date_name='Date'). \
        set_path('downloaded_data', 'cftc_data.csv')
        
    fx_info.dbs.OECD.downloader().set_path('downloaded_data', 'oecd_data.csv'). \
        compute_wanted_codes.set(data=load_oecd_qd_codes()).up(). \
        set(english_to_symbol_indicator=default_english_to_symbol_indicator). \
        set(indicator_handler=make_default_indicator_handler([],[])). \
        set_path('download_and_save', 'oecd_data.csv'). \
        set_path('process', 'oecd_processed_data.csv', compute_names=make_default_compute_names([], oecd_col_handler), load=True). \
        set(symbol_name='Country', date_name='Date')
    
        #set_path('all_codes', 'all_oecd_codes.csv')
    
    fx_info.dbs.CURRFX.downloader(). \
        compute_wanted_codes.set(data=load_currfx_qd_codes()).up(). \
        set_path('downloaded_data', 'currfx_data.csv'). \
        set_path('download_and_save', 'currfx_data.csv'). \
        set_path('process', 'currfx_processed_data.csv',
                 compute_names=make_default_compute_names([], make_currfx_col_handler()), load=True). \
        set(english_to_symbol_indicator = currfx_english_to_symbol_indicator). \
        set(indicator_handler=make_default_indicator_handler(['CURRFX Rate'], ['CURRFX Rate'])). \
        set(symbol_name='Country', date_name='Date')
    
    fx_info.dbs.UIFS.set_path('downloaded_data', 'uifs_data.csv'). \
        downloader().symbol('uifs_codes.xls', 'COUNTRY or AREA', 'CODE', read_excel). \
        symbol('uifs_indicators.xls', 'Name', 'Code', read_excel). \
        set(code_builder=make_default_code_builder('UIFS'), name_builder=default_name_builder). \
        set(english_to_symbol_indicator=default_english_to_symbol_indicator). \
        set(indicator_handler=make_default_indicator_handler([],[])). \
        set_path('download_and_save', 'uifs_data.csv'). \
        set_path('process', 'uifs_processed_data.csv', compute_names=make_default_compute_names(['Date'], make_uifs_col_handler()), load=True). \
        set(symbol_name='Country', date_name='Date')
        
    to_drop = ['Official exchange rate (LCU per US$, end period)',
                    'Official exchange rate (LCU per US$, period average)',
                    'Percent change in Official exchange rate (LCU per US$, period average)',
                    'Ease of doing business index (1=most business-friendly regulations)',
                    'London Interbank Offered 3-month rates (LIBOR)',
                    'London Interbank Offered 6-month rates (LIBOR)',
                    'Mainland',
                    'Paying taxes (rank)',
                    'Protecting investors (rank)',
                    'CURRFX Low (est)',
                    'CURRFX High (est)']
        
    fx_info.set_path('combined_df', 'combined_fx_data.csv'). \
            combined_df.set(labels=['Date', 'Country'], to_drop=to_drop, transformer=combined_df_transformer). \
                        set(names=['DB', 'Indicator']). \
                        up(). \
            set_path('analyzer', 'fx_model.pickle', load=False). \
            create_analyzer(). \
            set(y_key=('CURRFX', 'Future Percent change in CURRFX Rate')) # Shouldn't have to do this. Maybe change in later version)
    
    return(fx_info)


from systematic_investment import test_data_processing, test_models
from systematic_investment import LongOnlyTradingModel, ShortOnlyTradingModel
    
def fx_model_test_action(model):
    #model.boxplots_by('Country')
    #model.boxplots_by('Date')
    #model.plot_historic_returns()
    model.plot_hypothetical_portfolio()
    
if __name__ == '__main__':
    info = get_fx_info()
    test_data_processing(info)
    test_models(info, fx_model_test_action, LongOnlyTradingModel, ShortOnlyTradingModel)
    print("done")