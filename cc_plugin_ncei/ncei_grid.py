#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_grid.py
'''

from compliance_checker.base import BaseCheck
from cc_plugin_ncei.ncei_base import NCEIBaseCheck, TestCtx
from cc_plugin_ncei import util

class NCEIGrid(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-grid'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/grid.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Grid_Template_v1.1"
    ]

    valid_feature_types = [
        'grid'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a regular gridded dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are regular gridded feature types')

        message = '{} must be a valid regular gridded feature type. It must have dimensions (t, z, y, x)'
        message += ' and each dimension must be a coordinate variable with a dimension with the same name'
        message += ' as the variable. z is optional.'

        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_2d_regular_grid(dataset, variable)
            is_valid = is_valid or util.is_3d_regular_grid(dataset, variable)
            required_ctx.assert_true(
                is_valid,
                message.format(variable)
            )
        results.append(required_ctx.to_result())
        return results

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Trajectory Profile orthogonal dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Grid',
            'cdm_data_type attribute must be set to Grid'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'grid',
            'featureType attribute must be set to grid'
        )
        results.append(required_ctx.to_result())
        return results

    def check_bounds_variables(self, dataset):
        recommended_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended variables to describe grid boundaries')

        bounds_map = {
            'lat_bounds': {
                'units': 'degrees_north',
                'comment': 'latitude values at the north and south bounds of each pixel.'
            },
            'lon_bounds': {
                'units': 'degrees_east',
                'comment': 'longitude values at the west and east bounds of each pixel.'
            },
            'z_bounds': {
                'comment': 'z bounds for each z value',
            },
            'time_bounds': {
                'comment': 'time bounds for each time value'
            }
        }

        bounds_variables = [v.bounds for v in dataset.get_variables_by_attributes(bounds=lambda x: x is not None)]

        for variable in bounds_variables:
            ncvar = dataset.variables.get(variable, {})
            recommended_ctx.assert_true(ncvar != {}, 'a variable {} should exist as indicated by a bounds attribute'.format(variable))
            if ncvar == {}:
                continue

            units = getattr(ncvar, 'units', '')
            if variable in bounds_map and 'units' in bounds_map[variable]:
                recommended_ctx.assert_true(
                    units == bounds_map[variable]['units'],
                    'variable {} should have units {}'.format(variable, bounds_map[variable]['units'])
                )
            else:
                recommended_ctx.assert_true(
                    units != '',
                    'variable {} should have a units attribute that is not empty'.format(variable)
                )

            comment = getattr(ncvar, 'comment', '')
            recommended_ctx.assert_true(
                comment != '',
                'variable {} should have a comment and not be empty'
            )

        return recommended_ctx.to_result()

