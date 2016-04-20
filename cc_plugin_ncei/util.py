#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/util.py
'''
from compliance_checker.base import Result, BaseCheck

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
    inst_vars = []
    instrument_name = getattr(ds, 'instrument', None)
    if instrument_name is not None:
        inst_vars = instrument_name.split(', ')
        return list(set(inst_vars))
    
    for k, v in ds.variables.items():
        if 'instrument' in k:
            if not v.shape:  # Empty dimension
                inst_vars.append(k)
    return list(set(inst_vars))

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


