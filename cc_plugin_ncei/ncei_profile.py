#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_profile.py
'''

from compliance_checker.base import Result, BaseCheck
from cc_plugin_ncei.ncei_base import NCEIBaseCheck, TestCtx
from cc_plugin_ncei import util


class NCEIProfileOrthogonal(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-profile-orthogonal'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/profileOrthogonal.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Profile_Orthogonal_Template_v1.1",
    ]

    valid_feature_types = [
        'profile',
        'profile_id'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consistent with a profile-orthogonal dataset.
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are profile-orthogonal feature types')

        message = '{} must be a valid profile-orthogonal feature type. It must have dimensions of (profile, depth).'
        message += ' x and y should have dimensions of (profile), z should have dimension of (depth) and t should have dimension (profile)'
        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_profile_orthogonal(dataset, variable)
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
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Profile-orthogonal dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Station',
            'cdm_data_type attribute must be set to Station'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'profile',
            'featureType attribute must be set to profile'
        )
        results.append(required_ctx.to_result())
        return results

    def check_profile_id(self, dataset):
        '''
        Checks that if a variable exists for the profile id it has the appropriate attributes
        '''
        results = []
        exists_ctx = TestCtx(BaseCheck.MEDIUM, 'Variable defining "profile_id" exists')
        profile_ids = dataset.get_variables_by_attributes(cf_role='profile_id')
        # No need to check
        exists_ctx.assert_true(profile_ids, 'variable defining cf_role="profile_id" exists')
        if not profile_ids:
            return exists_ctx.to_result()
        results.append(exists_ctx.to_result())
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(profile_ids[0].name))
        test_ctx.assert_true(
            getattr(profile_ids[0], 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(test_ctx.to_result())
        return results


class NCEIProfileIncomplete(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-profile-incomplete'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/profileIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Profile_Incomplete_Template_v1.1"
    ]

    valid_feature_types = [
        'profile',
        'profile_id'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consistent with a profile-incomplete dataset.
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are profile-incomplete feature types')

        message = '{} must be a valid profile-incomplete feature type. It must have dimensions of (profile, depth).'
        message += ' x and y should have dimensions of (profile), z should have dimension of (profile, depth) and t should have dimension (profile)'
        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_profile_incomplete(dataset, variable)
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
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Profile-incomplete dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Station',
            'cdm_data_type attribute must be set to Station'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'profile',
            'featureType attribute must be set to profile'
        )
        results.append(required_ctx.to_result())
        return results

    def check_profile_id(self, dataset):
        '''
        Checks that if a variable exists for the profile id it has the appropriate attributes
        '''
        results = []
        exists_ctx = TestCtx(BaseCheck.MEDIUM, 'Variable defining "profile_id" exists')
        profile_ids = dataset.get_variables_by_attributes(cf_role='profile_id')
        # No need to check
        exists_ctx.assert_true(profile_ids, 'variable defining cf_role="profile_id" exists')
        if not profile_ids:
            return exists_ctx.to_result()
        results.append(exists_ctx.to_result())
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(profile_ids[0].name))
        test_ctx.assert_true(
            getattr(profile_ids[0], 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(test_ctx.to_result())
        return results
