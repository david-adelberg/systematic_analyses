#!/usr/bin/env python

"""
In progress

Provides definitions for the Industry Trading Model.
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

import systematic_investments as si
from si.shortcuts import *
import DBSymbol

def get_industry_analysis_info():
    industry_info = {}
    
    domodaran_firm_industry = DBSymbol('domodaran_firm_industry_name.xls', NotImplementedError("Different Format"))
    
    domodaran_info = {}
    domodaran_info["symbols"] = domodaran_firm_industry
    domodaran_info["create_downloader"] = None
    domodaran_info["code_builder"] = None
    domodaran_info["name_builder"] = None
    raise(NotImplementedError("Need to Architect this, may be different from other analyses."))