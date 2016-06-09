#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/util.py
'''
from compliance_checker.base import Result, BaseCheck
from pkg_resources import resource_filename
import csv


def is_geophysical(ds, variable):
    '''
    Returns true if the dataset's variable is likely a geophysical variable
    '''
    ncvar = ds.variables[variable]
    # Does it have a standard name and units?
    if not hasattr(ncvar, 'standard_name') or not hasattr(ncvar, 'units'):
        return False
    if getattr(ncvar, 'standard_name') in ('time', 'latitude', 'longitude', 'height', 'depth'):
        return False
    # Is it dimensionless?
    if len(ncvar.shape) == 0:
        return False
    # Is it a QC Flag?
    if 'status_flag' in ncvar.standard_name:
        return False

    if getattr(ncvar, 'cf_role', None):
        return False

    if getattr(ncvar, 'axis', None):
        return False

    return True


def get_geophysical_variables(ds):
    '''
    Returns a list of geophysical variables
    '''

    parameters = []
    for variable in ds.variables:
        if is_geophysical(ds, variable):
            parameters.append(variable)
    return parameters


def find_z_dimension(ds):
    '''
    Returns the variable which is likeliest to be the Z coordinate variable
    '''
    for var in ds.variables:
        if getattr(ds.variables[var], 'axis', None) == 'Z':
            return var

    return None


def get_lat_variable(nc):
    '''
    Returns the variable for latitude

    :param netcdf4.dataset nc: an open netcdf dataset object
    '''
    if 'latitude' in nc.variables:
        return 'latitude'
    latitudes = nc.get_variables_by_attributes(standard_name="latitude")
    if latitudes:
        return latitudes[0]
    return None


def get_lon_variable(nc):
    '''
    Returns the variable for longitude

    :param netCDF4.Dataset nc: netCDF dataset
    '''
    if 'longitude' in nc.variables:
        return 'longitude'
    longitudes = nc.get_variables_by_attributes(standard_name="longitude")
    if longitudes:
        return longitudes[0]
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


# alias for backwards compatibility
get_depth_variable = find_z_dimension
get_time_variable = find_time_variable


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


def is_point(nc, variable):
    '''
    Returns true if the variable is a point feature type

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    '''
    # x(o), y(o), z(o), t(o)
    # X(o)

    dims = nc.variables[variable].dimensions

    t = get_time_variable(nc)
    if not t:
        return False

    if not nc.variables[t].dimensions:
        return False
    o = nc.variables[t].dimensions[0]

    x = get_lon_variable(nc)
    y = get_lat_variable(nc)
    z = get_depth_variable(nc)

    if not x:
        return False
    if nc.variables[x].dimensions != (o,):
        return False
    if not y:
        return False
    if nc.variables[y].dimensions != (o,):
        return False
    if z and nc.variables[z].dimensions != (o,):
        return False

    if dims == (o,):
        return True
    return False


def is_timeseries(nc, variable):
    '''
    Returns true if the variable is a time series feature type.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    '''

    # x, y, z, t(o)
    # X(o)
    dims = nc.variables[variable].dimensions

    x = get_lon_variable(nc)
    y = get_lat_variable(nc)
    z = get_depth_variable(nc)

    if not x:
        return False
    if nc.variables[x].dimensions:
        return False
    if not y:
        return False
    if nc.variables[y].dimensions:
        return False
    if z and nc.variables[z].dimensions:
        return False

    timevar = get_time_variable(nc)
    if nc.variables[timevar].dimensions != (timevar,):
        return False

    if dims == (timevar,):
        return True
    return False


def is_multi_timeseries_orthogonal(nc, variable):
    '''
    Returns true if the variable is a orthogonal multidimensional array
    representation of time series. For more information on what this means see
    CF 1.6 §H.2.1

    http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#_orthogonal_multidimensional_array_representation_of_time_series

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    '''
    # x(i), y(i), z(i), t(o)
    # X(i, o)
    dims = nc.variables[variable].dimensions
    timeseries_ids = nc.get_variables_by_attributes(cf_role='timeseries_id')
    if not timeseries_ids:
        return False

    timeseries_id_dims = timeseries_ids[0].dimensions
    if not timeseries_id_dims:
        return False

    # i = series_id
    # i is the dimension of the variable where cf_role = 'timeseries_id'
    series_id = timeseries_id_dims[0]

    x = get_lon_variable(nc)
    y = get_lat_variable(nc)
    z = get_depth_variable(nc)

    if not x:
        return False
    if nc.variables[x].dimensions != (series_id,):
        return False
    if not y:
        return False
    if nc.variables[y].dimensions != (series_id,):
        return False
    if z and nc.variables[z].dimensions != (series_id,):
        return False

    # time is a variable with standard name and with dimensions (time)
    timevar = get_time_variable(nc)
    time_dims = nc.variables[timevar].dimensions
    if time_dims != (timevar,):
        return False

    # o = time_dim
    if dims == (series_id, timevar):
        return True

    return False


def is_multi_timeseries_incomplete(nc, variable):
    '''
    Returns true if the variable is an incomplete multidimensional array
    representation of time series. For more information on what this means see
    CF 1.6 §H.2.2

    http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#_incomplete_multidimensional_array_representation_of_time_series

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    '''

    # x(i), y(i), z(i), t(i, o)
    # X(i, o)
    dims = nc.variables[variable].dimensions
    timeseries_ids = nc.get_variables_by_attributes(cf_role='timeseries_id')
    if not timeseries_ids:
        return False

    timeseries_id_dims = timeseries_ids[0].dimensions
    if not timeseries_id_dims:
        return False
    # i = series_id
    # i is the dimension of the variable where cf_role = 'timeseries_id'
    series_id = timeseries_id_dims[0]

    # time is a variable with standard name and with dimensions (i, o)

    x = get_lon_variable(nc)
    y = get_lat_variable(nc)
    z = get_depth_variable(nc)

    if not x:
        return False
    if nc.variables[x].dimensions != (series_id,):
        return False
    if not y:
        return False
    if nc.variables[y].dimensions != (series_id,):
        return False
    if z and nc.variables[z].dimensions != (series_id,):
        return False
    timevar = get_time_variable(nc)
    time_dims = nc.variables[timevar].dimensions

    if len(time_dims) != 2:
        return False
    if time_dims[0] != series_id:
        return False

    # o = time_dim
    time_dim = time_dims[-1]

    if dims == (series_id, time_dim):
        return True
    return False


def is_cf_trajectory(nc, variable):
    '''
    Returns true if the variable is a CF trajectory feature type

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    '''
    # x(i, o), y(i, o), z(i, o), t(i, o)
    # X(i, o)
    dims = nc.variables[variable].dimensions
    trajectory_ids = nc.get_variables_by_attributes(cf_role='trajectory_id')
    if not trajectory_ids:
        return False

    trajectory_dims = trajectory_ids[0].dimensions
    if not trajectory_dims:
        return False

    # i is the first dimension of the variable where cf_role = 'trajectory_id'
    i = trajectory_dims[0]

    # time is a variable with standard name and with dimensions (i, o)
    timevar = get_time_variable(nc)
    time_dims = nc.variables[timevar].dimensions

    if len(time_dims) != 2:
        return False
    if time_dims[0] != i:
        return False

    # o = time_dim
    o = time_dims[1]

    x = get_lon_variable(nc)
    y = get_lat_variable(nc)
    z = get_depth_variable(nc)

    if not x:
        return False
    if nc.variables[x].dimensions != (i, o):
        return False
    if not y:
        return False
    if nc.variables[y].dimensions != (i, o):
        return False
    if z and nc.variables[z].dimensions != (i, o):
        return False

    if dims == (i, o):
        return True
    return False


