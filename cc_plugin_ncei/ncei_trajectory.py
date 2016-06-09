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
        Checks that the feature types of this dataset are consitent with a time series orthogonal dataset
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'All geophysical variables are trajectory feature types')
        trajectory_ctx = TestCtx(BaseCheck.HIGH, 'A variable defining "trajectory_id" exists')

        # Exit prematurely if we can't even find a trajectory_id
        trajectory_ids = dataset.get_variables_by_attributes(cf_role='trajectory_id')
        trajectory_ctx.assert_true(len(trajectory_ids), 'No variable defining cf_role="trajectory_id" exists')
        if not trajectory_ids:
            return trajectory_ctx.to_result()

        trajectory_dims = trajectory_ids[0].dimensions
        trajectory_ctx.assert_true(len(trajectory_dims), '{} must have at least one dimension'.format(trajectory_ids[0]))
        if not trajectory_dims:
            return trajectory_ctx.to_result()

        results.append(trajectory_ctx.to_result())

        # i is the first dimension of the variable where cf_role = 'trajectory_id'
        i = trajectory_dims[0]

        timevar = util.get_time_variable(dataset)
        if not timevar:
            required_ctx.assert_true(False, 'No time variable found')
            results.append(required_ctx.to_result())
            return results

        time_dims = dataset.variables[timevar].dimensions
        if len(time_dims) != 2:
            required_ctx.assert_true(False, '{} variable must have 2 dimensions'.format(timevar))
            results.append(required_ctx.to_result())
            return results

        if time_dims[0] != i:
            required_ctx.assert_true(False, '{} variable dimension 1 must be {}'.format(timevar, i))
            results.append(required_ctx.to_result())
            return results

        o = time_dims[1]

        message = '{} must be a valid timeseries feature type. It must have dimensions of ({}). And all coordinates must have dimensions ({})'
        for variable in util.get_geophysical_variables(dataset):
            is_valid = util.is_cf_trajectory(dataset, variable)
            required_ctx.assert_true(
                is_valid,
                message.format(variable, ', '.join([i, o])),
                message.format(variable, ', '.join([i, o]))
            )
        results.append(required_ctx.to_result())
        print results
        return results

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
        '''
        results = []
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required Global Attributes for Trajectory dataset')
        required_ctx.assert_true(
            getattr(dataset, 'nodc_template_version', '') == 'NODC_NetCDF_Trajectory_Template_v1.1',
            'nodc_template_version attribute must be NODC_NetCDF_Trajectory_Template_v1.1'
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
        trajectory_ids = dataset.get_variables_by_attributes(cf_role='trajectory_id')
        # No need to check
        if not trajectory_ids:
            return
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for the {} variable'.format(trajectory_ids[0].name))
        test_ctx.assert_true(
            getattr(trajectory_ids[0].name, 'long_name', '') != "",
            "long_name attribute should exist and not be empty"
        )
        return test_ctx.to_result()

