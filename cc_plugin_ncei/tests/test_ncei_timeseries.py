from compliance_checker.ncei_timeseries import GliderCheck
from pkg_resources import resource_filename
from netCDF4 import Dataset
from compliance_checker.base import DSPair
from wicken.netcdf_dogma import NetCDFDogma
import unittest

static_files = {
}

class TestNCEITimeSeries(unittest.TestCase):
    # @see
    # http://www.saltycrane.com/blog/2012/07/how-prevent-nose-unittest-using-docstring-when-verbosity-2/
    def shortDescription(self):
        return None

    # override __str__ and __repr__ behavior to show a copy-pastable nosetest name for ion tests
    #  ion.module:TestClassName.test_function_name
    def __repr__(self):
        name = self.id()
        name = name.split('.')
        if name[0] not in ["ion", "pyon"]:
            return "%s (%s)" % (name[-1], '.'.join(name[:-1]))
        else:
            return "%s ( %s )" % (name[-1], '.'.join(name[:-2]) + ":" + '.'.join(name[-2:]))
    __str__ = __repr__
    
    def get_pair(self, nc_dataset):
        '''
        Return a pairwise object for the dataset
        '''
        print nc_dataset
        if isinstance(nc_dataset, basestring):
            nc_dataset = Dataset(nc_dataset, 'r')
            self.addCleanup(nc_dataset.close)
        dogma = NetCDFDogma('nc', self.check.beliefs(), nc_dataset)
        pair = DSPair(nc_dataset, dogma)
        return pair
    
    def setUp(self):
        self.check = GliderCheck()
    
