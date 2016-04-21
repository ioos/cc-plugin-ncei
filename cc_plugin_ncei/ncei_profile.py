#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_profile.py
'''

from compliance_checker.cf.cf import CFBaseCheck
from compliance_checker.base import Result, BaseCheck, score_group
from cc_plugin_ncei.ncei_metadata import NCEIMetadataCheck
from cc_plugin_ncei.ncei_base import NCEIBaseCheck
import cf_units
import numpy as np

class NCEIProfileOrthogonal(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-profile-orthogonal'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/profileOrthogonal.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_profile_Orthogonal_Template_v1.1",
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

    def is_orthogonal(self, dataset):
        if 'time' not in dataset.dimensions:
            return False

        return nc.variables['z'].dimensions == ('z',)


    def check_dimensions(self, dataset):
        '''
        NCEI_profile_Orthogonal
        dimensions:
           time = < dim1 >;//..... REQUIRED - Number of time steps in the time series
           profile = <dim2>; // REQUIRED - Number of time series (=1 for single time series or can be removed)

        NCEI_profile_Incomplete
        dimensions:
            ntimeMax = < dim1 >;//. REQUIRED - Number of time steps in the time series
            profile = <dim2>; // REQUIRED - Number of time series
        '''
        out_of = 2
        score = 0
        messages = []

        test = 'z' in dataset.dimensions

        if test:
            score += 1
        else:
            messages.append('z is a required dimension for profile Orthogonal')

        test = 'z' in dataset.variables and dataset.variables['z'].dimensions == ('z',)

        if test:
            score += 1
        else:
            messages.append('z is required to be a coordinate variable')

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains required time dimensions', messages)

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
            messages.append('Dataset is missing NODC required attribute ncei_template_version')

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
            messages.append('Dataset is missing NODC profile required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI profile required and highly recommended attributes', messages)

    @score_group('Science Variables')
    def check_science_orthogonal(self, dataset):
        msgs = []
        results = []
        z_name = 'z' #Taking a guess, but checking righta after
        for var in dataset.variables:
            if getattr(dataset.variables[var],'axis',None) == "Z":
                z_name = var
        for var in dataset.variables:
            if hasattr(dataset.variables[var],'coordinates'):
                dimensions = [dim for dim in dataset.dimensions if 'Strlen' not in dim and 'profile' not in dim]
                dim_check = dataset.variables[var].dimensions == (u'profile', z_name,)
                if not dim_check:
                    msgs = ['{} does not have the correct dimensions'.format(var)]
                results.append(Result(BaseCheck.HIGH, dim_check, (var, 'dimensions'), msgs))
        return results
    @score_group('Required Variables')
    def check_profile(self, dataset):
        #Checks if the profile variable is formed properly
        msgs=[]
        results=[]

        #Check profile Exist
        if u'profile' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.LOW, exists_check, ('profile','exists'), msgs))       
        else:
            msgs = ['profile does not exist.  This is okay if there is only one Time Series in the dataset.']
            exists_check = False
            return Result(BaseCheck.LOW, (0,1), ('profile','exists'), msgs)

        #Check CF Role
        if getattr(dataset.variables[u'profile'], 'cf_role', None) in self.valid_feature_types:
            cfrole_check = True
        else: 
            msgs = ['cf_role is wrong']
            cfrole_check = False
        results.append(Result(BaseCheck.MEDIUM, cfrole_check, ('profile','cf_role'), msgs))       
        
        #Check Long Name
        if hasattr(dataset.variables[u'profile'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('profile','long_name'), msgs))
        return results
        


class NCEIProfileIncomplete(NCEIBaseCheck):
    register_checker = True
    __cc_spec = 'ncei-profile-incomplete'
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

    def is_profile(self, dataset):
        if 'profile' not in dataset.dimensions:
            return False

        return nc.variables['profile'].dimensions == ('profile',)


    def check_dimensions(self, dataset):
        '''
        NCEI_profile_Incomplete
        dimensions:
            ntimeMax = < dim1 >;//. REQUIRED - Number of time steps in the time series
            profile = <dim2>; // REQUIRED - Number of time series
        '''
        out_of = 2
        score = 0
        messages = []

        test = 'profile' in dataset.dimensions

        if test:
            score += 1
        else:
            messages.append('profile is a required dimension for profile')

        dimensions = [dim for dim in dataset.dimensions if 'Strlen' not in dim and 'profile' not in dim]
        if len(dimensions) == 1:
            score += 1
            out_of += 1

        test = 'profile' in dataset.variables and dataset.variables['profile'].dimensions == ('profile',)
        if test:
            score += 1
        else:
            messages.append('profile is required to be a coordinate variable')
        
        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains required dimensions', messages)

    @score_group('Science Variables')
    def check_science_incomplete(self, dataset):
        msgs = []
        results = []
        z_name = 'z' #Taking a guess, but checking righta after
        for var in dataset.variables:
            if getattr(dataset.variables[var],'axis',None) == "Z":
                z_name = var
        for var in dataset.variables:
            if hasattr(dataset.variables[var],'coordinates'):
                dim_check = dataset.variables[var].dimensions == dataset.variables[z_name].dimensions
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
            messages.append('Dataset is missing NCEI profile required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI profile require attributes', messages)

    @score_group('Required Variables')
    def check_profile(self, dataset):
        #Checks if the profile variable is formed properly
        msgs=[]
        results=[]

        #Check profile Exist
        if u'profile' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.LOW, exists_check, ('profile','exists'), msgs))       
        else:
            msgs = ['profile does not exist.  This is okay if there is only one profile in the dataset.']
            exists_check = False
            return Result(BaseCheck.LOW, (0,1), ('profile','exists'), msgs)

        #Check CF Role
        if getattr(dataset.variables[u'profile'], 'cf_role', None) in self.valid_feature_types:
            cfrole_check = True
        else: 
            msgs = ['cf_role is wrong']
            cfrole_check = False
        results.append(Result(BaseCheck.MEDIUM, cfrole_check, ('profile','cf_role'), msgs))       
        
        #Check Long Name
        if hasattr(dataset.variables[u'profile'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('profile','long_name'), msgs))

        return results
        




