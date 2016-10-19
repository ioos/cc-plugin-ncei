#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_timeseries.py
'''

from compliance_checker.base import BaseCheck
from cc_plugin_ncei.ncei_base import TestCtx, NCEI1_1Check, NCEI2_0Check
from cc_plugin_ncei import util
from isodate import parse_duration


class NCEITimeSeriesOrthogonalBase(BaseCheck):
    _cc_spec = 'ncei-timeseries-orthogonal'
    valid_feature_types = [
        'timeSeries',
        'timeseries_id'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a time series orthogonal dataset

        :param netCDF4.Dataset dataset: An open netCDF dataset
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

    def check_timeseries_id(self, dataset):
        '''
        Checks that if a variable exists for the time series id it has the appropriate attributes

        :param netCDF4.Dataset dataset: An open netCDF dataset
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


class NCEITimeSeriesOrthogonal1_1(NCEI1_1Check, NCEITimeSeriesOrthogonalBase):
    register_checker = True
    _cc_spec_version = '1.1'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF timeSeries Orthogonal '
        'template version 1.1 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/'
        'timeSeriesOrthogonal.cdl). The NCEI version 1.1 templates are based on “feature '
        'types”, as identified by Unidata and CF, and conform to ACDD version 1.0 and CF '
        'version 1.6. You can find more information about the version 1.1 templates at '
        'https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/. This test is specifically '
        'for the timeSeries feature type in an Orthogonal multidimensional array representation. '
        'This representation is typically used for a series of data points at the same spatial '
        'location with monotonically increaing times and all instruments measure at the '
        'exact same time.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/timeSeriesOrthogonal.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeries_Orthogonal_Template_v1.1",
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
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


class NCEITimeSeriesOrthogonal2_0(NCEI2_0Check, NCEITimeSeriesOrthogonalBase):
    register_checker = True
    _cc_spec_version = '2.0'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF timeSeries Orthogonal '
        'template version 2.0 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/'
        'timeSeriesOrthogonal.cdl). The NCEI version 2.0 templates are based on “feature '
        'types”, as identified by Unidata and CF, and conform to ACDD version 1.3 and CF '
        'version 1.6. You can find more information about the version 2.0 templates at '
        'https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/. This test is specifically '
        'for the timeSeries feature type in an Orthogonal multidimensional array representation. '
        'This representation is typically used for a series of data points at the same spatial '
        'location with monotonically increaing times and all instruments measure at the '
        'exact same time.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesOrthogonal.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.3.0'

    valid_templates = [
        "NCEI_NetCDF_TimeSeries_Orthogonal_Template_v2.0",
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Timeseries')
        required_ctx.assert_true(
            getattr(dataset, 'ncei_template_version', '').lower() == self.valid_templates[0].lower(),
            'ncei_template_version attribute must be {}'.format(self.valid_templates[0])
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

    def check_recommended_attributes(self, dataset):
        '''
        Feature type specific check of global recommended attributes.

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


class NCEITimeSeriesIncompleteBase(BaseCheck):
    _cc_spec = 'ncei-timeseries-incomplete'
    valid_feature_types = [
        'timeSeries',
        'timeseries_id'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a time series incomplete dataset

        :param netCDF4.Dataset dataset: An open netCDF dataset
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

    def check_timeseries_id(self, dataset):
        '''
        Checks that if a variable exists for the time series id it has the appropriate attributes

        :param netCDF4.Dataset dataset: An open netCDF dataset
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


class NCEITimeSeriesIncomplete1_1(NCEI1_1Check, NCEITimeSeriesIncompleteBase):
    register_checker = True
    _cc_spec_version = '1.1'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF timeSeries Incomplete '
        'template version 1.1 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1'
        '/timeSeriesOrthogonal.cdl). The NCEI version 1.1 templates are based on “feature types”,'
        ' as identified by Unidata and CF, and conform to ACDD version 1.0 and CF version 1.6. '
        'You can find more information about the version 1.1 templates at '
        'https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/. This test is specifically for the '
        'timeSeries feature type in an Incomplete multidimensional array representation. This '
        'representation is typically used for a series of data points at the same spatial '
        'location with monotonically increaing times and all instruments measure at different '
        'time intevals.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/timeSeriesIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeries_Incomplete_Template_v1.1"
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
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


class NCEITimeSeriesIncomplete2_0(NCEI2_0Check, NCEITimeSeriesIncompleteBase):
    register_checker = True
    _cc_spec_version = '2.0'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF timeSeries Incomplete '
        'template version 2.0 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0'
        '/timeSeriesOrthogonal.cdl). The NCEI version 2.0 templates are based on “feature types”,'
        ' as identified by Unidata and CF, and conform to ACDD version 1.0 and CF version 1.6. '
        'You can find more information about the version 2.0 templates at '
        'https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/. This test is specifically for the '
        'timeSeries feature type in an Incomplete multidimensional array representation. This '
        'representation is typically used for a series of data points at the same spatial '
        'location with monotonically increaing times and all instruments measure at different '
        'time intevals.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.3.0'

    valid_templates = [
        "NCEI_NetCDF_TimeSeries_Incomplete_Template_v2.0"
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Timeseries')
        required_ctx.assert_true(
            getattr(dataset, 'ncei_template_version', '').lower() == self.valid_templates[0].lower(),
            'ncei_template_version attribute must be "{}"'.format(self.valid_templates[0])
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

    def check_recommended_attributes(self, dataset):
        '''
        Feature type specific check of global recommended attributes.

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
