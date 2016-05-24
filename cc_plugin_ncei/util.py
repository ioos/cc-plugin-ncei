#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/util.py
'''
from compliance_checker.base import Result, BaseCheck
from pkg_resources import resource_filename
import csv
        
def find_z_dimension(ds):
    '''
    Returns the variable which is likeliest to be the Z coordinate variable
    '''
    for var in ds.variables:
        if getattr(ds.variables[var], 'axis', None) == 'Z':
            return var

    return None


def find_platform_variables(ds):
    '''
    Returns a list of platform variable NAMES
    '''
    candidates = []
    for variable in ds.variables:
        platform = getattr(ds.variables[variable], 'platform', '')
        if platform and platform in ds.variables:
            if platform not in candidates:
                candidates.append(platform)

    platform = getattr(ds, 'platform', '')
    if platform and platform in ds.variables:
        if platform not in candidates:
            candidates.append(platform)
    return candidates


def find_instrument_variables(ds):
    '''
    Returns a list of instrument variables
    '''
    candidates = []
    for variable in ds.variables:
        instrument = getattr(ds.variables[variable], 'instrument', '')
        if instrument and instrument in ds.variables:
            if instrument not in candidates:
                candidates.append(instrument)

    instrument = getattr(ds, 'instrument', '')
    if instrument and instrument in ds.variables:
        if instrument not in candidates:
            candidates.append(instrument)
    return candidates


def find_time_variable(ds):
    '''
    Returns the likeliest variable to be the time coordiante variable
    '''
    for var in ds.variables:
        if getattr(ds.variables[var], 'axis', '') == 'T':
            return var
    else:
        candidates = ds.get_variables_by_attributes(standard_name='time')
        if len(candidates) == 1:
            return candidates[0]

    return None


def getattr_check(ds, var, attr, val, level):
    '''
    Returns a Result object with the value (boolean) set to True if var has attr and is equal to val

    :param netCDF4.Dataset ds: An open netCDF4 dataset
    :param str var: Name of the variable
    :param str attr: Name of the attribute
    :param int level: Level of importance BaseCheck.LOW, BaseCheck.HIGH etc.
    '''
    msgs = []
    attr_value = getattr(ds.variables[var], attr, None) == val
    if attr_value:
        check = True
    else: 
        msgs = ['{} is missing attribute {}, which should have a value of {}: {}'.format(var, attr, val, attr_value)]
        check = False
    return Result(level, check, '{} has attribute {}'.format(var, attr), msgs)


def hasattr_check(ds, var, attr, level):
    '''
    Returns a Result object with the value (boolean) set to True if var has attr
    '''
    msgs = []
    if hasattr(ds.variables[var], attr):
        check = True
    else:
        msgs = ['{} is missing attribute {}'.format(var, attr)]
        check = False
    return Result(level, check, '{} has attribute {}'.format(var, attr), msgs)


def var_dtype(ds, var, valid_types, level):
    '''
    Returns a Result object with the value (boolean) set to True if the
    variable has a dtype in valid_types
    '''
    msgs = []
    data_type = str(ds.variables[var].dtype)
    if any(valid_type in data_type for valid_type in valid_types):
        check = True
    else:
        msgs = ['data type for {} is invalid'.format(var)]
        check = False
    return Result(level, check, '{} correct data type'.format(var), msgs)


def find_crs_variable(ds):
    for var in ds.variables:
        grid_mapping = getattr(ds.variables[var], 'grid_mapping', '')
        if grid_mapping and grid_mapping in ds.variables:
            return ds.variables[grid_mapping]
    return None

_SEA_NAMES = None


def get_sea_names():
    global _SEA_NAMES
    if _SEA_NAMES is None:
        buf = {}
        with open(resource_filename('cc_plugin_ncei', 'data/seanames.csv'), 'r') as f:
            reader = csv.reader(f)
            for code, sea_name in reader:
                buf[sea_name] = code
        _SEA_NAMES = buf
    return _SEA_NAMES


