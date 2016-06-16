#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_trajectory.py
'''

from compliance_checker.base import Result, BaseCheck, score_group
from cc_plugin_ncei.ncei_base import NCEIBaseCheck, TestCtx
from cc_plugin_ncei import util


class NCEITrajectory(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-trajectory'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/trajectoryIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Trajectory_Template_v1.1"
    ]

    valid_feature_types = [
        'trajectory',
        'trajectory_id'
    ]

    @classmethod
    def beliefs(cls):
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        Checks that the feature types of this dataset are consitent with a trajectory dataset
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

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
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

    def check_trajectory_id(self, dataset):
        '''
        Checks that if a variable exists for the trajectory id it has the appropriate attributes
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

