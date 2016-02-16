#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_timeseries.py
'''

from compliance_checker.base import Result, BaseCheck
from cc_plugin_ncei.ncei_metadata import NCEIMetadataCheck
import cf_units
import numpy as np

class NCEITimeSeriesOrthogonal(NCEIMetadataCheck):
    register_checker = True
    name = 'ncei-timeseries-orthogonal'
    _cc_spec = 'NCEI NetCDF Templates'
    _cc_spec_version = '2.0'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesOrthogonal.cdl'
    _cc_authors = 'Luke Campbell'
    _cc_checker_version = '2.1.0'

    @classmethod
    def beliefs(cls): 
        '''
        Not applicable for gliders
        '''
        return {}

    def is_orthogonal(self, dataset):
        if 'time' not in dataset.dimensions:
            return False

        return nc.variables['time'].dimensions == ('time',)


    def check_dimensions(self, dataset):
        '''
        NCEI_TimeSeries_Orthogonal
        dimensions:
           time = < dim1 >;//..... REQUIRED - Number of time steps in the time series
           timeSeries = <dim2>; // REQUIRED - Number of time series (=1 for single time series or can be removed)

        NCEI_TimeSeries_Incomplete
        dimensions:
            ntimeMax = < dim1 >;//. REQUIRED - Number of time steps in the time series
            timeSeries = <dim2>; // REQUIRED - Number of time series
        '''
        level = BaseCheck.HIGH
        out_of = 2
        score = 0
        messages = []

        test = 'time' in dataset.dimensions

        if test:
            score += 1
        else:
            messages.append('time is a required dimension for TimeSeries Orthogonal')

        test = 'time' in dataset.variables and dataset.variables['time'].dimensions == ('time',)

        if test:
            score += 1
        else:
            messages.append('time is required to be a coordinate variable')

        return self.make_result(level, score, out_of, 'Dataset contains required time dimensions', messages)



