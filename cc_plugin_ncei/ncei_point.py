#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_point.py
'''

from compliance_checker.base import Result, BaseCheck, score_group
from cc_plugin_ncei.ncei_base import NCEIBaseCheck
import numpy as np

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
        netcdf NODC_point {
        dimensions:
        obs = < dim1 >; 
        '''
        msgs = []

        dimensions = [dim for dim in dataset.dimensions if 'Strlen' not in dim]
        if 'obs' not in dimensions:
            msgs.append('The dimension "obs" is preferred by the NODC template')
        score = len(dimensions)
        
        return Result(BaseCheck.HIGH, (score, score), 'NCEI Required Dimensions', msgs)

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
        '''

        out_of = 4
        score = 0
        messages = []

        test = hasattr(dataset, 'nodc_template_version')
        if test:
            score += 1
        else:
            messages.append('Dataset is missing NCEI required attribute nodc_template_version')

        ncei_template_version = getattr(dataset, 'nodc_template_version', None)
        test = ncei_template_version in self.valid_templates
        if test:
            score += 1
        else:
            messages.append('nodc_template_version attribute references an invalid template: {}'.format(ncei_template_version))

        test = hasattr(dataset, 'featureType')

        if test:
            score += 1
        else:
            messages.append('Dataset is missing NCEI Point required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'NCEI Point required attributes', messages)

    @score_group('Science Variables')
    def check_science_point(self, dataset):
        #Additional checks for Science Variables in a point Dataset
        results = []
        msgs = []
        #Check and Dimensions
        dims_required = [dim for dim in dataset.dimensions if 'Strlen' not in dim]
        for name in dataset.variables:
            var = dataset.variables[name]
            if hasattr(var, 'coordinates') and not hasattr(dataset.variables[name], 'flag_meanings'):
                dimensions = getattr(var, 'dimensions', None)
                dim_contain_check = all([dim in dims_required for dim in dimensions])
                if not dim_contain_check:
                    msgs = ['The dimensions for {} includes unexpected dimensions (<dim1>,)'.format(name)]
                results.append(Result(BaseCheck.MEDIUM, dim_contain_check, (name, 'dimensions'), msgs))
                dim_order_check =  any(dims_used in dimensions for dims_used in dims_required)
                if not dim_order_check:
                    msgs = ['The dimensions for {} are in the wrong order (<dim1>,)'.format(name)]
                results.append(Result(BaseCheck.MEDIUM, dim_order_check, (name, 'dimensions_order'), msgs))

                #@TODO Also, note that whenever any auxiliary coordinate variable contains a missing value, all other 
                #coordinate, auxiliary coordinate and data values corresponding to that element should also contain 
                #missing values.   
                #Check Cell Methods
                score = 0
                out_of = 0
                cell_methods = getattr(var, 'cell_methods', '')
                cell_methods = cell_methods.split(' ')
                cell_methods_keys = []
                for term in cell_methods:
                    if ':' in term and term.replace(':','') in dims_required:
                        score += 1
                        out_of += 1
                        cell_methods_keys.append(term.replace(':',''))
                    elif ':' in term and term.replace(':','') not in dims_required:
                        out_of += 1
                        msgs.append('The cell value key for {} is not in the required dimensions'.format(name))
                        cell_methods_keys.append(term.replace(':',''))
                results.append(Result(BaseCheck.MEDIUM, (score, out_of), (name, 'cell_methods_in_coordinate_vars'), msgs))

                method_keys_check = [dim in cell_methods_keys for dim in dims_required]
                if not all(method_keys_check):
                    msgs = ['Use coordinate variable to define the cell values']
                results.append(Result(BaseCheck.MEDIUM, (np.sum(method_keys_check), len(method_keys_check)), (name, 'cell_method_contains_all_dims'), msgs))

        return results
        
