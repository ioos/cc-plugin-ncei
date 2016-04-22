#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_grid.py
'''

from compliance_checker.cf.cf import CFBaseCheck
from compliance_checker.base import Result, BaseCheck, score_group
from cc_plugin_ncei.ncei_metadata import NCEIMetadataCheck
from cc_plugin_ncei.ncei_base import NCEIBaseCheck
from cc_plugin_ncei.util import _find_z_dimension
import cf_units
import numpy as np

class NCEIGrid(NCEIBaseCheck):
    register_checker = True
    _cc_spec = 'ncei-grid'
    _cc_spec_version = '1.1'
    _cc_description = '''These templates are intended as a service to our community of Data Producers, and are also being used internally at NCEI in our own data development efforts. We hope the templates will serve as good starting points for Data Producers who wish to create preservable, discoverable, accessible, and interoperable data. It is important to note that these templates do not represent an attempt to create a new standard, and they are not absolutely required for archiving data at NCEI. However, we do hope that you will see the benefits in structuring your data following these conventions and NCEI stands ready to assist you in doing so.'''
    _cc_url = 'http://www.nodc.noaa.gov/data/formats/netcdf/v2.0/grid.cdl'
    _cc_authors = 'Luke Campbell, Dan Maher'
    _cc_checker_version = '2.1.0'

    valid_templates = [
        "NODC_NetCDF_Grid_Template_v1.1"
    ]

    valid_feature_types = [
        'grid'
    ]
    @classmethod
    def beliefs(cls): 
        '''
        Not applicable for gliders
        '''
        return {}

    def check_dimensions(self, dataset):
        '''
        netcdf NODC_Grid 
        dimensions:
	    lat = < dim1 >;
	    lon = < dim2 >;
	    time = < dim3 >;
	    z = < dim4 >;
	    nv = 2;
        '''
        out_of = 9
        score = 0
        messages = []

        required_dimensions = ['time', 'lat', 'lon', 'z']
        required_dimensions_not_coord_var = ['nv']

        for dim in required_dimensions:
            if dim in dataset.dimensions:
                score += 1
            else:
                messages.append('{} is a required dimension for Grid gatasets'.format(dim))
            if dim in dataset.variables and dataset.variables[dim].dimensions == (u'{}'.format(dim),):
                score += 1
            else:
                messages.append('{} is required to be a coordinate variable'.format(dim))

        for dim in required_dimensions_not_coord_var:
            if dim in dataset.dimensions:
                score += 1
            else:
                messages.append('{} is a required dimension for grid gatasets'.format(dim))

        return Result(BaseCheck.HIGH, (score, out_of), 'NCEI Required Dimensions', messages)

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
            messages.append('Dataset is missing NCEI Grid required attribute featureType')

        feature_type = getattr(dataset, 'featureType', None)
        test = feature_type in self.valid_feature_types

        if test:
            score += 1
        else:
            messages.append('featureType attribute references an invalid feature type: {}'.format(feature_type)) 

        return Result(BaseCheck.HIGH, (score, out_of), 'NCEI Grid required attributes', messages)

    @score_group('Required Variables')
    def check_lat_grid(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]

        #Check Lat Bounds
        bounds = getattr(dataset.variables[u'lat'], 'bounds', None)
        if bounds in dataset.variables:
            bounds_check = True
        else:
            bounds_check = False
            msgs.append('The bounds attribute is not in the variable list')
        return Result(BaseCheck.MEDIUM, bounds_check, ('lat','bounds'), msgs)      
        
    @score_group('Required Variables')
    def check_lon_grid(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]

        #Check Lon Bounds
        bounds = getattr(dataset.variables[u'lon'], 'bounds', None)
        if bounds in dataset.variables:
            bounds_check = True
        else:
            bounds_check = False
            msgs.append('The bounds attribute is not in the variable list')
        return Result(BaseCheck.MEDIUM, bounds_check, ('lon','bounds'), msgs)   
        
    @score_group('Required Variables')
    def check_time_grid(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]
        results=[]

        #Check Time Bounds
        bounds = getattr(dataset.variables[u'time'], 'bounds', None)
        if not bounds:
            bounds = getattr(dataset.variables[u'time'], 'climatology', None)
        if bounds in dataset.variables:
            bounds_check = True
        else:
            bounds_check = False
            msgs.append('The bounds attribute is not in the variable list')
        results.append(Result(BaseCheck.MEDIUM, bounds_check, ('time','bounds'), msgs))      
        return results 
    
    @score_group('Required Variables')
    def check_height_grid(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]
        results=[]
        try:
            getattr(dataset.variables[u'z'], 'bounds', None)
        except:        
            msgs.append('The z variable is missing')
            return Result(BaseCheck.MEDIUM, False, ('height_variable','bounds'), msgs)  
        #Check Z Bounds
        bounds = getattr(dataset.variables[u'z'], 'bounds', None)
        if bounds in dataset.variables:
            bounds_check = True
        else:
            bounds_check = False
            msgs.append('The bounds attribute is not in the variable list')
        results.append(Result(BaseCheck.MEDIUM, bounds_check, ('height_variable','bounds'), msgs))       
        
        return results


    @score_group('Boundary Variables')
    def check_lat_bounds_grid(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]
        results=[]

        #Check Lat Boundary Variable
        bounds = getattr(dataset.variables[u'lat'], 'bounds', None)
        if hasattr(dataset.variables[bounds], 'comment'):
            comment_check = True
        else:
            comment_check = False
            msgs.append('The comment attribute is missing')
        results.append(Result(BaseCheck.MEDIUM, comment_check, (bounds, 'comment'), msgs))

        if getattr(dataset.variables[bounds],'units',None) == 'degrees_north':
            unit_check = True
        else:
            unit_check = False
            msgs.append('The units attribute is missing or incorrect')
        results.append(Result(BaseCheck.MEDIUM, comment_check, (bounds, 'units'), msgs))
        
        dimensions = getattr(dataset.variables[bounds], 'dimensions', None)
        if dimensions == (u'lat',u'nv',):
            dim_check = True
        else:
            dim_check = False
            msgs = ['The dimensions are not right for the boundary variable']
        results.append(Result(BaseCheck.MEDIUM, dim_check, (bounds, 'dimensions'), msgs))

        return results 
    
    @score_group('Boundary Variables')
    def check_lon_bounds_grid(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]
        results=[]

        #Check Lon Boundary Variable
        bounds = getattr(dataset.variables[u'lon'], 'bounds', None)
        if hasattr(dataset.variables[bounds], 'comment'):
            comment_check = True
        else:
            comment_check = False
            msgs.append('The comment attribute is missing')
        results.append(Result(BaseCheck.MEDIUM, comment_check, (bounds, 'comment'), msgs))

        if getattr(dataset.variables[bounds],'units',None) == 'degrees_east':
            unit_check = True
        else:
            unit_check = False
            msgs.append('The units attribute is missing or incorrect')
        results.append(Result(BaseCheck.MEDIUM, comment_check, (bounds, 'units'), msgs))
        
        dimensions = getattr(dataset.variables[bounds], 'dimensions', None)
        if dimensions == (u'lon',u'nv',):
            dim_check = True
        else:
            dim_check = False
            msgs = ['The dimensions are not right for the boundary variable']
        results.append(Result(BaseCheck.MEDIUM, dim_check, (bounds, 'dimensions'), msgs))

        return results 
    
    @score_group('Boundary Variables')
    def check_time_bounds_grid(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]
        results=[]

        #Check Time Boundary Variable
        
        bounds = getattr(dataset.variables[u'time'], 'bounds', None)
        if not bounds:
            bounds = getattr(dataset.variables[u'time'], 'climatology', None)
        if hasattr(dataset.variables[bounds], 'comment'):
            comment_check = True
        else:
            comment_check = False
            msgs.append('The comment attribute is missing')
        results.append(Result(BaseCheck.MEDIUM, comment_check, (bounds, 'comment'), msgs))

        if getattr(dataset.variables[bounds],'units',None) == 'degrees_east':
            unit_check = True
        else:
            unit_check = False
            msgs.append('The units attribute is missing or incorrect')
        results.append(Result(BaseCheck.MEDIUM, comment_check, (bounds, 'units'), msgs))
        
        dimensions = getattr(dataset.variables[bounds], 'dimensions', None)
        if dimensions == (u'time',u'nv',):
            dim_check = True
        else:
            dim_check = False
            msgs = ['The dimensions are not right for the boundary variable']
        results.append(Result(BaseCheck.MEDIUM, dim_check, (bounds, 'dimensions'), msgs))

        return results 

    @score_group('Boundary Variables')
    def check_height_bounds_grid(self, dataset):
        #Checks if the timeseries variable is formed properly
        msgs=[]
        results=[]

        #Check Time Boundary Variable
        try:
            bounds = getattr(dataset.variables[u'z'], 'bounds', None)
        except:
            return Result(BaseCheck.MEDIUM, False, ('height_boundary_variable', 'exists'), ['There is not height boundary variable present'])

        if hasattr(dataset.variables[bounds], 'comment'):
            comment_check = True
        else:
            comment_check = False
            msgs.append('The comment attribute is missing')
        results.append(Result(BaseCheck.MEDIUM, comment_check, (bounds, 'comment'), msgs))

        if hasattr(dataset.variables[bounds],'units'):
            unit_check = True
        else:
            unit_check = False
            msgs.append('The units attribute is missing')
        results.append(Result(BaseCheck.MEDIUM, comment_check, (bounds, 'units'), msgs))
        
        dimensions = getattr(dataset.variables[bounds], 'dimensions', None)
        if dimensions == (u'z',u'nv',):
            dim_check = True
        else:
            dim_check = False
            msgs = ['The dimensions are not right for the boundary variable']
        results.append(Result(BaseCheck.MEDIUM, dim_check, (bounds, 'dimensions'), msgs))

        return results
    
    @score_group('Science Variables')
    def check_science_grid(self, dataset):
        #Additional checks for Science Variables in a Grid Dataset
        results = []
        msgs = []
        #Check Dimensions
        z_dim = _find_z_dimension(dataset)
        dims_required = (u'time', z_dim, u'lat', u'lon',)
        for name in dataset.variables:
            var = dataset.variables[name]
            if hasattr(var, 'coordinates') and not hasattr(dataset.variables[name], 'flag_meanings'):
                dimensions = getattr(var, 'dimensions', None)
                dim_contain_check = all([dim in dims_required for dim in dimensions])
                if not dim_contain_check:
                    msgs = ['The dimensions includes unexpected dimensions (time, z, lat, lon)']
                results.append(Result(BaseCheck.MEDIUM, dim_contain_check, (name, 'dimensions'), msgs))

                dim_order_check = dimensions == dims_required
                if not dim_order_check:
                    msgs = ['The dimensions are in the wrong order (time, z, lat, lon)']
                results.append(Result(BaseCheck.MEDIUM, dim_order_check, (name, 'dimensions_order'), msgs))

                #@TODO Also, note that whenever any auxiliary coordinate variable contains a missing value, all other 
                #coordinate, auxiliary coordinate and data values corresponding to that element should also contain 
                #missing values.   
                #Check 3) Cell Methods
                score = 0
                out_of = 0
                cell_methods = getattr(var, 'cell_methods', None).split(' ')
                cell_methods_keys = []
                for term in cell_methods:
                    if ':' in term and term.replace(':','') in dims_required:
                        score += 1
                        out_of += 1
                        cell_methods_keys.append(term.replace(':',''))
                    elif ':' in term and term.replace(':','') not in dims_required:
                        out_of += 1
                        msgs.append('The cell value key is not in the required dimensions')
                        cell_methods_keys.append(term.replace(':',''))
                results.append(Result(BaseCheck.MEDIUM, (score, out_of), (name, 'cell_methods_in_coordinate_vars'), msgs))

                method_keys_check = [dim in cell_methods_keys for dim in dims_required]
                if not all(method_keys_check):
                    msgs = ['Each coordinate variable should have a cell method explaining the grid']
                results.append(Result(BaseCheck.MEDIUM, (np.sum(method_keys_check), len(method_keys_check)), (name, 'dimensions_have_cell_method'), msgs))

        return results
        
