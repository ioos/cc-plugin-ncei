from cc_plugin_ncei.ncei_trajectory import NCEITrajectory
from cc_plugin_ncei.tests.resources import STATIC_FILES
from netCDF4 import Dataset
import unittest


class TestNCEItrajectory(unittest.TestCase):
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
        self.check = NCEITrajectory()
    

##########################################################################
# Trajectory Test
##########################################################################
    def test_dimension_check(self):
        dataset = self.get_dataset(STATIC_FILES['trajectory'])
        result = self.check.check_dimensions(dataset)
        self.assertEquals(result.value, (3, 3))

    def test_required_attributes(self):
        dataset = self.get_dataset(STATIC_FILES['trajectory'])
        result = self.check.check_required_attributes(dataset)
        print result
        self.assertEquals(result.value, (4, 4))

    def test_trajectory(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['trajectory'])
        result = self.check.check_trajectory(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))

    def test_science_incomplete(self):
        test_results = []
        dataset = self.get_dataset(STATIC_FILES['trajectory'])
        result = self.check.check_science_incomplete(dataset)
        for test_result in result:
            test_results.append(test_result)
        self.assertTrue(all(test_results))
