from cc_plugin_ncei.ncei_profile import NCEIProfileOrthogonal, NCEIProfileIncomplete
from cc_plugin_ncei.tests.resources import STATIC_FILES
from netCDF4 import Dataset
import unittest


class TestNCEIProfile(unittest.TestCase):
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
        self.orthcheck = NCEIProfileOrthogonal()
        self.inccheck = NCEIProfileIncomplete()
    

##########################################################################
# Orthogonal Time Series Test
##########################################################################
    def test_dimension_check_orthogonal(self):
        dataset = self.get_dataset(STATIC_FILES['profileOrthogonal'])
        result = self.orthcheck.check_dimensions(dataset)
        self.assertEquals(result.value, (2, 2))

    def test_required_attributes_orthogonal(self):
        dataset = self.get_dataset(STATIC_FILES['profileOrthogonal'])
        result = self.orthcheck.check_required_attributes(dataset)
        self.assertEquals(result.value, (4, 4))

    def test_science_orthogonal(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['profileOrthogonal'])
        result = self.orthcheck.check_science_orthogonal(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))

    def test_profile(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['profileOrthogonal'])
        result = self.orthcheck.check_profile_orthogonal(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))

##########################################################################
# Incomplete Time Series Test
##########################################################################
    def test_dimension_check_incomplete(self):
        dataset = self.get_dataset(STATIC_FILES['profileIncomplete'])
        result = self.inccheck.check_dimensions(dataset)
        self.assertEquals(result.value, (2, 2))

    def test_required_attributes(self):
        dataset = self.get_dataset(STATIC_FILES['profileIncomplete'])
        result = self.inccheck.check_required_attributes(dataset)
        self.assertEquals(result.value, (4, 4))

    def test_profile(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['profileIncomplete'])
        result = self.inccheck.check_profile(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
    
    def test_science_incomplete(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['profileIncomplete'])
        result = self.inccheck.check_science_incomplete(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
