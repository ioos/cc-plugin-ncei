#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
compliance_checker.glider_dac

Compliance Test Suite for the IOOS National Glider Data Assembly Center
https://github.com/ioos/ioosngdac/wiki
'''

from compliance_checker.base import BaseCheck, BaseNCCheck, Result
import cf_units
import numpy as np

class NCEITimeSeries(BaseNCCheck):
    register_checker = True
    name = 'ncei-timeseries'

    @classmethod
    def beliefs(cls): 
        '''
        Not applicable for gliders
        '''
        return {}

    @classmethod
    def make_result(cls, level, score, out_of, name, messages):
        return Result(level, (score, out_of), name, messages)

    def setup(self, ds):
        pass


    def check_time_required(self, ds):
        '''
        '''
        level = BaseCheck.HIGH
        out_of = 4
        score = 0
        messages = []

        if 'time' in ds.dataset.variables:
            score += 1
        else:
            messages.append("Variable time is missing and all supporting attributes")
            return self.make_result(level, score, out_of, 'Verifies time exists and is valid', messages)

        variable = ds.dataset.variables['time']
        
        if getattr(variable, "standard_name", None) == 'time':
            score += 1
        else:
            messages.append("Invalid standard_name for time")
            
        # Calendar is required if it's not default which is gregorian
        calendar = getattr(variable, "calendar", None)
        # Valid calendars come from CF 1.6 §4.4.1
        valid_calendars = ('gregorian', 'standard', 'proleptic_gregorian', 'noleap', '365_day', 'all_leap', '366_day', 'julian', 'none')
        if calendar is None or calendar.lower() in valid_calendars:
            score += 1
        else:
            messages.append("time has an invalid calendar: %s" % calendar)

        if getattr(variable, 'axis', None) == 'T':
            score += 1
        else:
            messages.append("time must define axis to be equal to 'T'")


        return self.make_result(level, score, out_of, 'Verifies time exists and is valid', messages)


