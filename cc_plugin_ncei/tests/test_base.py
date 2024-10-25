"""TestNCEIBase.

Tests the base functionality of the checker that should remain the same
across all of the discrete sampling geometries.
"""

import numpy as np
import pytest
from compliance_checker.base import BaseCheck
from compliance_checker.tests.helpers import MockNetCDF

from cc_plugin_ncei import ncei_base


@pytest.fixture
def nc():
    """Create a simple timeseries like NetCDF object."""
    nc = MockNetCDF()
    nc.createDimension("time", None)
    tvar = nc.createVariable("time", "f8", ("time",))
    tvar.axis = "T"
    tvar.standard_name = "time"
    tvar.units = "seconds since 1970-01-01"
    tvar.calendar = "gregorian"
    tvar[:] = np.array([1, 2], dtype="f8")
    pres = nc.createVariable("pressure", "f8", ("time",))
    pres.standard_name = "air_pressure"
    pres.units = "Pa"
    pres[:] = np.array([101.325, 101.425], dtype=np.float64)
    yield nc
    nc.close()


def test_valid_range(nc):
    """Check for defined valid range with same dtype as source variable with
    two elements in min to max order.
    """
    base_check = ncei_base.BaseNCEICheck()

    var = nc.variables["pressure"]
    tc1 = ncei_base.TestCtx(BaseCheck.MEDIUM, "Test context")
    var.valid_range = np.array([101.325, 101.425], dtype=np.float64)
    base_check._check_min_max_range(var, tc1)
    assert len(tc1.messages) == 0
    # list-like types get automatically converted to numpy arrays if they
    # aren't a base numpy type
    var.valid_range = [100, 200, 300]
    tc2 = ncei_base.TestCtx(BaseCheck.MEDIUM, "Test context")
    base_check._check_min_max_range(var, tc2)
    assert (
        "valid_range must be a two element vector of min followed by max with the same data type as pressure"
        in tc2.messages
    )


def test_valid_min_max(nc):
    """When valid_range is not defined, check for the presence of both attributes
    valid_min and valid_max which are the same data type as the data in the variable.
    """
    base_check = ncei_base.BaseNCEICheck()

    var = nc.variables["pressure"]
    var.valid_min, var.valid_max = 101.325, 101.425
    tc1 = ncei_base.TestCtx(BaseCheck.MEDIUM, "Test context")
    base_check._check_min_max_range(var, tc1)
    var.valid_min, var.valid_max = "101", "102"
    tc2 = ncei_base.TestCtx(BaseCheck.MEDIUM, "Test context")
    base_check._check_min_max_range(var, tc2)
    expected = [
        f"{v} attribute should exist, have the same type as pressure, and not be empty or valid_range should be defined"
        for v in ["valid_min", "valid_max"]
    ]
    assert expected == tc2.messages
