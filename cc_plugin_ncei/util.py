"""cc_plugin_ncei/util.py."""

import functools
import json
from pathlib import Path
from pkgutil import get_data

from lxml import etree


@functools.lru_cache(maxsize=128)
def get_unitless_standard_names():
    """Return a list of valid standard_names that are allowed to be unitless."""
    resource_filename = Path(__file__).parent
    f = resource_filename.joinpath("data/unitless.json").read_text()
    return json.loads(f)


@functools.lru_cache(maxsize=128)
def get_sea_names():
    """Return a list of NODC sea names.

    source of list: http://www.nodc.noaa.gov/General/NODC-Archive/seanames.xml
    """
    resource_text = get_data("cc_plugin_ncei", "data/seanames.xml")
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(resource_text, parser)
    _sea_names = {}
    for seaname in root.findall("seaname"):
        name = seaname.find("seaname").text
        _sea_names[name] = (
            seaname.find("seacode").text
            if seaname.find("seacode") is not None
            else "N/A"
        )

    return _sea_names


def is_geophysical(ds, variable):
    """Return true if the dataset's variable is likely a geophysical variable."""
    ncvar = ds.variables[variable]
    # Does it have a standard name and units?
    standard_name = getattr(ncvar, "standard_name", "")
    if not standard_name:
        return False
    if standard_name and standard_name not in get_unitless_standard_names():
        units = getattr(ncvar, "units", "")
        if units == "":
            return False
    if not hasattr(ncvar, "standard_name") or not hasattr(ncvar, "units"):
        return False
    if ncvar.standard_name in (
        "time",
        "latitude",
        "longitude",
        "height",
        "depth",
        "altitude",
    ):
        return False
    # Is it dimensionless? or  a QC Flag or cf_role?
    if (
        len(ncvar.shape) == 0
        or "status_flag" in ncvar.standard_name
        or getattr(ncvar, "cf_role", None)
    ):
        return False

    return not getattr(ncvar, "axis", None)


def get_geophysical_variables(ds):
    """Return a list of variable names for the variables detected as geophysical variables.

    :param netCDF4.Dataset nc: An open netCDF dataset
    """
    return [
        variable for variable in ds.variables if is_geophysical(ds, variable)
    ]


def get_z_variable(nc):
    """Return the name of the variable that defines the Z axis or height/depth.

    :param netCDF4.Dataset nc: netCDF dataset
    """
    axis_z = nc.get_variables_by_attributes(axis="Z")
    if axis_z:
        return axis_z[0].name
    valid_standard_names = ("depth", "height", "altitude")
    z = nc.get_variables_by_attributes(
        standard_name=lambda x: x in valid_standard_names,
    )
    if z:
        return z[0].name
    return None


def get_lat_variable(nc):
    """Return the variable for latitude.

    :param netcdf4.dataset nc: an open netcdf dataset object
    """
    if "latitude" in nc.variables:
        return "latitude"
    latitudes = nc.get_variables_by_attributes(standard_name="latitude")
    if latitudes:
        return latitudes[0].name
    return None


def get_lon_variable(nc):
    """Return the variable for longitude.

    :param netCDF4.Dataset nc: netCDF dataset
    """
    if "longitude" in nc.variables:
        return "longitude"
    longitudes = nc.get_variables_by_attributes(standard_name="longitude")
    if longitudes:
        return longitudes[0].name
    return None


def get_platform_variables(ds):
    """Return a list of platform variable NAMES.

    :param netCDF4.Dataset ds: An open netCDF4 Dataset
    """
    candidates = []
    for variable in ds.variables:
        platform = getattr(ds.variables[variable], "platform", "")
        if (
            platform
            and platform in ds.variables
            and platform not in candidates
        ):
            candidates.append(platform)

    platform = getattr(ds, "platform", "")
    if platform and platform in ds.variables and platform not in candidates:
        candidates.append(platform)
    return candidates


def get_instrument_variables(ds):
    """Return a list of instrument variables.

    :param netCDF4.Dataset ds: An open netCDF4 Dataset
    """
    candidates = []
    for variable in ds.variables:
        instrument = getattr(ds.variables[variable], "instrument", "")
        if (
            instrument
            and instrument in ds.variables
            and instrument not in candidates
        ):
            candidates.append(instrument)

    instrument = getattr(ds, "instrument", "")
    if (
        instrument
        and instrument in ds.variables
        and instrument not in candidates
    ):
        candidates.append(instrument)
    return candidates


