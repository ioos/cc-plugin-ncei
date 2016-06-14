#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_point.py
'''

from compliance_checker.base import BaseCheck
from cc_plugin_ncei.ncei_base import NCEIBaseCheck, TestCtx
from cc_plugin_ncei import util


class NCEIPoint(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-point'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/point.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_Point_Template_v1.1"
    ]

    valid_feature_types = [
        'station',
        'point'
    ]

    @classmethod
    def beliefs(cls): 
        '''
        Not applicable for gliders
        '''
        return {}

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


