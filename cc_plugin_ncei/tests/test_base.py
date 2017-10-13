from cc_plugin_ncei.tests.ncei_test_case import NCEITestCase
from cc_plugin_ncei import ncei_base
from compliance_checker.base import BaseCheck
from cc_plugin_ncei.tests.helpers import MockNetCDF
from netCDF4 import Dataset
import numpy as np

class TestNCEIBase(NCEITestCase):
    """
    Tests the base functionality of the checker that should remain the same
    across all of the discrete sampling geometries
    """


    def setUp(self):
        """Create a simple timeseries like NetCDF object."""
        self.ds = MockNetCDF()
        self.ds.createDimension('time', None)
        tvar = self.ds.createVariable('time', 'f8', ('time',))
        tvar.axis = 'T'
        tvar.standard_name = 'time'
        tvar.units = 'seconds since 1970-01-01'
        tvar.calendar = 'gregorian'
        tvar[:] = np.array([1,2], dtype='f8')
        pres = self.ds.createVariable('pressure', 'f8', ('time',))
        pres.standard_name = 'air_pressure'
        pres.units = 'Pa'
        pres[:] = np.array([101.325, 101.425], dtype=np.float64)
        self.base_check = ncei_base.BaseNCEICheck()

    def tearDown(self):
        """
        Ensure the NetCDF object closes after each test or if an exception is
        raised.
        """
        self.ds.close()

    def test_valid_range(self):
        """
        Check for defined valid range with same dtype as source variable with
        two elements in min to max order.
        """
        var = self.ds.variables['pressure']
        tc1 = ncei_base.TestCtx(BaseCheck.MEDIUM, 'Test context')
        var.valid_range = np.array([101.325, 101.425], dtype=np.float64)
        self.base_check._check_min_max_range(var, tc1)
        self.assertEqual(len(tc1.messages), 0)
        # list-like types get automatically converted to numpy arrays if they
        # aren't a base numpy type
        var.valid_range = [100, 200, 300]
        tc2 = ncei_base.TestCtx(BaseCheck.MEDIUM, 'Test context')
        self.base_check._check_min_max_range(var, tc2)
        self.assertTrue("valid_range must be a two element vector of min followed by max with the same data type as pressure" in tc2.messages)

    def test_valid_min_max(self):
        """
        When valid_range is not defined, check for the presence of both
        attributes valid_min and valid_max which are the same data type as the
        data in the variable.
        """
        var = self.ds.variables['pressure']
        var.valid_min, var.valid_max = 101.325, 101.425
        tc1 = ncei_base.TestCtx(BaseCheck.MEDIUM, 'Test context')
        self.base_check._check_min_max_range(var, tc1)
        var.valid_min, var.valid_max = '101', '102'
        tc2 = ncei_base.TestCtx(BaseCheck.MEDIUM, 'Test context')
        self.base_check._check_min_max_range(var, tc2)
        expected = ['{} attribute should exist, have the same type as pressure, and not be empty or valid_range should be defined'.format(v)
                    for v in ['valid_min', 'valid_max']]
        self.assertEqual(expected, tc2.messages)