def get_time_variable(ds):
    """Return the likeliest variable to be the time coordinate variable.

    :param netCDF4.Dataset ds: An open netCDF4 Dataset
    """
    for var in ds.variables:
        if getattr(ds.variables[var], "axis", "") == "T":
            return var
    candidates = ds.get_variables_by_attributes(standard_name="time")
    if len(candidates) == 1:
        return candidates[0].name
    # Look for a coordinate variable time
    for candidate in candidates:
        if candidate.dimensions == (candidate.name,):
            return candidate.name

    return None


def get_crs_variable(ds):
    """Return the name of the variable identified by a grid_mapping attribute.

    :param netCDF4.Dataset ds: An open netCDF4 Dataset
    """
    for var in ds.variables:
        grid_mapping = getattr(ds.variables[var], "grid_mapping", "")
        if grid_mapping and grid_mapping in ds.variables:
            return grid_mapping
    return None


def coordinate_dimension_matrix(nc):
    """Return a dictionary of coordinates mapped to their dimensions.

    :param netCDF4.Dataset nc: An open netCDF dataset
    """
    retval = {}
    x = get_lon_variable(nc)
    if x:
        retval["x"] = nc.variables[x].dimensions
    y = get_lat_variable(nc)
    if y:
        retval["y"] = nc.variables[y].dimensions

    z = get_z_variable(nc)
    if z:
        retval["z"] = nc.variables[z].dimensions

    t = get_time_variable(nc)
    if t:
        retval["t"] = nc.variables[t].dimensions
    return retval


def is_point(nc, variable):
    """Return true if the variable is a point feature type.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(o), y(o), z(o), t(o)
    # X(o)

    dims = nc.variables[variable].dimensions

    cmatrix = coordinate_dimension_matrix(nc)
    for req in ("x", "y", "t"):
        if req not in cmatrix:
            return False
    t = get_time_variable(nc)
    if cmatrix["x"] != cmatrix["y"] or cmatrix["x"] != cmatrix["t"]:
        return False
    # This is a trajectory
    if cmatrix["t"] == (t,):
        return False
    if len(cmatrix["x"]) != 1:
        return False
    if "z" in cmatrix and cmatrix["x"] != cmatrix["z"]:
        return False
    return dims == cmatrix["x"]


def is_timeseries(nc, variable):
    """Return true if the variable is a time series feature type.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x, y, z, t(o)
    # X(o)
    dims = nc.variables[variable].dimensions

    cmatrix = coordinate_dimension_matrix(nc)
    for req in ("x", "y", "t"):
        if req not in cmatrix:
            return False
    if len(cmatrix["x"]) != 0:
        return False
    if len(cmatrix["y"]) != 0:
        return False
    if "z" in cmatrix and len(cmatrix["z"]) != 0:
        return False
    timevar = get_time_variable(nc)

    # time has to be a coordinate variable in this case
    if cmatrix["t"] != (timevar,):
        return False
    return dims == cmatrix["t"]


def is_multi_timeseries_orthogonal(nc, variable):
    """Return true if the variable is a orthogonal multidimensional array representation of time series.

    For more information on what this means see CF 1.6 §H.2.1.

    http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#_orthogonal_multidimensional_array_representation_of_time_series

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(i), y(i), z(i), t(o)
    # X(i, o)
    dims = nc.variables[variable].dimensions

    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "t"):
        if req not in cmatrix:
            return False
    if len(cmatrix["x"]) != 1 or cmatrix["x"] != cmatrix["y"]:
        return False
    if "z" in cmatrix and cmatrix["x"] != cmatrix["z"]:
        return False

    timevar = get_time_variable(nc)
    if cmatrix["t"] != (timevar,):
        return False

    i = cmatrix["x"][0]
    o = cmatrix["t"][0]
    return dims == (i, o)


def is_multi_timeseries_incomplete(nc, variable):
    """Return true if the variable is an incomplete multidimensional array representation of time series.

    For more information on what this means see CF 1.6 §H.2.2.

    http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#_incomplete_multidimensional_array_representation_of_time_series

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(i), y(i), z(i), t(i, o)
    # X(i, o)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "t"):
        if req not in cmatrix:
            return False
    if len(cmatrix["x"]) != 1:
        return False
    if cmatrix["x"] != cmatrix["y"]:
        return False
    if len(cmatrix["t"]) != 2:
        return False
    if cmatrix["x"][0] != cmatrix["t"][0]:
        return False

    i = cmatrix["x"][0]
    o = cmatrix["t"][1]

    return dims == (i, o)


