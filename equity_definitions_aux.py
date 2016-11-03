#!/usr/bin/env python

"""
In progress

Provides additional definitions for the equity trading model.
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

from systematic_investment.shortcuts import *
from systematic_investment.data import *
from utils import *
from pandas import DataFrame, Timestamp, to_datetime, read_csv
from numpy import log, int64
import math
import statsmodels as sm

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
    
def meta_loader_creator(info):
    def res():
        wanted_columns = ['Ticker', 'Name', 'Sector', 'Industry']
        return(QuandlMetaDataLoader(wanted_columns, 'data/SF0-tickers.csv'))
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
    if df.index[0][0].__class__ != int64:
        res = df.dropna(how='all')
        is_good = [Timestamp(idx[0]) < Timestamp('2016-01-01') for idx in res.index.tolist()]
        res = res.loc[is_good]
        res = default_multi_index_resample_method(res)
        #res = res.unstack().stack()
        return(res)
    else:
        df.index=df['Name']
        df.drop('Name', inplace=True)
        df.drop_duplicates(inplace=True)
        return(df)
        
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