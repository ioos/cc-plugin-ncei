#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
cc_plugin_ncei/tests/test_ncei_metadata.py
'''
from cc_plugin_ncei.ncei_timeseries import NCEIMetadataCheck
from cc_plugin_ncei.tests.resources import STATIC_FILES
from netCDF4 import Dataset
import unittest


class TestNCEIMetadata(unittest.TestCase):
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
        self.check = NCEIMetadataCheck()


    def test_required_attributes(self):
        '''
        Verifies the test checks the required attributes
        '''
        dataset = self.get_dataset(STATIC_FILES['station_timeseries'])
        result = self.check.check_required_attributes(dataset)

        self.assertEquals(result.value, (8, 8))