def is_cf_trajectory(nc, variable):
    """Return true if the variable is a CF trajectory feature type.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(i, o), y(i, o), z(i, o), t(i, o)
    # X(i, o)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "t"):
        if req not in cmatrix:
            return False
    if len(cmatrix["x"]) != 2:
        return False
    if cmatrix["x"] != cmatrix["y"]:
        return False
    if cmatrix["x"] != cmatrix["t"]:
        return False
    if "z" in cmatrix and cmatrix["x"] != cmatrix["z"]:
        return False
    return dims == cmatrix["x"]


def is_single_trajectory(nc, variable):
    """Return true if the variable is a single trajectory feature.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(t), y(t), z(t), t(t)
    # X(t)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "t"):
        if req not in cmatrix:
            return False
    t = get_time_variable(nc)
    if cmatrix["x"] != (t,):
        return False
    if cmatrix["x"] != cmatrix["y"]:
        return False
    if cmatrix["x"] != cmatrix["t"]:
        return False
    if "z" in cmatrix and cmatrix["x"] != cmatrix["z"]:
        return False
    return dims == cmatrix["x"]


def is_profile_orthogonal(nc, variable):
    """Return true if the variable is a orthogonal profile feature type.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # Every profile has the exact same depths, think thermister or ADCP
    # x(i), y(i), z(j), t(i)
    # X(i, j)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False
    if len(cmatrix["x"]) != 1:
        return False
    if cmatrix["x"] != cmatrix["y"]:
        return False
    if cmatrix["x"] != cmatrix["t"]:
        return False
    if len(cmatrix["z"]) != 1:
        return False

    i = cmatrix["x"][0]
    j = cmatrix["z"][0]

    return dims == (i, j)


def is_profile_incomplete(nc, variable):
    """Return true if the variable is a incomplete profile feature type.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # Every profile may have different depths
    # x(i), y(i), z(i, j), t(i)
    # X(i, j)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False
    if (
        len(cmatrix["x"]) != 1
        or cmatrix["x"] != cmatrix["y"]
        or cmatrix["x"] != cmatrix["t"]
        or len(cmatrix["z"]) != 2
        or cmatrix["z"][0] != cmatrix["x"][0]
    ):
        return False

    i = cmatrix["x"][0]
    j = cmatrix["z"][1]

    return dims == (i, j)


def is_timeseries_profile_single_station(nc, variable):
    """Return true if the variable is a time-series profile that represents a single station and each profile is the same length.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x, y, z(z), t(t)
    # X(t, z)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False
    if len(cmatrix["x"]) != 0 or cmatrix["x"] != cmatrix["y"]:
        return False

    z = get_z_variable(nc)
    if cmatrix["z"] != (z,):
        return False
    t = get_time_variable(nc)
    if cmatrix["t"] != (t,):
        return False

    return dims == (t, z)


def is_timeseries_profile_multi_station(nc, variable):
    """Return true if the variable is a time-series profile that represents multiple stations with orthogonal time and depth.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(i), y(i), z(z), t(t)
    # X(i, t, z)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False
    if len(cmatrix["x"]) != 1:
        return False
    if cmatrix["x"] != cmatrix["y"]:
        return False
    i = cmatrix["x"][0]

    z = get_z_variable(nc)
    if cmatrix["z"] != (z,):
        return False
    t = get_time_variable(nc)
    if cmatrix["t"] != (t,):
        return False

    return dims == (i, t, z)


def is_timeseries_profile_single_ortho_time(nc, variable):
    """Return true if the variable is a time-series profile that represents a single station with orthogonal time only.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x, y, z(t, j), t(t)
    # X(t, j)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False

    if len(cmatrix["x"]) != 0:
        return False
    if cmatrix["x"] != cmatrix["y"]:
        return False

    t = get_time_variable(nc)
    if cmatrix["t"] != (t,) or len(cmatrix["z"]) != 2 or cmatrix["z"][0] != t:
        return False

    j = cmatrix["z"][1]

    return dims == (t, j)


def is_timeseries_profile_multi_ortho_time(nc, variable):
    """Return true if the variable is a time-series profile that represents a multi station with orthogonal time only.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(i), y(i), z(i, t, j), t(t)
    # X(i, t, j)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False

    if len(cmatrix["x"]) != 1:
        return False
    if cmatrix["x"] != cmatrix["y"]:
        return False

    t = get_time_variable(nc)
    if cmatrix["t"] != (t,):
        return False

    if (
        len(cmatrix["z"]) != 3
        or cmatrix["z"][1] != t
        or cmatrix["z"][0] != cmatrix["x"][0]
    ):
        return False

    i = cmatrix["x"][0]
    j = cmatrix["z"][2]

    return dims == (i, t, j)


