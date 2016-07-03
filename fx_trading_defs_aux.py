#!/usr/bin/env python

"""
Provides additional definitions for the FX Trading Model.
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

from utils import *

from pandas import DataFrame, concat
    
def make_wb_col_handler():
    indicators = default_indicator_loader('wb_indicator_codes.xls')
    countries = default_indicator_loader('iso_codes.xls')
    def res(col):
        sym_ind = col.split(' - ')[0].split('.')[1].split('_', 1)
        
        indicator = indicators.loc[indicators['Code'] == sym_ind[1]]['Indicator Name'].iloc[0]
        country = countries.loc[countries['World Bank Code']==sym_ind[0]]['Country'].iloc[0]
        return('%s - %s' % (country, indicator))
    
    return(res)

wb_to_handle = [[#"Official exchange rate (LCU per US$, period average)",
     #"Official exchange rate (LCU per US$, end period)",
     "Export price index (goods and services, 2000=100)",
     "Import price index (goods and services 2000=100)",
     "Average precipitation in depth (mm per year)",
     "Bank capital to assets ratio (%)",
     "Global Competitiveness Index (GCI)",
     "Real interest rate (%)",
     "Return on assets (%)",
     "Return on equity (%)"],
    []]
    
def load_oecd_qd_codes():
        # The OECD database is poorly designed with no documentation.
        #hourly earnings manufacturing 
        oecd_qd_codes = {'Name': [], 'Code': []}
        ind_name, ind_code = "Composite Leading Index", "OECD/MEI_CLI_LOLITOAA"
        ends = dict(zip(["Monthly", "Quarterly", "Annually", ""], ["_M", "_Q", "_A", ""]))
        
        for period_name, period_code in ends.items():
            for country, country_code in default_indicator_loader('iso_codes.xls').items():
                name = "%s: %s, %s" % (country, ind_name, period_name)
                code = "%s_%s%s" % (ind_code, country_code, period_code)
                
                oecd_qd_codes['Name'].append(name)
                oecd_qd_codes['Code'].append(code)
        
        return DataFrame(oecd_qd_codes)
        
def load_currfx_currency_codes():
    res = fix_read_excel('iso_currency_codes.xls')[['ENTITY', 'Alphabetic Code']]
    res = res.loc[:267] # metals and test codes
    res.columns = ['Country', 'Code']
    return(res)
    
def load_currfx_qd_codes():
    currency_codes = load_currfx_currency_codes()
    res = concat([currency_codes['Country'], currency_codes[['Code']].applymap(lambda x: 'CURRFX/%sUSD' % x)], axis=1)
    return(res)
    
def make_currfx_col_handler():
    codes = load_currfx_qd_codes()
    def res(col_name):
        qd_code = col_name.split(' - ')[0].replace('.', '/')
        quote_type = col_name.split(' - ')[1].split('_')[0].split('.')[0]
        country = codes.loc[codes['Code']==qd_code]['Country'].iloc[0]
        return('%s - %s' % (country, quote_type))
    return(res)
    
def currfx_english_to_symbol_indicator(english):
    sym_ind = english.split(' - ')
    return sym_ind[0], 'CURRFX ' + sym_ind[1]
    
def load_cftc_contracts():
    df = fix_read_excel('cftc_contracts.xls', converters={"Symbol": str})
    return(df)
    
def cftc_col_handler(col_name):
    contract_indicator = col_name.split('.')[1].split(' - ')
    contract = contract_indicator[0].split('_')[0]
    indicator = contract_indicator[1]
    
    contract = cftc_contracts.loc[cftc_contracts['Symbol']==contract]['Name'].iloc[0]
    contract = reconciliation.loc[reconciliation['CFTC Name']==contract]['Country'].iloc[0]
    #sym_name = list(cftc_contracts.keys())[list(cftc_contracts.values()).index(sym)]
    return('%s - %s' % (contract, indicator))
    
def oecd_col_handler(col):
    c = col.split('_')[3]
    country = countries.loc[countries['World Bank Code'] == c]['Country'].iloc[0]
    return('%s - %s' % (country, 'Composite Leading Index'))
    
def load_uifs_countries():
    uifs_countries = fix_read_excel('uifs_codes.xls', converters={'CODE': str})   
    return(dict(zip(uifs_countries['COUNTRY or AREA'], uifs_countries['CODE'])))
    
def make_uifs_col_handler():
    countries = load_uifs_countries()
    def res(col_name):
        rm_ugid = col_name.split('.')[1]
        c_eng = rm_ugid.split('_')[1].split(' - ')
        c_code = c_eng[0]
        country = list(countries.keys())[list(countries.values()).index(c_code)]
        eng = c_eng[1].split('(')[0]
        
        return('%s - %s' % (country, eng))
    return(res)
    
def combined_df_transformer(df):
    level = df.index.levels[1].tolist()
    level = [name.upper() for name in level]
    df.index.set_levels(level, 1, inplace=True)
    return(df)
    
def load_analyzer_func(info):
    def res():
        return(DFAnalyzer.load(info["create_analyzer"]["path"]))
    return(res)