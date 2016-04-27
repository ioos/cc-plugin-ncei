#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_trajectory.py
'''

from compliance_checker.cf.cf import CFBaseCheck
from compliance_checker.base import Result, BaseCheck, score_group
from cc_plugin_ncei.ncei_base import NCEIBaseCheck
import cf_units
import numpy as np


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
        NCEI_Trajectory_Incomplete
        dimensions:
            ntimeMax = < dim1 >;//. REQUIRED - Number of time steps in the time series
            trajectory = <dim2>; // REQUIRED - Number of time series
        '''
        out_of = 2
        score = 0
        messages = []

        test = 'trajectory' in dataset.dimensions

        if test:
            score += 1
        else:
            messages.append('trajectory is a required dimension for Trajectory')

        dimensions = [dim for dim in dataset.dimensions if 'Strlen' not in dim and 'trajectory' not in dim]
        if len(dimensions) == 1:
            score += 1
            out_of += 1

        test = 'trajectory' in dataset.variables and dataset.variables['trajectory'].dimensions == ('trajectory',)
        if test:
            score += 1
        else:
            messages.append('trajectory is required to be a coordinate variable')
        
        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains required dimensions', messages)

    @score_group('Science Variables')
    def check_science_incomplete(self, dataset):
        msgs = []
        results = []
        for var in dataset.variables:
            if hasattr(dataset.variables[var],'coordinates'):
                dimensions = [dim for dim in dataset.dimensions if 'Strlen' not in dim and 'trajectory' not in dim]
                dim_check = dataset.variables[var].dimensions == dataset.variables['time'].dimensions
                if not dim_check:
                    msgs = ['{} does not have the correct dimensions'.format(var)]
                results.append(Result(BaseCheck.HIGH, dim_check, (var, 'dimensions'), msgs))
        return results

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
            messages.append('Dataset is missing NCEI Trajectory required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI Trajectory require attributes', messages)

    @score_group('Required Variables')
    def check_trajectory(self, dataset):
        #Checks if the trajectory variable is formed properly
        msgs=[]
        results=[]

        #Check Trajectory Exist
        if u'trajectory' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.LOW, exists_check, ('trajectory','exists'), msgs))       
        else:
            msgs = ['trajectory does not exist.  This is okay if there is only one Trajectory in the dataset.']
            exists_check = False
            return Result(BaseCheck.LOW, (0,1), ('trajectory','exists'), msgs)

        #Check CF Role
        if getattr(dataset.variables[u'trajectory'], 'cf_role', None) in self.valid_feature_types:
            cfrole_check = True
        else: 
            msgs = ['cf_role is wrong']
            cfrole_check = False
        results.append(Result(BaseCheck.MEDIUM, cfrole_check, ('trajectory','cf_role'), msgs))       
        
        #Check Long Name
        if hasattr(dataset.variables[u'trajectory'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('trajectory','long_name'), msgs))

        return results
        




