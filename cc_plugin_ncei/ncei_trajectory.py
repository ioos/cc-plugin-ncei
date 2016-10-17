#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_trajectory.py
'''

from compliance_checker.base import BaseCheck
from cc_plugin_ncei.ncei_base import TestCtx, NCEI1_1Check, NCEI2_0Check
from cc_plugin_ncei import util
from isodate import parse_duration


class NCEITrajectoryBase(BaseCheck):
    _cc_spec = 'ncei-trajectory'
    valid_feature_types = [
        'trajectory',
        'trajectory_id'
    ]

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a trajectory dataset

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are trajectory feature types')

        message = ("{} must be a valid trajectory feature type. It must have dimensions of (trajectoryID, time)."
                   " And all coordinates must have dimensions (trajectoryID, time)")
        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_cf_trajectory(dataset, variable)
            is_valid = is_valid or util.is_single_trajectory(dataset, variable)
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


class NCEITrajectory1_1(NCEI1_1Check, NCEITrajectoryBase):
    register_checker = True
    _cc_spec_version = '1.1'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF trajectory Incomplete '
        'template version 1.1 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v1.1/'
        'trajectoryIncomplete.cdl). The NCEI version 1.1 templates are based on “feature types”, '
        'as identified by Unidata and CF, and conform to ACDD version 1.0 and CF version 1.6. You '
        'can find more information about the version 1.1 templates at https://www.nodc.noaa.gov/'
        'data/formats/netcdf/v1.1/. This test is specifically for the trajectory feature type '
        'in an Incomplete multidimensional array representation. This representation is typically '
        'used for a series of data points along a path through space with monotonically '
        'increasing times.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/trajectoryIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Trajectory_Template_v1.1"
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
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Trajectory dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '').lower() == self.valid_templates[0].lower(),
            'nodc_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Trajectory',
            'cdm_data_type attribute must be set to Trajectory'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'trajectory',
            'featureType attribute must be set to trajectory'
        )
        results.append(required_ctx.to_result())
        return results


class NCEITrajectory2_0(NCEI2_0Check, NCEITrajectoryBase):
    register_checker = True
    _cc_spec_version = '2.0'
    _cc_description = (
        'This test checks the selected file against the NCEI netCDF trajectory Incomplete '
        'template version 2.0 (found at https://www.nodc.noaa.gov/data/formats/netcdf/v2.0/'
        'trajectoryIncomplete.cdl). The NCEI version 2.0 templates are based on “feature types”, '
        'as identified by Unidata and CF, and conform to ACDD version 1.3 and CF version 1.6. You '
        'can find more information about the version 2.0 templates at https://www.nodc.noaa.gov/'
        'data/formats/netcdf/v2.0/. This test is specifically for the trajectory feature type '
        'in an Incomplete multidimensional array representation. This representation is typically '
        'used for a series of data points along a path through space with monotonically '
        'increasing times.')
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/trajectoryIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.3.0'

    valid_templates = [
        "NCEI_NetCDF_Trajectory_Template_v2.0"
    ]

    def check_required_attributes(self, dataset):
        '''
        Feature type specific check of global required and highly recommended attributes.

        :param netCDF4.Dataset dataset: An open netCDF dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Trajectory dataset')
        required_ctx.assert_true(
            getattr(dataset, 'ncei_template_version', '').lower() == self.valid_templates[0].lower(),
            'ncei_template_version attribute must be {}'.format(self.valid_templates[0])
        )
        required_ctx.assert_true(
            getattr(dataset, 'cdm_data_type', '') == 'Trajectory',
            'cdm_data_type attribute must be set to Trajectory'
        )
        required_ctx.assert_true(
            getattr(dataset, 'featureType', '') == 'trajectory',
            'featureType attribute must be set to trajectory'
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
