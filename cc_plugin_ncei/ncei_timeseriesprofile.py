#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_timeseriesprofile.py
'''

from compliance_checker.cf.cf import CFBaseCheck
from compliance_checker.base import Result, BaseCheck, score_group
from cc_plugin_ncei.ncei_metadata import NCEIMetadataCheck
from cc_plugin_ncei.ncei_base import NCEIBaseCheck
from cc_plugin_ncei.util import _find_z_dimension
import cf_units
import numpy as np

class NCEITimeSeriesProfileOrthogonal(NCEIBaseCheck):
    register_checker = True
    name = 'ncei-timeseriesprofile-orthogonal'
    _cc_spec = 'NCEI NetCDF Templates'
    _cc_spec_version = '2.0'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/timeSeriesOrthogonal.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeriesProfile_Orthogonal_Template_v1.1",
    ]

    valid_feature_types = [
        'timeseries',
        'timeseries_id',
        'timeSeriesProfile'
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

        return nc.variables['time'].dimensions == ('time',)


    def check_dimensions(self, dataset):
        '''
        NODC_TimeSeriesProfile_Orthogonal 
        dimensions:
              z = <dim1> ;
              station = <dim2> ;
              time = <dim3> ;
        '''
        out_of = 6
        score = 0
        msgs = []
        z_dim = _find_z_dimension(dataset)
        required_dimensions = ['station', 'time']
        required_dimensions.append(z_dim)

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

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains required time dimensions', msgs)

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
            messages.append('Dataset is missing NODC TimeSeriesProfile required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI TimeSeriesProfile required and highly recommended attributes', messages)

    @score_group('Required Variables')
    def check_timeseriesprofile(self, dataset):
        #Checks if the station variable is formed properly
        msgs=[]
        results=[]

        #Check 1) TimeSeries Exist
        if u'station' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.LOW, exists_check, ('station','exists'), msgs))       
        else:
            msgs = ['station does not exist.  This is okay if there is only one Time Series in the dataset.']
            exists_check = False
            return Result(BaseCheck.LOW, (0,1), ('station','exists'), msgs)

        #Check 2) CF Role
        if getattr(dataset.variables[u'station'], 'cf_role', None) in self.valid_feature_types:
            cfrole_check = True
        else: 
            msgs = ['cf_role is wrong']
            cfrole_check = False
        results.append(Result(BaseCheck.MEDIUM, cfrole_check, ('station','cf_role'), msgs))       
        
        #Check 3) Long Name
        if hasattr(dataset.variables[u'station'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('station','long_name'), msgs))
        return results
        


class NCEITimeSeriesProfileOrthTimeIncompleteDepth(NCEIBaseCheck):
    register_checker = True
    name = 'ncei-timeseriesprofile-orthtime-incompletedepth'
    _cc_spec = 'NCEI NetCDF Templates'
    _cc_spec_version = '2.0'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeriesProfile_IncompleteVertical_OrthogonalTemporal_Template_v1.1"
    ]

    valid_feature_types = [
        'timeSeries',
        'timeseries_id',
        'timeSeriesProfile',
        'timeseriesprofile_id'
    ]
    @classmethod
    def beliefs(cls): 
        '''
        Not applicable for gliders
        '''
        return {}

    def is_incomplete(self, dataset):
        if 'timeSeries' not in dataset.dimensions:
            return False

        return nc.variables['timeSeries'].dimensions == ('timeSeries',)


    def check_dimensions(self, dataset):
        '''
        NCEI_TimeSeries_Incomplete
        dimensions:
            ntimeMax = < dim1 >;//. REQUIRED - Number of time steps in the time series
            timeSeries = <dim2>; // REQUIRED - Number of time series
        '''
        out_of = 5
        score = 0
        msgs = []
        required_dimensions = [u'nzMax', u'station', u'time']
        for dim in required_dimensions:
            is_coord_var = False

            is_dim = dim in dataset.dimensions
            if not is_dim:
                msgs.append('{} is requried to be a dimension.'.format(dim))
            if dim == u'nzMax':
                score += 1
                continue
            is_var = dim in dataset.variables
            if is_var:
                is_coord_var = dataset.variables[dim].dimensions == (dim,)

            test = np.sum([is_dim, is_coord_var])

            if not is_coord_var:
                msgs.append('{} is required to be a coordinate variable.'.format(dim))
            score += test

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains required time dimensions', msgs)

    @score_group('Science Variables')
    def check_science_incomplete(self, dataset):
        msgs = []
        results = []
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
            messages.append('Dataset is missing NCEI TimeSeries required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI TimeSeries require attributes', messages)

    @score_group('Required Variables')
    def check_timeseries(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]
        results=[]

        #Check 1) TimeSeries Exist
        if u'station' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.LOW, exists_check, ('station','exists'), msgs))       
        else:
            msgs = ['station does not exist.  This is okay if there is only one Time Series in the dataset.']
            exists_check = False
            return Result(BaseCheck.LOW, (0,1), ('station','exists'), msgs)

        #Check 2) CF Role
        if getattr(dataset.variables[u'station'], 'cf_role', None) in self.valid_feature_types:
            cfrole_check = True
        else: 
            msgs = ['cf_role is wrong']
            cfrole_check = False
        results.append(Result(BaseCheck.MEDIUM, cfrole_check, ('station','cf_role'), msgs))       
        
        #Check 3) Long Name
        if hasattr(dataset.variables[u'station'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('station','long_name'), msgs))
        return results

    @score_group('Required Variables')
    def check_z(self, dataset):
        msgs = []
        
        for var in dataset.variables:
            if getattr(dataset.variables[var], 'axis', None) == 'Z':
                dim_check = dataset.variables[var].dimensions == ('station', 'time', 'nzMax',)
                if dim_check == False:
                    msgs.append('The dimension of the depth variable is wrong')
                return Result(BaseCheck.HIGH, dim_check, (var,'dimension'), msgs)

        return
        
class NCEITimeSeriesProfileIncomplete(NCEIBaseCheck):
    register_checker = True
    name = 'ncei-timeseriesprofile-incomplete'
    _cc_spec = 'NCEI NetCDF Templates'
    _cc_spec_version = '2.0'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeriesProfile_Incomplete_Template_v1.1"
    ]

    valid_feature_types = [
        'timeSeries',
        'timeseries_id',
        'timeSeriesProfile',
        'timeseriesprofile_id'
    ]
    @classmethod
    def beliefs(cls): 
        '''
        Not applicable for gliders
        '''
        return {}

    def is_incomplete(self, dataset):
        if 'timeSeries' not in dataset.dimensions:
            return False

        return nc.variables['timeSeries'].dimensions == ('timeSeries',)


    def check_dimensions(self, dataset):
        '''
        netcdf NODC_TimeSeriesProfile_Incomplete {
        dimensions:
              nzMax = <dim1> ;
              station = <dim2> ;
              ntimeMax = <dim3> ;
        '''
        out_of = 4
        score = 0
        msgs = []
        required_dimensions = [u'nzMax', u'station', u'ntimeMax']
        for dim in required_dimensions:
            is_coord_var = False

            is_dim = dim in dataset.dimensions
            if not is_dim:
                msgs.append('{} is requried to be a dimension.'.format(dim))
            if dim == u'nzMax' or dim == 'ntimeMax':
                score += 1
                continue
            is_var = dim in dataset.variables
            if is_var:
                is_coord_var = dataset.variables[dim].dimensions == (dim,)

            test = np.sum([is_dim, is_coord_var])

            if not is_coord_var:
                msgs.append('{} is required to be a coordinate variable.'.format(dim))
            score += test

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains required time dimensions', msgs)

    @score_group('Science Variables')
    def check_science_incomplete(self, dataset):
        msgs = []
        results = []
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
            messages.append('Dataset is missing NCEI TimeSeries required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI TimeSeries require attributes', messages)

    @score_group('Required Variables')
    def check_timeseries(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]
        results=[]

        #Check 1) TimeSeries Exist
        if u'station' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.LOW, exists_check, ('station','exists'), msgs))       
        else:
            msgs = ['station does not exist.  This is okay if there is only one Time Series in the dataset.']
            exists_check = False
            return Result(BaseCheck.LOW, (0,1), ('station','exists'), msgs)

        #Check 2) CF Role
        if getattr(dataset.variables[u'station'], 'cf_role', None) in self.valid_feature_types:
            cfrole_check = True
        else: 
            msgs = ['cf_role is wrong']
            cfrole_check = False
        results.append(Result(BaseCheck.MEDIUM, cfrole_check, ('station','cf_role'), msgs))       
        
        #Check 3) Long Name
        if hasattr(dataset.variables[u'station'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('station','long_name'), msgs))
        return results

    @score_group('Required Variables')
    def check_z(self, dataset):
        msgs = []
        
        for var in dataset.variables:
            if getattr(dataset.variables[var], 'axis', None) == 'Z':
                dim_check = dataset.variables[var].dimensions == ('station', 'ntimeMax', 'nzMax',)
                if dim_check == False:
                    msgs.append('The dimension of the depth variable is wrong')
                return Result(BaseCheck.HIGH, dim_check, (var,'dimension'), msgs)

        return
        
class NCEITimeSeriesProfileIncompleteTimeOrthDepth(NCEIBaseCheck):
    register_checker = True
    name = 'ncei-timeseriesprofile-incompletetime-orthdepth'
    _cc_spec = 'NCEI NetCDF Templates'
    _cc_spec_version = '2.0'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/timeSeriesIncomplete.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_TimeSeriesProfile_OrthogonalVertical_IncompleteTemporal_Template_v1.1"
    ]

    valid_feature_types = [
        'timeSeries',
        'timeseries_id',
        'timeSeriesProfile',
        'timeseriesprofile_id'
    ]
    @classmethod
    def beliefs(cls): 
        '''
        Not applicable for gliders
        '''
        return {}

    def is_incomplete(self, dataset):
        if 'timeSeries' not in dataset.dimensions:
            return False

        return nc.variables['timeSeries'].dimensions == ('timeSeries',)


    def check_dimensions(self, dataset):
        '''
        netcdf NODC_TimeSeriesProfile_OrthogonalVertical_IncompleteTemporal {
        dimensions:
              z = <dim1> ;
              station = <dim2> ;
              ntimeMax = <dim3> ;
        '''
        out_of = 5
        score = 0
        msgs = []
        z_dim = _find_z_dimension(dataset)
        required_dimensions = [z_dim, u'station', u'ntimeMax']

        for dim in required_dimensions:
            is_coord_var = False

            is_dim = dim in dataset.dimensions
            if not is_dim:
                msgs.append('{} is requried to be a dimension.'.format(dim))
            if dim == 'ntimeMax':
                score += 1
                continue
            is_var = dim in dataset.variables
            if is_var:
                is_coord_var = dataset.variables[dim].dimensions == (dim,)

            test = np.sum([is_dim, is_coord_var])

            if not is_coord_var:
                msgs.append('{} is required to be a coordinate variable.'.format(dim))
            score += test

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains required time dimensions', msgs)

    @score_group('Science Variables')
    def check_science_incompletetime_orthdepth(self, dataset):
        msgs = []
        results = []
        z_dim = _find_z_dimension(dataset)
        for var in dataset.variables:
            if hasattr(dataset.variables[var],'coordinates'):
                dim_check = dataset.variables[var].dimensions == ('station', 'ntimeMax', z_dim,)
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
            messages.append('Dataset is missing NCEI TimeSeries required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI TimeSeries require attributes', messages)

    @score_group('Required Variables')
    def check_timeseriesprofile(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]
        results=[]

        #Check 1) TimeSeries Exist
        if u'station' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.LOW, exists_check, ('station','exists'), msgs))       
        else:
            msgs = ['station does not exist.  This is okay if there is only one Time Series in the dataset.']
            exists_check = False
            return Result(BaseCheck.LOW, (0,1), ('station','exists'), msgs)

        #Check 2) CF Role
        if getattr(dataset.variables[u'station'], 'cf_role', None) in self.valid_feature_types:
            cfrole_check = True
        else: 
            msgs = ['cf_role is wrong']
            cfrole_check = Falsei
        results.append(Result(BaseCheck.MEDIUM, cfrole_check, ('station','cf_role'), msgs))       
        
        #Check 3) Long Name
        if hasattr(dataset.variables[u'station'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('station','long_name'), msgs))
        return results

    @score_group('Required Variables')
    def check_z(self, dataset):
        msgs = []
        z_dim = _find_z_dimension(dataset)

        dim_check = dataset.variables[z_dim].dimensions == (z_dim,)
        if dim_check == False:
            msgs.append('The dimension of the depth variable is wrong')
        return Result(BaseCheck.HIGH, dim_check, (z_dim,'dimension'), msgs)

        return
