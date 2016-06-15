#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_timeseries.py
'''

from compliance_checker.base import Result, BaseCheck, score_group
from cc_plugin_ncei.ncei_base import NCEIBaseCheck, TestCtx
from cc_plugin_ncei import util


class NCEITimeSeriesOrthogonal(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-timeseries-orthogonal'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/timeSeriesOrthogonal.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeries_Orthogonal_Template_v1.1",
    ]

    valid_feature_types = [
        'timeSeries',
        'timeseries_id'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a time series orthogonal dataset
        '''
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are time-series orthogonal feature types')
        message = '{} must be a valid timeseries feature type. It must have dimensions of (timeSeries, time) or (time).'
        message += ' And x, y and z coordinates must have dimensions (timeSeries) or be dimensionless'
        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_timeseries(dataset, variable) or util.is_multi_timeseries_orthogonal(dataset, variable)
            required_ctx.assert_true(
                is_valid,
                message.format(variable)
            )
        return required_ctx.to_result()

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
            getattr(dataset, 'cdm_data_type', '') == 'Station',
            'cdm_data_type attribute must be set to Station'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'timeSeries',
            'featureType attribute must be set to timeSeries'
        )
        results.append(required_ctx.to_result())
        return results

    def check_timeseries_id(self, dataset):
        '''
        Checks that if a variable exists for the time series id it has the appropriate attributes
        '''
        timeseries_ids = dataset.get_variables_by_attributes(cf_role='timeseries_id')
        # No need to check
        if not timeseries_ids:
            return
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the timeSeries variable')
        timeseries_variable = timeseries_ids[0]
        test_ctx.assert_true(
            getattr(timeseries_variable, 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        return test_ctx.to_result()


class NCEITimeSeriesIncomplete(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-timeseries-incomplete'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeries_Incomplete_Template_v1.1"
    ]

    valid_feature_types = [
        'timeSeries',
        'timeseries_id'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a time series incomplete dataset
        '''
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are time-series incomplete feature types')
        message = '{} must be a valid timeseries feature type. It must have dimensions of (timeSeries, time).'
        message += ' And all coordinates must have dimensions of (timeSeries)'
        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_multi_timeseries_incomplete(dataset, variable)
            required_ctx.assert_true(
                is_valid,
                message.format(variable)
            )
        return required_ctx.to_result()

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Timeseries')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be "{}"'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Station',
            'cdm_data_type attribute must be set to Station'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'timeSeries',
            'featureType attribute must be set to timeSeries'
        )
        results.append(required_ctx.to_result())
        return results

    def check_timeseries_id(self, dataset):
        '''
        Checks that if a variable exists for the time series id it has the appropriate attributes
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required variable for time series identifier')
        recommended_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the timeSeries variable')
        # A variable with cf_role="timeseries_id" MUST exist for this to be a valid timeseries incomplete
        timeseries_ids = dataset.get_variables_by_attributes(cf_role='timeseries_id')
        required_ctx.assert_true(timeseries_ids, 'a unique variable must define attribute cf_role="timeseries_id"')
        results.append(required_ctx.to_result())
        if not timeseries_ids:
            return results

        timevar = util.get_time_variable(dataset)
        nc_timevar = dataset.variables[timevar]
        time_dimensions = nc_timevar.dimensions

        timeseries_variable = timeseries_ids[0]
        dims = timeseries_variable.dimensions
        required_ctx.assert_true(
            time_dimensions and time_dimensions[0] == dims[0],
            '{} must have a dimension and that dimension must be shared by the time variable'.format(timeseries_variable.name)
        )
        recommended_ctx.assert_true(
            getattr(timeseries_variable, 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(recommended_ctx.to_result())
        return results
