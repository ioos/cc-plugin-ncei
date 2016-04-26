from cc_plugin_ncei.ncei_timeseriesprofile import NCEITimeSeriesProfileOrthogonal, NCEITimeSeriesProfileIncomplete,  NCEITimeSeriesProfileOrthTimeIncompleteDepth,  NCEITimeSeriesProfileIncompleteTimeOrthDepth

from cc_plugin_ncei.tests.resources import STATIC_FILES
from netCDF4 import Dataset
import unittest


class TestNCEITimeSeriesProfile(unittest.TestCase):
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
    
    def get_dataset(self, nc_dataset):
        '''
        Return a pairwise object for the dataset
        '''
        if isinstance(nc_dataset, basestring):
            nc_dataset = Dataset(nc_dataset, 'r')
            self.addCleanup(nc_dataset.close)
        return nc_dataset
    
    def setUp(self):
        self.orthcheck = NCEITimeSeriesProfileOrthogonal()
        self.inccheck = NCEITimeSeriesProfileIncomplete()
        self.orthtimecheckincdepth = NCEITimeSeriesProfileOrthTimeIncompleteDepth()
        self.inctimecheckorthdepth = NCEITimeSeriesProfileIncompleteTimeOrthDepth()
    

##########################################################################
# Orthogonal Time Series Profile Test
##########################################################################
    def test_dimension_check_orthogonal(self):
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileOrthogonal'])
        result = self.orthcheck.check_dimensions(dataset)
        print result
        self.assertEquals(result.value, (6, 6))

    def test_required_attributes_orthogonal(self):
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileOrthogonal'])
        result = self.orthcheck.check_required_attributes(dataset)
        print result
        self.assertEquals(result.value, (4, 4))

    def test_timeseriesprofile_orthogonal(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileOrthogonal'])
        result = self.orthcheck.check_timeseriesprofile(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))

##########################################################################
# Incomplete Time Series Profile Test
##########################################################################
    def test_dimension_check_incomplete(self):
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncomplete'])
        result = self.inccheck.check_dimensions(dataset)
        self.assertEquals(result.value, (4, 4))

    def test_required_attributes_incomplete(self):
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncomplete'])
        result = self.inccheck.check_required_attributes(dataset)
        self.assertEquals(result.value, (4, 4))

    def test_timeseriesprofile_incomplete(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncomplete'])
        result = self.inccheck.check_timeseries(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
    
    def test_science_incomplete(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncomplete'])
        result = self.inccheck.check_science_incomplete(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
    
    def test_z_incomplete(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncomplete'])
        result = self.inccheck.check_z(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))

##########################################################################
# Incomplete Time Orth Depth Time Series Profile Test
##########################################################################
    def test_dimension_check_incompletetime_orthdepth(self):
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncompleteTimeOrthDepth'])
        result = self.inctimecheckorthdepth.check_dimensions(dataset)
        self.assertEquals(result.value, (5, 5))

    def test_required_attributes_incompletetime_orthdepth(self):
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncompleteTimeOrthDepth'])
        result = self.inctimecheckorthdepth.check_required_attributes(dataset)
        self.assertEquals(result.value, (4, 4))

    def test_timeseries_incompletetime_orthdepth(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncompleteTimeOrthDepth'])
        result = self.inctimecheckorthdepth.check_timeseriesprofile(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
    
    def test_science_incompletetime_orthdepth(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncompleteTimeOrthDepth'])
        result = self.inctimecheckorthdepth.check_science_incompletetime_orthdepth(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
    
    def test_z_incompletetime_orthdepth(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileIncompleteTimeOrthDepth'])
        result = self.inctimecheckorthdepth.check_z(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))

##########################################################################
# Orth Time Incomplete Depth Time Series Profile Test
##########################################################################
    def test_dimension_check_orthtime_incompletedepth(self):
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileOrthTimeIncompleteDepth'])
        result = self.orthtimecheckincdepth.check_dimensions(dataset)
        self.assertEquals(result.value, (5, 5))

    def test_required_attributes_orthtime_incompletedepth(self):
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileOrthTimeIncompleteDepth'])
        result = self.orthtimecheckincdepth.check_required_attributes(dataset)
        self.assertEquals(result.value, (4, 4))

    def test_timeseries_orthtime_incompletedepth(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileOrthTimeIncompleteDepth'])
        result = self.orthtimecheckincdepth.check_timeseries(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
    
    def test_science_orthtime_incompletedepth(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileOrthTimeIncompleteDepth'])
        result = self.orthtimecheckincdepth.check_science_orthtime_incompletedepth(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
    
    def test_z_orthtime_incompletedepth(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['timeSeriesProfileOrthTimeIncompleteDepth'])
        result = self.orthtimecheckincdepth.check_z(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
