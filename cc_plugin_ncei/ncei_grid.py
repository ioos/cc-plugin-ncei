#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_grid.py
'''

from compliance_checker.base import BaseCheck
from cc_plugin_ncei.ncei_base import TestCtx, NCEI1_1Check, NCEI2_0Check
from cc_plugin_ncei import util
from isodate import parse_duration


class NCEIGridBase(BaseCheck):
    _cc_spec = 'ncei-grid'
    valid_feature_types = [
        'grid'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consistent with a regular gridded dataset

        :param netCDF4.Dataset dataset: An open netCDF dataset
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

    def check_bounds_variables(self, dataset):
        '''
        Checks the grid boundary variables.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
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


class NCEIGrid1_1(NCEI1_1Check, NCEIGridBase):
    register_checker = True
    _cc_spec_version = '1.1'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF grid template version 1.1 '
        '(found at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/grid.cdl). The NCEI '
        'version 1.1 templates are based on “feature types”, as identified by Unidata and CF, '
        'and conform to ACDD version 1.0 and CF version 1.6. You can find more information about '
        'the version 1.1 templates at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/. This '
        'test is specifically for the Grid feature type, which is typically used for data points '
        'represented or projected on a regular or irregular grid.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/grid.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Grid_Template_v1.1"
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Grid')
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


class NCEIGrid2_0(NCEI2_0Check, NCEIGridBase):
    register_checker = True
    _cc_spec_version = '2.0'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF grid template '
        'version 2.0 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/grid.cdl). The NCEI '
        'version 2.0 templates are based on “feature types”, as identified by Unidata and CF, and '
        'conform to ACDD version 1.3 and CF version 1.6. You can find more information about the '
        'version 2.0 templates at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/. This test is '
        'specifically for the Grid feature type, which is typically used for data points represented '
        'or projected on a regular or irregular grid.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/grid.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.3.0'

    valid_templates = [
        "NCEI_NetCDF_Grid_Template_v2.0"
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Grid')
        required_ctx.assert_true(
            getattr(dataset, 'ncei_template_version', '').lower() == self.valid_templates[0].lower(),
            'ncei_template_version attribute must be {}'.format(self.valid_templates[0])
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

    def check_recommended_attributes(self, dataset):
        '''
        Feature type specific check of global recommended and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        recommended_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended global attributes')
        # Check time_coverage_duration and resolution
        for attr in ['time_coverage_duration', 'time_coverage_resolution']:
            attr_value = getattr(dataset, attr, '')
            try:
                parse_duration(attr_value)
                recommended_ctx.assert_true(True, '')  # Score it True!
            except Exception:
                recommended_ctx.assert_true(False, '{} should exist and be ISO-8601 format (example: PT1M30S), currently: {}'.format(attr, attr_value))
        results.append(recommended_ctx.to_result())
        return results
