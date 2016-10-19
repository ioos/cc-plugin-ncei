#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_point.py
'''

from compliance_checker.base import BaseCheck
from cc_plugin_ncei.ncei_base import TestCtx, NCEI1_1Check, NCEI2_0Check
from cc_plugin_ncei import util


class NCEIPointBase(BaseCheck):
    _cc_spec = 'ncei-point'
    valid_feature_types = [
        'station',
        'point'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a point dataset
        '''
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are point feature types')
        t = util.get_time_variable(dataset)

        # Exit prematurely
        if not t:
            required_ctx.assert_true(False, 'A dimension representing time is required for point feature types')
            return required_ctx.to_result()
        t_dims = dataset.variables[t].dimensions
        o = None or (t_dims and t_dims[0])

        message = '{} must be a valid timeseries feature type. It must have dimensions of ({}), and all coordinates must have dimensions of ({})'
        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_point(dataset, variable)
            required_ctx.assert_true(
                is_valid,
                message.format(variable, o, o)
            )
        return required_ctx.to_result()


class NCEIPoint1_1(NCEI1_1Check, NCEIPointBase):
    register_checker = True
    _cc_spec_version = '1.1'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF Point template version 1.1 '
        '(found at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/point.cdl). The NCEI '
        'version 1.1 templates are based on “feature types”, as identified by Unidata and CF, '
        'and conform to ACDD version 1.0 and CF version 1.6. You can find more information about '
        'the version 1.1 templates at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/. This '
        'test is specifically for the Point feature type which is typically used for a single '
        'data point with one or more recorded observations that have no temporal or spatial '
        'relationship (where each observation equals one point in time and space).')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/point.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Point_Template_v1.1"
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Timeseries')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Point',
            'cdm_data_type attribute must be set to Point'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'point',
            'featureType attribute must be set to point'
        )
        results.append(required_ctx.to_result())
        return results


class NCEIPoint2_0(NCEI2_0Check, NCEIPointBase):
    register_checker = True
    _cc_spec_version = '2.0'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF Point template'
        'version 2.0 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/point.cdl). The NCEI '
        'version 2.0 templates are based on “feature types”, as identified by Unidata and CF, and '
        'conform to ACDD version 1.3 and CF version 1.6. You can find more information about the '
        'version 2.0 templates at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/. This test is '
        'specifically for the Point feature type which is typically used for a single data point with '
        'one or more recorded observations that have no temporal or spatial relationship (where each '
        'observation equals one point in time and space).')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/point.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.3.0'

    valid_templates = [
        "NCEI_NetCDF_Point_Template_v2.0"
    ]

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Timeseries')
        required_ctx.assert_true(
            getattr(dataset, 'ncei_template_version', '').lower() == self.valid_templates[0].lower(),
            'ncei_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Point',
            'cdm_data_type attribute must be set to Point'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'point',
            'featureType attribute must be set to point'
        )
        results.append(required_ctx.to_result())
        return results
