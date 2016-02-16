#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_metadata.py
'''

from compliance_checker.base import BaseCheck, BaseNCCheck, Result
import numpy as np

class NCEIMetadataCheck(BaseNCCheck):
    register_checker = True
    name = 'ncei-timeseries-orthogonal'
    _cc_spec = 'NCEI NetCDF Templates'
    _cc_spec_version = '2.0'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesOrthogonal.cdl'
    _cc_authors = 'Luke Campbell'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NCEI_NetCDF_TimeSeries_Orthogonal_Template_v2.0",
        "NCEI_NetCDF_TimeSeries_Incomplete_Template_v2.0"
    ]

    valid_feature_types = [
        'timeSeries'
    ]

    @classmethod
    def make_result(cls, level, score, out_of, name, messages):
        return Result(level, (score, out_of), name, messages)

    def setup(self, ds):
        pass

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
        '''

        level = BaseCheck.HIGH
        out_of = 8
        score = 0
        messages = []


        test = hasattr(dataset, 'ncei_template_version')
        if test:
            score += 1
        else:
            messages.append('Dataset is missing NCEI required attribute ncei_template_version')

        ncei_template_version = getattr(dataset, 'ncei_template_version', None)
        test = ncei_template_version in self.valid_templates
        if test:
            score += 1
        else:
            messages.append('ncei_template_version attribute references an invalid template: {}'.format(ncei_template_version))

        test = hasattr(dataset, 'featureType')

        if test:
            score += 1
        else:
            messages.append('Dataset is missing NCEI required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 


        for attribute in ('title', 'summary', 'keywords', 'Conventions'):
            test = getattr(dataset, attribute, '') != ''

            if test:
                score += 1
            else:
                messages.append('Dataset is missing the global attribute {}'.format(attribute))


        return self.make_result(level, score, out_of, 'Dataset contains NCEI required and highly recommended attributes', messages)

