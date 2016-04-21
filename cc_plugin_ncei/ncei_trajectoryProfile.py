#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_trajectoryProfile.py
'''

from compliance_checker.cf.cf import CFBaseCheck
from compliance_checker.base import Result, BaseCheck, score_group
from cc_plugin_ncei.ncei_metadata import NCEIMetadataCheck
from cc_plugin_ncei.ncei_base import NCEIBaseCheck
import cf_units
import numpy as np


class NCEITrajectoryProfileOrthogonal(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-trajectoryProfile-orthogonal'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/necdf/v1.1/trajectoryProfileIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TrajectoryProfile_Orthogonal_Template_v1.1"
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
        netcdf NODC_TrajectoryProfile_Orthogonal 
        dimensions:
              obs = <dim1> ;
              trajectory = <dim2> ;
              z = <dim3> ;
        '''
        out_of = 5
        score = 0
        msgs = []
        z_dim = _find_z_dimension(dataset)
        required_dimensions = ['trajectory']
        required_dimesions = required_dimensions.append(z_dim)

        for dim in required_dimensions:
            is_coord_var = False

            is_dim = dim in dataset.dimensions
            is_var = dim in dataset.variables
            if is_var:
                is_coord_var = dataset.variables[dim].dimensions == (dim,)

            test = np.sum([is_dim, is_coord_var])

            if not is_dim:
                msgs.append('{} is requried to be a dimension.'.format(dim))
            if not is_coord_var:
                msgs.append('{} is required to be a coordinate variable.'.format(dim))
            score += test
        
        if 'obs' in dataset.dimensions:
            score += 1
        else:
            msgs.append('obs must be a dimension')

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains required time dimensions', msgs)

    @score_group('Science Variables')
    def check_science_orthogonal(self, dataset):
        msgs = []
        results = []
        z_dim = _find_z_dimension(dataset)
        required_dims = ('trajectory', 'obs', z_dim,)
        for var in dataset.variables:
            if hasattr(dataset.variables[var],'coordinates'):
                dim_check = dataset.variables[var].dimensions == required_dims
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
            messages.append('Dataset is missing NCEI trajectoryProfile required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI trajectoryProfile require attributes', messages)

    @score_group('Required Variables')
    def check_trajectory(self, dataset):
        #Checks if the trajectoryProfile variable is formed properly
        msgs=[]
        results=[]

        #Check trajectoryProfile Exist
        if u'trajectory' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.LOW, exists_check, ('trajectory','exists'), msgs))       
        else:
            msgs = ['trajectoryProfile does not exist.  This is okay if there is only one trajectoryProfile in the dataset.']
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
    
    def check_lat_profile(self, dataset):
        msgs = []
        dim = dataset.variables['lat'].dimensions
        check_dim = dim == ('trajectory','obs',)
        if not check_dim:
            msgs=['lat has the wrong dimensions']
        return(Result(BaseCheck.HIGH, dim_check, ('lat','dimensions'),msgs))

    def check_lon_profile(self, dataset):
        msgs = []
        dim = dataset.variables['lon'].dimensions
        check_dim = dim == ('trajectory','obs',)
        if not check_dim:
            msgs=['lon has the wrong dimensions']
        return(Result(BaseCheck.HIGH, dim_check, ('lon','dimensions'),msgs))

    def check_time_profile(self, dataset):
        msgs = []
        dim = dataset.variables['time'].dimensions
        check_dim = dim == ('trajectory','obs',)
        if not check_dim:
            msgs=['time has the wrong dimensions']
        return(Result(BaseCheck.HIGH, dim_check, ('time','dimensions'),msgs))


class NCEITrajectoryProfileIncomplete(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-trajectoryProfile-orthogonal'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/necdf/v1.1/trajectoryProfileIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TrajectoryProfile_Orthogonal_Template_v1.1"
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
        netcdf NODC_TrajectoryProfile_Orthogonal 
        dimensions:
              obs = <dim1> ;
              trajectory = <dim2> ;
              nzMax = <dim3> ;
        '''
        out_of = 5
        score = 0
        msgs = []
        required_dimensions = ['trajectory']
        non_coord_dimensions = ['obs', 'nzMax']

        for dim in required_dimensions:
            is_coord_var = False

            is_dim = dim in dataset.dimensions
            is_var = dim in dataset.variables
            if is_var:
                is_coord_var = dataset.variables[dim].dimensions == (dim,)

            test = np.sum([is_dim, is_coord_var])

            if not is_dim:
                msgs.append('{} is requried to be a dimension.'.format(dim))
            if not is_coord_var:
                msgs.append('{} is required to be a coordinate variable.'.format(dim))
            score += test
       
        for dim in non_coord_dimensions:
            if dim in dataset.dimensions:
                score += 1
            else:
                msgs.append('{} must be a dimensions'.format(dim))

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains required time dimensions', msgs)

    @score_group('Science Variables')
    def check_science_orthogonal(self, dataset):
        msgs = []
        results = []
        for var in dataset.variables:
            if hasattr(dataset.variables[var],'coordinates'):
                dim_check = dataset.variables[var].dimensions == ('trajectory', 'obs', 'nzMax',)
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
            messages.append('Dataset is missing NCEI trajectoryProfile required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI trajectoryProfile require attributes', messages)

    @score_group('Required Variables')
    def check_trajectory(self, dataset):
        #Checks if the trajectoryProfile variable is formed properly
        msgs=[]
        results=[]

        #Check trajectoryProfile Exist
        if u'trajectory' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.LOW, exists_check, ('trajectory','exists'), msgs))       
        else:
            msgs = ['trajectoryProfile does not exist.  This is okay if there is only one trajectoryProfile in the dataset.']
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
    
    def check_lat_profile(self, dataset):
        msgs = []
        dim = dataset.variables['lat'].dimensions
        check_dim = dim == ('trajectory','obs',)
        if not check_dim:
            msgs=['lat has the wrong dimensions']
        return(Result(BaseCheck.HIGH, dim_check, ('lat','dimensions'),msgs))

    def check_lon_profile(self, dataset):
        msgs = []
        dim = dataset.variables['lon'].dimensions
        check_dim = dim == ('trajectory','obs',)
        if not check_dim:
            msgs=['lon has the wrong dimensions']
        return(Result(BaseCheck.HIGH, dim_check, ('lon','dimensions'),msgs))

    def check_time_profile(self, dataset):
        msgs = []
        dim = dataset.variables['time'].dimensions
        check_dim = dim == ('trajectory','obs',)
        if not check_dim:
            msgs=['time has the wrong dimensions']
        return(Result(BaseCheck.HIGH, dim_check, ('time','dimensions'),msgs))


