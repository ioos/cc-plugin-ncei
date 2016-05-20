#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/util.py
'''
from compliance_checker.base import Result, BaseCheck
from pkg_resources import resource_filename
import csv

def _find_z_dimension(ds):
    for var in ds.variables:
        if getattr(ds.variables[var], 'axis', None) == 'Z':
            return var
    return None

def _find_platform_variables(ds):
    plat_vars = []
    platform_name = getattr(ds, 'platform', None)
    if platform_name is not None:
        plat_vars = platform_name.split(',')
        return list(set(plat_vars))

    for k, v in ds.variables.items():
        if 'platform' in k:
            if not v.shape:  # Empty dimension
                plat_vars.append(k)
    return list(set(plat_vars))


def _find_instrument_variables(ds):
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


def getattr_check(ds, var, attr, val, level):
    msgs = []
    if getattr(ds.variables[var], attr, None) == val:
        check = True
    else: 
        msgs = ['{} is wrong'.format(attr)]
        check = False
    return Result(level, check, (var,attr), msgs)

def hasattr_check(ds, var, attr, level):
    msgs = []
    if hasattr(ds.variables[var], attr):
        check = True
    else:
        msgs = ['{} is missing'.format(attr)]
        check = False
    return Result(level, check, (var,attr), msgs)

def var_dtype(ds, var, valid_types, level):
    msgs = []
    data_type = str(ds.variables[var].dtype)
    if any(valid_type in data_type for valid_type in valid_types):
        check = True
    else:
        msgs = ['data type for {} is invalid'.format(var)]
        check = False
    return Result(level, check, (var,'data_type'), msgs)


def _find_crs_variable(ds):
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


