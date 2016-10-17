#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_trajectory_profile.py
'''

from compliance_checker.base import BaseCheck
from cc_plugin_ncei.ncei_base import TestCtx, NCEI1_1Check, NCEI2_0Check
from cc_plugin_ncei import util
from isodate import parse_duration


class NCEITrajectoryProfileOrthogonalBase(BaseCheck):
    _cc_spec = 'ncei-trajectory-profile-orthogonal'
    valid_feature_types = [
        'trajectory',
        'trajectory_id'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a trajectory profile orthogonal dataset

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are trajectory profile orthogonal feature types')

        message = '{} must be a valid trajectory profile orthogonal feature type. It must have dimensions of (trajectory, obs, z).'
        message += ' Also, x, y, and t must have dimensions (trajectory, obs). z must be a coordinate variable with dimensions (z).'

        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_trajectory_profile_orthogonal(dataset, variable)
            required_ctx.assert_true(
                is_valid,
                message.format(variable)
            )
        results.append(required_ctx.to_result())
        return results

    def check_trajectory_id(self, dataset):
        '''
        Checks that if a variable exists for the trajectory id it has the appropriate attributes

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        exists_ctx = TestCtx(BaseCheck.MEDIUM, 'Variable defining "trajectory_id" exists')
        trajectory_ids = dataset.get_variables_by_attributes(cf_role='trajectory_id')
        # No need to check
        exists_ctx.assert_true(trajectory_ids, 'variable defining cf_role="trajectory_id" exists')
        if not trajectory_ids:
            return exists_ctx.to_result()
        results.append(exists_ctx.to_result())
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(trajectory_ids[0].name))
        test_ctx.assert_true(
            getattr(trajectory_ids[0], 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(test_ctx.to_result())
        return results


class NCEITrajectoryProfileOrthogonal1_1(NCEI1_1Check, NCEITrajectoryProfileOrthogonalBase):
    register_checker = True
    _cc_spec_version = '1.1'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF trajectoryProfile Orthogonal '
        'template version 1.1 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/'
        'trajectoryProfileOrtho.cdl). The NCEI version 1.1 templates are based on “feature types”'
        ', as identified by Unidata and CF, and conform to ACDD version 1.0 and CF version 1.6. '
        'You can find more information about the version 1.1 templates at https://www.nodc.noaa.'
        'gov/data/formats/netcdf/v1.1/. This test is specifically for the trajectoryProfile '
        'feature type in an Orthogonal multidimensional array representation, which is typically '
        'used for a series of profile features located at points ordered along a trajectory and '
        'all data points have the exact same depth values.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/necdf/v1.1/trajectoryProfileIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TrajectoryProfile_Orthogonal_Template_v1.1"
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
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Trajectory Profile orthogonal dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Trajectory',
            'cdm_data_type attribute must be set to Trajectory'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'trajectoryProfile',
            'featureType attribute must be set to trajectoryProfile'
        )
        results.append(required_ctx.to_result())
        return results


class NCEITrajectoryProfileOrthogonal2_0(NCEI2_0Check, NCEITrajectoryProfileOrthogonalBase):
    register_checker = True
    _cc_spec_version = '2.0'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF trajectoryProfile Orthogonal '
        'template version 2.0 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/'
        'trajectoryProfileOrtho.cdl). The NCEI version 2.0 templates are based on “feature types”'
        ', as identified by Unidata and CF, and conform to ACDD version 1.3 and CF version 1.6. '
        'You can find more information about the version 2.0 templates at https://www.nodc.noaa.'
        'gov/data/formats/netcdf/v2.0/. This test is specifically for the trajectoryProfile '
        'feature type in an Orthogonal multidimensional array representation, which is typically '
        'used for a series of profile features located at points ordered along a trajectory and '
        'all data points have the exact same depth values.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/necdf/v2.0/trajectoryProfileIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.3.0'

    valid_templates = [
        "NCEI_NetCDF_TrajectoryProfile_Orthogonal_Template_v2.0"
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Trajectory Profile orthogonal dataset')
        required_ctx.assert_true(
            getattr(dataset, 'ncei_template_version', '').lower() == self.valid_templates[0].lower(),
            'ncei_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Trajectory',
            'cdm_data_type attribute must be set to Trajectory'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'trajectoryProfile',
            'featureType attribute must be set to trajectoryProfile'
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


class NCEITrajectoryProfileIncompleteBase(BaseCheck):
    _cc_spec = 'ncei-trajectory-profile-incomplete'
    valid_feature_types = [
        'trajectory',
        'trajectory_id'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a trajectory profile incomplete dataset

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are trajectory profile incomplete feature types')

        message = '{} must be a valid trajectory profile incomplete feature type. It and z must have dimensions of (trajectory, obs, nzMax).'
        message += ' Also, x, y, and t must have dimensions (trajectory, obs).'

        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_trajectory_profile_incomplete(dataset, variable)
            required_ctx.assert_true(
                is_valid,
                message.format(variable)
            )
        results.append(required_ctx.to_result())
        return results

    def check_trajectory_id(self, dataset):
        '''
        Checks that if a variable exists for the trajectory id it has the appropriate attributes

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        exists_ctx = TestCtx(BaseCheck.MEDIUM, 'Variable defining "trajectory_id" exists')
        trajectory_ids = dataset.get_variables_by_attributes(cf_role='trajectory_id')
        # No need to check
        exists_ctx.assert_true(trajectory_ids, 'variable defining cf_role="trajectory_id" exists')
        if not trajectory_ids:
            return exists_ctx.to_result()
        results.append(exists_ctx.to_result())
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(trajectory_ids[0].name))
        test_ctx.assert_true(
            getattr(trajectory_ids[0], 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        results.append(test_ctx.to_result())
        return results


class NCEITrajectoryProfileIncomplete1_1(NCEI1_1Check, NCEITrajectoryProfileIncompleteBase):
    register_checker = True
    _cc_spec_version = '1.1'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF trajectoryProfile '
        'Incomplete template version 1.1 (found at https://www.nodc.noaa.gov/data/formats/'
        'netcdf/v1.1/trajectoryProfileIncom.cdl). The NCEI version 1.1 templates are based '
        'on “feature types”, as identified by Unidata and CF, and conform to ACDD version 1.0'
        ' and CF version 1.6. You can find more information about the version 1.1 templates at '
        'https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/. This test is specifically for the '
        'trajectoryProfile feature type in an Incomplete multidimensional array representation, '
        'which is typically used for a series of profile features located at points ordered along '
        'a trajectory and all data points do not have the exact same number of elements.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/necdf/v1.1/trajectoryProfileIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TrajectoryProfile_Incomplete_Template_v1.1"
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Trajectory Profile incomplete dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Trajectory',
            'cdm_data_type attribute must be set to Trajectory'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'trajectoryProfile',
            'featureType attribute must be set to trajectoryProfile'
        )
        results.append(required_ctx.to_result())
        return results


class NCEITrajectoryProfileIncomplete2_0(NCEI2_0Check, NCEITrajectoryProfileIncompleteBase):
    register_checker = True
    _cc_spec_version = '2.0'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF trajectoryProfile '
        'Incomplete template version 2.0 (found at https://www.nodc.noaa.gov/data/formats/'
        'netcdf/v2.0/trajectoryProfileIncom.cdl). The NCEI version 2.0 templates are based '
        'on “feature types”, as identified by Unidata and CF, and conform to ACDD version 1.3'
        ' and CF version 1.6. You can find more information about the version 2.0 templates at '
        'https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/. This test is specifically for the '
        'trajectoryProfile feature type in an Incomplete multidimensional array representation, '
        'which is typically used for a series of profile features located at points ordered along '
        'a trajectory and all data points do not have the exact same number of elements.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/necdf/v2.0/trajectoryProfileIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.3.0'

    valid_templates = [
        "NCEI_NetCDF_TrajectoryProfile_Incomplete_Template_v2.0"
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Trajectory Profile incomplete dataset')
        required_ctx.assert_true(
            getattr(dataset, 'ncei_template_version', '').lower() == self.valid_templates[0].lower(),
            'ncei_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Trajectory',
            'cdm_data_type attribute must be set to Trajectory'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'trajectoryProfile',
            'featureType attribute must be set to trajectoryProfile'
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