def is_timeseries_profile_ortho_depth(nc, variable):
    """Return true if the variable is a time-series profile with orthogonal depth only.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(i), y(i), z(z), t(i, j)
    # X(i, j, z)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False

    if len(cmatrix["x"]) != 1 or cmatrix["x"] != cmatrix["y"]:
        return False

    z = get_z_variable(nc)
    if cmatrix["z"] != (z,):
        return False

    i = cmatrix["x"][0]

    if len(cmatrix["t"]) != 2 or cmatrix["t"][0] != i:
        return False

    j = cmatrix["t"][1]

    return dims == (i, j, z)


def is_timeseries_profile_incomplete(nc, variable):
    """Return true if the variable is a time-series profile incomplete depth and incomplete time.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(i), y(i), z(i, j, k), t(i, j)
    # X(i, j, k)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False

    if len(cmatrix["x"]) != 1 or cmatrix["x"] != cmatrix["y"]:
        return False
    i = cmatrix["x"][0]

    if len(cmatrix["t"]) != 2 or cmatrix["t"][0] != i:
        return False
    j = cmatrix["t"][1]

    if len(cmatrix["z"]) != 3 or cmatrix["z"][0] != i or cmatrix["z"][1] != j:
        return False
    k = cmatrix["z"][2]

    return dims == (i, j, k)


def is_trajectory_profile_orthogonal(nc, variable):
    """Return true if the variable is a trajectory profile with orthogonal depths.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(i, o), y(i, o), z(z), t(i, o)
    # X(i, o, z)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False

    if len(cmatrix["x"]) != 2:
        return False
    if cmatrix["x"] != cmatrix["y"]:
        return False
    if cmatrix["x"] != cmatrix["t"]:
        return False

    i, o = cmatrix["x"]

    z = get_z_variable(nc)
    if cmatrix["z"] != (z,):
        return False

    return dims == (i, o, z)


def is_trajectory_profile_incomplete(nc, variable):
    """Return true if the variable is a trajectory profile with incomplete depths.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(i, o), y(i, o), z(i, o, j), t(i, o)
    # X(i, o, j)
    dims = nc.variables[variable].dimensions
    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False

    if (
        len(cmatrix["x"]) != 2
        or cmatrix["x"] != cmatrix["y"]
        or cmatrix["x"] != cmatrix["t"]
    ):
        return False

    i, o = cmatrix["x"]

    if len(cmatrix["z"]) != 3 or cmatrix["z"][0] != i or cmatrix["z"][1] != o:
        return False

    j = cmatrix["z"][2]

    return dims == (i, o, j)


def is_2d_regular_grid(nc, variable):
    """Return True if the variable is a 2D Regular grid.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(x), y(y), t(t)
    # X(t, y, x)

    dims = nc.variables[variable].dimensions

    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "t"):
        if req not in cmatrix:
            return False

    x = get_lon_variable(nc)
    y = get_lat_variable(nc)
    t = get_time_variable(nc)

    if cmatrix["x"] != (x,):
        return False
    if cmatrix["y"] != (y,):
        return False
    if cmatrix["t"] != (t,):
        return False

    # Relaxed dimension ordering
    return len(dims) == 3 and x in dims and y in dims and t in dims


def is_3d_regular_grid(nc, variable):
    """Return True if the variable is a 3D Regular grid.

    :param netCDF4.Dataset nc: An open netCDF dataset
    :param str variable: name of the variable to check
    """
    # x(x), y(y), z(z), t(t)
    # X(t, z, y, x)

    dims = nc.variables[variable].dimensions

    cmatrix = coordinate_dimension_matrix(nc)

    for req in ("x", "y", "z", "t"):
        if req not in cmatrix:
            return False

    x = get_lon_variable(nc)
    y = get_lat_variable(nc)
    z = get_z_variable(nc)
    t = get_time_variable(nc)

    if cmatrix["x"] != (x,):
        return False
    if cmatrix["y"] != (y,):
        return False
    if cmatrix["z"] != (z,):
        return False
    if cmatrix["t"] != (t,):
        return False

    # Relaxed dimension ordering
    return (
        len(dims) == 4 and x in dims and y in dims and t in dims and z in dims
    )
