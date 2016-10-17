#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_profile.py
'''

from compliance_checker.base import BaseCheck
from cc_plugin_ncei.ncei_base import TestCtx, NCEI1_1Check, NCEI2_0Check
from cc_plugin_ncei import util


class NCEIProfileOrthogonalBase(BaseCheck):
    _cc_spec = 'ncei-profile-orthogonal'
    valid_feature_types = [
        'profile',
        'profile_id'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consistent with a profile-orthogonal dataset.

        :param netCDF4.Dataset dataset: An open netCDF dataset
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

    def check_profile_id(self, dataset):
        '''
        Checks that if a variable exists for the profile id it has the appropriate attributes

        :param netCDF4.Dataset dataset: An open netCDF dataset
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


class NCEIProfileOrthogonal1_1(NCEI1_1Check, NCEIProfileOrthogonalBase):
    register_checker = True
    _cc_spec_version = '1.1'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF Profile Orthogonal template '
        'version 1.1 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/profileOrthogonal.cdl).'
        ' The NCEI version 1.1 templates are based on “feature types”, as identified by Unidata '
        'and CF, and conform to ACDD version 1.0 and CF version 1.6. You can find more information about '
        'the version 1.1 templates at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/. '
        'This test is specifically for the Profile feature type in an Orthogonal multidimensional array '
        'representation, which is typically used for an ordered set of data points along a vertical line '
        'at a fixed horizontal position and fixed time and all data points have the exact same depth values.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/profileOrthogonal.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Profile_Orthogonal_Template_v1.1",
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


class NCEIProfileOrthogonal2_0(NCEI2_0Check, NCEIProfileOrthogonalBase):
    register_checker = True
    _cc_spec_version = '2.0'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF Profile Orthogonal template '
        'version 2.0 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/profileOrthogonal.cdl).'
        ' The NCEI version 2.0 templates are based on “feature types”, as identified by Unidata '
        'and CF, and conform to ACDD version 1.3 and CF version 1.6. You can find more information about '
        'the version 2.0 templates at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/. '
        'This test is specifically for the Profile feature type in an Orthogonal multidimensional array '
        'representation, which is typically used for an ordered set of data points along a vertical line '
        'at a fixed horizontal position and fixed time and all data points have the exact same depth values.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/profileOrthogonal.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.3.0'

    valid_templates = [
        "NCEI_NetCDF_Profile_Orthogonal_Template_v2.0",
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Profile-orthogonal dataset')
        required_ctx.assert_true(
            getattr(dataset, 'ncei_template_version', '').lower() == self.valid_templates[0].lower(),
            'ncei_template_version attribute must be {}'.format(self.valid_templates[0])
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


class NCEIProfileIncomplete(BaseCheck):
    _cc_spec = 'ncei-profile-incomplete'
    valid_feature_types = [
        'profile',
        'profile_id'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consistent with a profile-incomplete dataset.

        :param netCDF4.Dataset dataset: An open netCDF dataset
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

    def check_profile_id(self, dataset):
        '''
        Checks that if a variable exists for the profile id it has the appropriate attributes

        :param netCDF4.Dataset dataset: An open netCDF dataset
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


class NCEIProfileIncomplete1_1(NCEI1_1Check, NCEIProfileIncomplete):
    register_checker = True
    _cc_spec_version = '1.1'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF Profile Incomplete template '
        'version 1.1 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/profileIncomplete.cdl).'
        ' The NCEI version 1.1 templates are based on “feature types”, as identified by Unidata '
        'and CF, and conform to ACDD version 1.0 and CF version 1.6. You can find more information '
        'about the version 1.1 templates at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/. '
        'This test is specifically for the Profile feature type in an Incomplete multidimensional '
        'array representation, which is typically used for an ordered set of data points along a '
        'vertical line at a fixed horizontal position and fixed time and all data points do not '
        'have the exact same depth values.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/profileIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Profile_Incomplete_Template_v1.1"
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


class NCEIProfileIncomplete2_0(NCEI2_0Check, NCEIProfileIncomplete):
    register_checker = True
    _cc_spec_version = '2.0'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF Profile Incomplete template '
        'version 2.0 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/profileIncomplete.cdl).'
        ' The NCEI version 2.0 templates are based on “feature types”, as identified by Unidata '
        'and CF, and conform to ACDD version 1.3 and CF version 1.6. You can find more information '
        'about the version 2.0 templates at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/. '
        'This test is specifically for the Profile feature type in an Incomplete multidimensional '
        'array representation, which is typically used for an ordered set of data points along a '
        'vertical line at a fixed horizontal position and fixed time and all data points do not '
        'have the exact same depth values.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/profileIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.3.0'

    valid_templates = [
        "NCEI_NetCDF_Profile_Incomplete_Template_v2.0"
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Profile-incomplete dataset')
        required_ctx.assert_true(
            getattr(dataset, 'ncei_template_version', '').lower() == self.valid_templates[0].lower(),
            'ncei_template_version attribute must be {}'.format(self.valid_templates[0])
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
