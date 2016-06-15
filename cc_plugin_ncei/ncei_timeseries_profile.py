#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_timeseries_profile.py
'''

from compliance_checker.base import BaseCheck
from cc_plugin_ncei.ncei_base import NCEIBaseCheck, TestCtx
from cc_plugin_ncei import util


class NCEITimeSeriesProfileOrthogonal(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-timeseries-profile-orthogonal'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/timeSeriesOrthogonal.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeriesProfile_Orthogonal_Template_v1.1",
    ]

    valid_feature_types = [
        'timeseries',
        'timeseries_id',
        'timeSeriesProfile'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consistent with a timeseries-profile-orthogonal dataset.
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are timeseries-profile-orthogonal feature types')

        message = '{} must be a valid profile-orthogonal feature type. It must have dimensions of (station, time, z).'
        message += ' If it\'s a single station, it must have dimensions (time, z). x and y dimensions must be scalar or have'
        message += ' dimensions (station). time must be a coordinate variable with dimension (time) and z must be a'
        message += ' coordinate variabel with dimension (z).'

        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_timeseries_profile_single_station(dataset, variable)
            is_valid = is_valid or util.is_timeseries_profile_multi_station(dataset, variable)
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
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Timeseries Profile orthogonal dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Station',
            'cdm_data_type attribute must be set to Station'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'timeSeriesProfile',
            'featureType attribute must be set to timeSeriesProfile'
        )
        results.append(required_ctx.to_result())
        return results

    def check_timeseries_id(self, dataset):
        '''
        Checks that if a variable exists for the timeseries id it has the appropriate attributes
        '''
        results = []
        exists_ctx = TestCtx(BaseCheck.MEDIUM, 'Variable defining "timeseries_id" exists')
        timeseries_ids = dataset.get_variables_by_attributes(cf_role='timeseries_id')
        # No need to check
        exists_ctx.assert_true(timeseries_ids, 'variable defining cf_role="timseries_id" exists')
        if not timeseries_ids:
            return exists_ctx.to_result()
        results.append(exists_ctx.to_result())
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(timeseries_ids[0].name))
        test_ctx.assert_true(
            getattr(timeseries_ids[0], 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(test_ctx.to_result())
        return results


class NCEITimeSeriesProfileOrthTimeIncompleteDepth(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-timeseries-profile-orthtime-incompletedepth'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeriesProfile_IncompleteVertical_OrthogonalTemporal_Template_v1.1"
    ]

    valid_feature_types = [
        'timeSeries',
        'timeseries_id',
        'timeSeriesProfile',
        'timeseriesprofile_id'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consistent with a timeseries-profile-orthogonal dataset.
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are timeseries-profile-ortho-time-incomplete-depth feature types')

        message = '{} must be a valid timeseries-profile-ortho-time-incomplete-depth feature type.'
        message += ' If it\'s multiple stations, it must have dimensions (station, time, z).'
        message += ' If it\'s a single station, it must have dimensions (time, z). x and y dimensions must be scalar or have'
        message += ' dimensions (station). time must be a coordinate variable with dimension (time) and z must'
        message += ' have dimensions (time, z) or (station, time, z) if it\'s a multi-station dataset.'

        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_timeseries_profile_single_ortho_time(dataset, variable)
            is_valid = is_valid or util.is_timeseries_profile_multi_ortho_time(dataset, variable)
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
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Timeseries Profile orthogonal dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Station',
            'cdm_data_type attribute must be set to Station'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'timeSeriesProfile',
            'featureType attribute must be set to timeSeriesProfile'
        )
        results.append(required_ctx.to_result())
        return results

    def check_timeseries_id(self, dataset):
        '''
        Checks that if a variable exists for the timeseries id it has the appropriate attributes
        '''
        results = []
        exists_ctx = TestCtx(BaseCheck.MEDIUM, 'Variable defining "timeseries_id" exists')
        timeseries_ids = dataset.get_variables_by_attributes(cf_role='timeseries_id')
        # No need to check
        exists_ctx.assert_true(timeseries_ids, 'variable defining cf_role="timseries_id" exists')
        if not timeseries_ids:
            return exists_ctx.to_result()
        results.append(exists_ctx.to_result())
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(timeseries_ids[0].name))
        test_ctx.assert_true(
            getattr(timeseries_ids[0], 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(test_ctx.to_result())
        return results


class NCEITimeSeriesProfileIncomplete(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-timeseries-profile-incomplete'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeriesProfile_Incomplete_Template_v1.1"
    ]

    valid_feature_types = [
        'timeSeries',
        'timeseries_id',
        'timeSeriesProfile',
        'timeseriesprofile_id'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consistent with a timeseries-profile-incomplete dataset.
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are timeseries-profile-incomplete feature types')

        message = '{} must be a valid timeseries-profile-incomplete feature type.'
        message += ' it must have dimensions (station, nTimeMax, zMax). x and y must have dimensions (station).'
        message += ' time must have dimensions (station, nTimeMax). And z must have dimensions (station, nTimeMax, zMax).'

        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_timeseries_profile_incomplete(dataset, variable)
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
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Timeseries Profile orthogonal dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Station',
            'cdm_data_type attribute must be set to Station'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'timeSeriesProfile',
            'featureType attribute must be set to timeSeriesProfile'
        )
        results.append(required_ctx.to_result())
        return results

    def check_timeseries_id(self, dataset):
        '''
        Checks that if a variable exists for the timeseries id it has the appropriate attributes
        '''
        results = []
        exists_ctx = TestCtx(BaseCheck.MEDIUM, 'Variable defining "timeseries_id" exists')
        timeseries_ids = dataset.get_variables_by_attributes(cf_role='timeseries_id')
        # No need to check
        exists_ctx.assert_true(timeseries_ids, 'variable defining cf_role="timseries_id" exists')
        if not timeseries_ids:
            return exists_ctx.to_result()
        results.append(exists_ctx.to_result())
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(timeseries_ids[0].name))
        test_ctx.assert_true(
            getattr(timeseries_ids[0], 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(test_ctx.to_result())
        return results


class NCEITimeSeriesProfileIncompleteTimeOrthDepth(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-timeseries-profile-incompletetime-orthdepth'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeriesProfile_OrthogonalVertical_IncompleteTemporal_Template_v1.1"
    ]

    valid_feature_types = [
        'timeSeries',
        'timeseries_id',
        'timeSeriesProfile',
        'timeseriesprofile_id'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consistent with a timeseries-profile-orthogonal dataset.
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are timeseries-profile-ortho-depth-incomplete-time feature types')

        message = '{} must be a valid timeseries-profile-ortho-depth-incomplete-time feature type.'
        message += ' it must have dimensions (station, time, z). x and y must have dimensions (station).'
        message += ' time must have dimensions (station, time). And z must be a coordinate variable with'
        message += ' dimension (z).'

        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_timeseries_profile_ortho_depth(dataset, variable)
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
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Timeseries Profile orthogonal dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '') == self.valid_templates[0],
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Station',
            'cdm_data_type attribute must be set to Station'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'timeSeriesProfile',
            'featureType attribute must be set to timeSeriesProfile'
        )
        results.append(required_ctx.to_result())
        return results

    def check_timeseries_id(self, dataset):
        '''
        Checks that if a variable exists for the timeseries id it has the appropriate attributes
        '''
        results = []
        exists_ctx = TestCtx(BaseCheck.MEDIUM, 'Variable defining "timeseries_id" exists')
        timeseries_ids = dataset.get_variables_by_attributes(cf_role='timeseries_id')
        # No need to check
        exists_ctx.assert_true(timeseries_ids, 'variable defining cf_role="timseries_id" exists')
        if not timeseries_ids:
            return exists_ctx.to_result()
        results.append(exists_ctx.to_result())
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(timeseries_ids[0].name))
        test_ctx.assert_true(
            getattr(timeseries_ids[0], 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(test_ctx.to_result())
        return results
