#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_base.py
'''
from __future__ import print_function

from compliance_checker.base import Result, BaseCheck, score_group, BaseNCCheck
from compliance_checker.cf.util import StandardNameTable, units_known
from cc_plugin_ncei.util import _find_platform_variables, _find_instrument_variables, getattr_check, hasattr_check, var_dtype, _find_crs_variable
from cc_plugin_ncei.util import get_sea_names
import re


class TestCtx(object):
    '''
    Simple struct object that holds score values and messages to compile into a result
    '''
    def __init__(self, category=None, description='', out_of=0, score=0, messages=None):
        self.category = category or BaseCheck.LOW
        self.out_of = out_of
        self.score = score
        self.messages = messages or []
        self.description = description or ''


    def to_result(self):
        return Result(self.category, (self.score, self.out_of), self.description, self.messages)


class NCEIBaseCheck(BaseNCCheck):
    register_checker = True

    @classmethod
    def __init__(self):
        self._std_names = StandardNameTable('cf-standard-name-table.xml')

    def setup(self, ds):
        pass

    def assert_is(self, ctx, test, message):
        '''
        Increments score if test is true otherwise appends a message
        '''
        ctx.out_of += 1

        if test:
            ctx.score += 1
        else:
            ctx.messages.append(message)

    def check_base_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes

        :Conventions = "CF-1.6" ; //......................................... REQUIRED    - Always try to use latest value. (CF)
        :Metadata_Conventions = "Unidata Dataset Discovery v1.0" ; //........ REQUIRED    - Do not change. (ACDD)
        :featureType = "timeSeries" ; //..................................... REQUIRED - CF attribute for identifying the featureType.
        :cdm_data_type = "Station" ; //...................................... REQUIRED (ACDD)
        :nodc_template_version = "NODC_NetCDF_TimeSeries_Orthogonal_Template_v1.1" ; //....... REQUIRED (NODC)
        :standard_name_vocabulary = "NetCDF Climate and Forecast (CF) Metadata Convention Standard Name Table "X"" ; //........ REQUIRED    - If using CF standard name attribute for variables. "X" denotes the table number  (ACDD)
        '''

        test_ctx = TestCtx(BaseCheck.HIGH, 'Dataset contains NCEI required and highly recommended attributes')

        conventions = getattr(dataset, 'Conventions', '')
        metadata_conventions = getattr(dataset, 'Metadata_Conventions', '')
        feature_type = getattr(dataset, 'featureType', '')
        cdm_data_type = getattr(dataset, 'cdm_data_type')
        standard_name_vocab = getattr(dataset, 'standard_name_vocabulary', '')

        self.assert_is(test_ctx,
                       conventions == 'CF-1.6',
                       'Conventions attribute is missing or is not equal to CF-1.6: {}'.format(conventions))
        self.assert_is(test_ctx,
                       metadata_conventions == 'Unidata Dataset Discovery v1.0',
                       "Metadata_Conventions attribute is required to be 'Unidata Dataset Discovery v1.0': {}".format(metadata_conventions))
        self.assert_is(test_ctx,
                       feature_type in ['station', 'timeSeries', 'trajectory', 'profile', 'timeSeriesProfile', 'grid'],
                       'Feature type must be one of station, timeSeries, trajectory, profile, timeSeriesProfile, grid: {}'.format(feature_type))
        self.assert_is(test_ctx,
                       cdm_data_type in ['Point', 'Station', 'Trajectory', 'Profile', 'Grid'],
                       'cdm_data_type must be one of Point, Station, Trajectory, Profile, Grid: {}'.format(cdm_data_type))

        feature_cdm_map = {
            'station': 'Point',
            'timeSeries': 'Station',
            'trajectory': 'Trajectory',
            'profile': 'Profile',
            'timeSeriesProfile': 'Profile',
            'grid': 'Grid'
        }
        self.assert_is(test_ctx,
                       feature_cdm_map[feature_type] == cdm_data_type,
                       'cdm_data_type must correspond to the featureType specified: {} doesn\'t map to {}'.format(feature_type, cdm_data_type))
        self.assert_is(test_ctx,
                       standard_name_vocab.startswith("NetCDF Climate and Forecast (CF) Metadata Convention Standard Name Table"),
                       "standard_name_vocabulary doesn't start with 'NetCDF Climate and Forecast (CF) Metadata Convention Standard Name Table': {}".format(standard_name_vocab))

        return test_ctx.to_result()

    ################################################################################
    # Checks for Required Variables
    ################################################################################

    @score_group('Required Variables')
    def check_lat(self, dataset):
        '''
        float lat(time) ;//....................................... Depending on the precision used for the variable, the data type could be int or double instead of float.
                lat:long_name = "" ; //...................................... RECOMMENDED - Provide a descriptive, long name for this variable.
                lat:standard_name = "latitude" ; //.......................... REQUIRED    - Do not change.
                lat:units = "degrees_north" ; //............................. REQUIRED    - CF recommends degrees_north, but at least must use UDUNITS.
                lat:axis = "Y" ; //.......................................... REQUIRED    - Do not change.
                lat:valid_min = 0.0f ; //.................................... RECOMMENDED - Replace with correct value.
                lat:valid_max = 0.0f ; //.................................... RECOMMENDED - Replace with correct value.
                lat:_FillValue = 0.0f;//..................................... REQUIRED  if there could be missing values in the data.
                lat:ancillary_variables = "" ; //............................ RECOMMENDED - List other variables providing information about this variable.
                lat:comment = "" ; //........................................ RECOMMENDED - Add useful, additional information here.
        '''

        # Checks if the lat variable is formed properly

        msgs = []
        results = []
        var = u'lat'

        # Check 1) lat exist

        if var in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.HIGH, exists_check, (var, 'exists'), msgs))
        else:
            msgs = ['{} does not exist'.format(var)]
            return Result(BaseCheck.HIGH, (0, 1), (var, 'exists'), msgs)

        # Check 2) Data Type
        valid_types = ['int', 'long', 'double', 'float']
        results.append(var_dtype(dataset, var, valid_types, BaseCheck.HIGH))

        # Check 3,4,5 Check standard name, units, and axis
        get_attr_val = [
            ('standard_name', 'latitude'),
            ('units', 'degrees_north'),
            ('axis', 'Y')
        ]
        # Check 6,7,8,9,10,11 has these attributes
        has_var_attr = [
            'valid_min',
            'valid_max',
            'ancillary_variables',
            'comment',
            'long_name'
        ]

        for attr, val in get_attr_val:
            results.append(getattr_check(dataset, var, attr, val, BaseCheck.HIGH))

        for attr in has_var_attr:
            results.append(hasattr_check(dataset, var, attr, BaseCheck.MEDIUM))
 
        return results

    @score_group('Required Variables')
    def check_lon(self, dataset):
        '''
                float lat(time) ;//....................................... Depending on the precision used for the variable, the data type could be int or double instead of float. 
                lat:long_name = "" ; //...................................... RECOMMENDED - Provide a descriptive, long name for this variable.
                lat:standard_name = "latitude" ; //.......................... REQUIRED    - Do not change.
                lat:units = "degrees_north" ; //............................. REQUIRED    - CF recommends degrees_north, but at least must use UDUNITS.
                lat:axis = "Y" ; //.......................................... REQUIRED    - Do not change.
                lat:valid_min = 0.0f ; //.................................... RECOMMENDED - Replace with correct value.
                lat:valid_max = 0.0f ; //.................................... RECOMMENDED - Replace with correct value.
                lat:_FillValue = 0.0f;//..................................... REQUIRED  if there could be missing values in the data.
                lat:ancillary_variables = "" ; //............................ RECOMMENDED - List other variables providing information about this variable.
                lat:comment = "" ; //........................................ RECOMMENDED - Add useful, additional information here.
                '''
        #Checks if the lon variable is formed properly
        msgs=[]
        results=[]
        var = u'lon'

       #Check lon exist
        if var in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.HIGH, exists_check, (var,'exists'), msgs))
        else:
            msgs = ['{} does not exist'.format(var)]
            return Result(BaseCheck.HIGH, (0,1), (var,'exists'), msgs)
       
        #Check Data Type
        valid_types = ['int', 'long', 'double', 'float']
        results.append(var_dtype(dataset, var, valid_types, BaseCheck.HIGH))

        #Check Check standard name, units, and axis
        get_attr_val = [
                ('standard_name', 'longitude'), 
                ('units', 'degrees_east'), 
                ('axis', 'X')
                ]
        #Check has these attributes
        has_var_attr = [
                #'_FillValue',
                'valid_min',
                'valid_max',
                'ancillary_variables',
                'comment',
                'long_name'
                ]

        for attr,val in get_attr_val:
            results.append(getattr_check(dataset, var, attr, val, BaseCheck.HIGH))

        for attr in has_var_attr:
            results.append(hasattr_check(dataset, var, attr, BaseCheck.MEDIUM))
 
        return results

    @score_group('Required Variables')
    def check_time(self, dataset):
        '''
                double time(time) ;//........................................ Depending on the precision used for the variable, the data type could be int or double instead of float.
                time:long_name = "" ; //..................................... RECOMMENDED - Provide a descriptive, long name for this variable. 
                time:standard_name = "time" ; //............................. REQUIRED    - Do not change
                time:units = "seconds since 1970-01-01 00:00:00 0:00" ; //... REQUIRED    - Use approved CF convention with approved UDUNITS.
                time:calendar = "julian" ; //................................ REQUIRED    - IF the calendar is not default calendar, which is "gregorian".
                time:axis = "T" ; //......................................... REQUIRED    - Do not change.
                time:_FillValue = 0.0f;//.................................... REQUIRED  if there could be missing values in the data.
                time:ancillary_variables = "" ; //........................... RECOMMENDED - List other variables providing information about this variable.
                time:comment = "" ; //....................................... RECOMMENDED - Add useful, additional information here. 
                '''
        #Checks if the time variable is formed properly
        msgs=[]
        results=[]
        var = u'time'
       #Check time exist

        if var in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.HIGH, exists_check, (var,'exists'), msgs))
        else:
            msgs = ['{} does not exist'.format(var)]
            return Result(BaseCheck.HIGH, (0,1), (var,'exists'), msgs)
       
        #Check Data Type
        valid_types = ['int', 'long', 'double', 'float']
        results.append(var_dtype(dataset, var, valid_types, BaseCheck.HIGH))

        #Check  Check standard name and axis
        get_attr_val = [
                ('standard_name', 'time'), 
                ('axis', 'T')
                ]
        #Check has these attributes
        has_var_attr = [
                'ancillary_variables',
                'comment',
                'long_name',
                'calendar'
                ]

        for attr,val in get_attr_val:
            results.append(getattr_check(dataset, var, attr, val, BaseCheck.HIGH))

        for attr in has_var_attr:
            results.append(hasattr_check(dataset, var, attr, BaseCheck.MEDIUM))
 
        #Check Units
        if 'since' in getattr(dataset.variables[var], 'units', None):
            units_check = True
        else: 
            msgs = ['units are wrong']
            units_check = False
        results.append(Result(BaseCheck.HIGH, units_check, (var,'units'), msgs))
        
        return results

    @score_group('Required Variables')
    def check_height(self, dataset):
        #Checks if the lat variable is formed properly
        '''
                float z(time) ;//........................................ Depending on the precision used for the variable, the data type could be int or double instead of float. Also the variable "z" could be substituted with a more descriptive name like "depth", "altitude", "pressure", etc.
                z:long_name = "" ; //........................................ RECOMMENDED - Provide a descriptive, long name for this variable. 
                z:standard_name = "" ; //.................................... REQUIRED    - Usually "depth" or "altitude" is used.
                z:units = "" ; //............................................ REQUIRED    - Use UDUNITS.
                z:axis = "Z" ; //............................................ REQUIRED    - Do not change.
                z:positive = "" ; //......................................... REQUIRED    - Use "up" or "down".
                z:valid_min = 0.0f ; //...................................... RECOMMENDED - Replace with correct value.
                z:valid_max = 0.0f ; //...................................... RECOMMENDED - Replace with correct value.
                z:_FillValue = 0.0f;//....................................... REQUIRED  if there could be missing values in the data.
                z:ancillary_variables = "" ; //.............................. RECOMMENDED - List other variables providing information about this variable.
                z:comment = "" ; //.......................................... RECOMMENDED - Add useful, additional information here.
                '''
        msgs=[]
        results=[]
        #best guess for variable name and units
        valid_types = ['int', 'long', 'double', 'float']
        valid_variable_names = ["depth", "DEPTH",
              "depths", "DEPTHS",
              "height", "HEIGHT",
              "altitude", "ALTITUDE",
              "alt", "ALT",
              "Alt", "Altitude",
              "h", "H",
              "s_rho", "S_RHO",
              "s_w", "S_W",
              "z", "Z",
              "siglay", "SIGLAY",
              "siglev", "SIGLEV",
              "sigma", "SIGMA",
              "vertical", "VERTICAL", "lev", "LEV", "level", "LEVEL"
              ]
        valid_units = ['m','meters','meter','metre','metres','km','kilometers','kilometer','bar','millibar','decibar','atm','atmosphere','pascal','Pa','hPa']

        #Check  height exists and Check Axis 
        no_height = True
        for var in dataset.variables:
            if getattr(dataset.variables[var],'axis',None) == 'Z':
                no_height = False
                results.append(Result(BaseCheck.HIGH, True, (var,'exists'), msgs))
                results.append(Result(BaseCheck.HIGH, True, (var,'axis'), msgs))
                break
        if no_height:
            return Result(BaseCheck.HIGH, (0,1), ('height_variable','exists'), msgs)
        
       #Check Height Name
        if var in valid_variable_names:
            name_check = True
            results.append(Result(BaseCheck.HIGH, name_check, (var,'valid_height_name'), msgs))
        else:
            msgs = ['The name of the Height Variable is not in the approved vocab list']
            return Result(BaseCheck.HIGH, (0,1), (var,'valid_height_name'), msgs)
       
        #Check Data Type
        valid_types = ['int', 'long', 'double', 'float']
        results.append(var_dtype(dataset, var, valid_types, BaseCheck.HIGH))

        #Check Standard Name
        if getattr(dataset.variables[var], 'standard_name', None) in ['depth','altitude']:
            std_check = True
        else: 
            msgs = ['standard name is wrong']
            std_check = False
        results.append(Result(BaseCheck.HIGH, std_check, (var,'standard_name'), msgs))

        #Check Units
        if getattr(dataset.variables[var], 'units', None) in valid_units:
            units_check = True
        else: 
            msgs = ['units are wrong']
            units_check = False
        results.append(Result(BaseCheck.HIGH, units_check, (var,'units'), msgs))

        #Check has these attributes
        has_var_attr = [
                'ancillary_variables',
                'comment',
                'long_name',
                'valid_min',
                'valid_max'
                #'_FillValue'
                ]

        for attr in has_var_attr:
            results.append(hasattr_check(dataset, var, attr, BaseCheck.MEDIUM))
         
        #Check Positive
        if getattr(dataset.variables[var], 'positive', None) in ['up', 'down']:
            pos_check = True
        else: 
            msgs = ['positive is incorrect']
            pos_check = False
        results.append(Result(BaseCheck.MEDIUM, pos_check, (var,'positive'), msgs))
        return results

################################################################################
# Checks for Science Variables 
################################################################################
    @score_group('Science Variables')
    def check_science(self, dataset):
        '''
                float geophysical_variable_1(time) ;//................................ This is an example of how each and every geophysical variable in the file should be represented. Replace the name of the variable("geophysical_variable_1") with a suitable name. Replace "float" by data type which is appropriate for the variable. 
                geophysical_variable_1:long_name = "" ; //................... RECOMMENDED - Provide a descriptive, long name for this variable. 
                geophysical_variable_1:standard_name = "" ; //............... REQUIRED    - If using a CF standard name and a suitable name exists in the CF standard name table.
                geophysical_variable_1:nodc_name = "" ; //................... RECOMMENDED - From the NODC variables vocabulary, if standard_name does not exist.
                geophysical_variable_1:units = "" ; //....................... REQUIRED    - Use UDUNITS compatible units.
                geophysical_variable_1:scale_factor = 0.0f ; //.............. REQUIRED if the data uses a scale_factor other than 1.The data type should be the data type of the variable.
                geophysical_variable_1:add_offset = 0.0f ; // ............... REQUIRED if the data uses an add_offset other than 0. The data type should be the data type of the variable.
                geophysical_variable_1:_FillValue = 0.0f ; //................ REQUIRED  if there could be missing values in the data.
                geophysical_variable_1:valid_min = 0.0f ; //................. RECOMMENDED - Replace with correct value.
                geophysical_variable_1:valid_max = 0.0f ; //................. RECOMMENDED - Replace with correct value.
                geophysical_variable_1:coordinates = "time lat lon z" ; //... REQUIRED    - Include the auxiliary coordinate variables and optionally coordinate variables in the list. The order itself does not matter. Also, note that whenever any auxiliary coordinate variable contains a missing value, all other coordinate, auxiliary coordinate and data values corresponding to that element should also contain missing values.
                geophysical_variable_1:grid_mapping = "crs" ; //............. RECOMMENDED - It is highly recommended that the data provider put the data in a well known geographic coordinate system and provide the details of the coordinate system.
                geophysical_variable_1:source = "" ; //...................... RECOMMENDED - The method of production of the original data
                geophysical_variable_1:references = "" ; //.................. RECOMMENDED - Published or web-based references that describe the data or methods used to produce it.
                geophysical_variable_1: cell_methods = "" ; // .............. RECOMMENDED - Use the coordinate variables to define the cell values (ex., "time: point lon: point lat: point z: point").
                geophysical_variable_1:ancillary_variables = "instrument_parameter_variable platform_variable boolean_flag_variable enumerated_flag_variable" ; //......... RECOMMENDED - Identify the variable name(s) of the flag(s) and other ancillary variables relevant to this variable.  Use a space-separated list.
                geophysical_variable_1:platform = "platform_variable" ; //... RECOMMENDED - Refers to name of variable containing information on the platform from which this variable was collected.
                geophysical_variable_1:instrument = "instrument_variable";//..RECOMMENDED - Refers to name of variable containing information on the instrument from which this variable was collected.
                geophysical_variable_1:comment = "" ; //..................... RECOMMENDED - Add useful, additional information here.
                '''
        #Check the science variables to ensure they are good
        results = []
        msgs = []
        for name in dataset.variables:
            if hasattr(dataset.variables[name],'coordinates') and not hasattr(dataset.variables[name],'flag_meanings'):
                #This is a science Variable.  Start Checks.
                #Check  has these attributes
                has_var_attr = [
                        #'_FillValue',
                        'valid_min',
                        'valid_max',
                        'ancillary_variables',
                        'comment',
                        'long_name',
                        'units',
                        #'nodc_name',
                        'grid_mapping',
                        'source',
                        'references'
                        ]
                var  = name

                for attr in has_var_attr:
                    results.append(hasattr_check(dataset, var, attr, BaseCheck.MEDIUM))

                #Check NODC Name
                if not hasattr(dataset.variables[name], 'standard_name'):
                    nodc_check = hasattr(dataset.variables[name],'nodc_name')
                    if not nodc_check:
                        msgs = ['{} does not ahve a standard_name or nodc_name field'.format(name)]
                        results.append(Result(BaseCheck.HIGH, nodc_check, (name, 'nodc_name'), msgs))
                    else:
                        results.append(Result(BaseCheck.HIGH, nodc_check, (name, 'nodc_name'), msgs))

                #Check Units
                units = getattr(dataset.variables[name],'units',None)
                units_check = units_known(units)
                if not units_check:
                    msgs.append('Units are wrong for {}'.format(name))
                results.append(Result(BaseCheck.HIGH, units_check, (name,'udunits'),msgs))

                #Check Platform
                level = BaseCheck.MEDIUM
                if not hasattr(dataset.variables[name], 'platform'):
                    plat_check = False
                    level = BaseCheck.LOW
                    msgs = ['platform attribute is missing for {}'.format(name)]
                elif getattr(dataset.variables[name], 'platform', None) in dataset.variables:
                    plat_check = (2,2)
                else:
                    plat_check = (1,2)
                    msgs = ['platform attribute is not present in the variable {}'.format(name)]
                if not hasattr(dataset,'platform'):
                    results.append(Result(level, plat_check, (name,'platform'), msgs))
                msgs = []  
                #Check Instrument
                level = BaseCheck.MEDIUM
                if not hasattr(dataset.variables[name], 'instrument'):
                    inst_check = False
                    level = BaseCheck.LOW
                    msgs = ['instrument attribute is missing for {}'.format(name)]
                elif getattr(dataset.variables[name], 'instrument', None) in dataset.variables:
                    inst_check = (2,2)
                else:
                    inst_check = (1,2)
                    msgs = ['instrument attribute is not present in the variable {}'.format(name)]
                if not hasattr(dataset,'instrument'):
                    results.append(Result(level, inst_check, (name,'instrument'), msgs)) 
             
                #Check  Standard Name
                level = BaseCheck.HIGH
                if not hasattr(dataset.variables[name], 'standard_name'):
                    inst_check = (0,2)
                    msgs = ['standard_name attribute is missing for {}'.format(name)]
                elif getattr(dataset.variables[name], 'standard_name', None) in self._std_names:
                    inst_check = (2,2)
                else:
                    inst_check = (1,2)
                    msgs = ['standard_name is not in standard name table for {}'.format(name)]
                results.append(Result(level, inst_check, (name,'standard_name'), msgs)) 
            else:
                continue
        return results
    
################################################################################
# Checks for QA/QC Variables 
################################################################################
    @score_group('QA/QC Variables')
    def check_qaqc(self, dataset):
        '''
                byte boolean_flag_variable(timeSeries,ntimeMax); //............................. A boolean flag variable, in which each bit of the flag can be a 1 or 0.
                boolean_flag_variable:standard_name= "" ; //................. RECOMMENDED - This attribute should include the standard name of the variable which this flag contributes plus the modifier: "status_flag" (for example, "sea_water_temperature status_flag"). See CF standard name modifiers.
                boolean_flag_variable:long_name = "" ; //.................... RECOMMENDED - Provide a descriptive, long name for this variable. 
                boolean_flag_variable:flag_masks = ; //...................... REQUIRED    - Provide a comma-separated list describing the binary condition of the flags. 
                boolean_flag_variable:flag_meanings = "" ; //................ REQUIRED    - Provide a comma-separated list of flag values that map to the flag_masks.
                boolean_flag_variable:references = "" ; //................... RECOMMENDED - Published or web-based references that describe the data or methods used to produce it.
                boolean_flag_variable:comment = "" ; //...................... RECOMMENDED - Add useful, additional information here.
        int enumerated_flag_variable(timeSeries,ntimeMax);  //...................... An enumerated flag variable, in which numeric values refer to defined, exclusive conditions.
                enumerated_flag_variable:standard_name= "" ; //.............. RECOMMENDED - This attribute should include the standard name of the variable which this flag contributes plus the modifier: "status_flag" (for example, "sea_water_temperature status_flag"). See CF standard name modifiers.
                enumerated_flag_variable:long_name = "" ; //................. RECOMMENDED - Provide a descriptive, long name for this variable. 
                enumerated_flag_variable:flag_values = ; //.................. REQUIRED    - Provide a comma-separated list of flag values that map to the flag_meanings.
                enumerated_flag_variable:flag_meanings = "" ; //............. REQUIRED    - Provide a space-separated list of meanings corresponding to each of the flag_values
                enumerated_flag_variable:references = "" ; //................ RECOMMENDED - Published or web-based references that describe the data or methods used to produce it.
                enumerated_flag_variable:comment = "" ; //................... RECOMMENDED - Add useful, additional information here.
                '''
        #Check the qaqc variables to ensure they are good
        results = []
        msgs = []
        std_name_list = [getattr(dataset.variables[var], 'standard_name', None) for var in dataset.variables]
        for name in dataset.variables:
            if hasattr(dataset.variables[name],'flag_meanings'):
                #Check Standard Name
                std_check = 0
                msgs = []

                std_name = getattr(dataset.variables[name], 'standard_name', 'thereis noname')
                std_name_split = std_name.split(' ')
                if std_name_split[0] in std_name_list:
                    std_check = std_check + 1
                else:
                    msgs.append('Standard Name for {} does not reference a variable in the dataset.'.format(name))
                if std_name_split[1] == 'status_flag':
                    std_check = std_check + 1
                else:
                    msgs.append('Standard Name for {} does not end in "status_flag"'.format(name))
                results.append(Result(BaseCheck.HIGH, (std_check,2), (name,'standard_name'), msgs))

                #Check Flag Mask / Flag Values
                msgs = []
                mask_val_check = False
                test_name = 'flag_masks_values'
                if 'bool' in str(dataset.variables[name].dtype):
                    mask_val_check = hasattr(dataset.variables[name],'flag_masks')
                    test_name = 'flag_masks'
                    mask_length = len(getattr(dataset.variables[name], 'flag_masks', None)) #Used in length check
                elif 'int' in str(dataset.variables[name].dtype):
                    mask_val_check = hasattr(dataset.variables[name], 'flag_values')
                    test_name = 'flag_values'
                    mask_length = len(getattr(dataset.variables[name], 'flag_values', None)) #Used in length check
                else:
                    mask_val_check = False
                    msgs = ['flag_masks or flag_values are not present for {}'.format(name)]
                    mask_length = 0
                results.append(Result(BaseCheck.HIGH, mask_val_check, (name,test_name), msgs))

                #Check Flag Meaning
                msgs = []
                if hasattr(dataset.variables[name],'flag_meanings'):
                    meanings_check = True
                    meaning_length = len(getattr(dataset.variables[name],'flag_meanings',None).split(','))
                else:
                    meanings_check = False
                    msgs = ['flag_meanings not present for {}'.format(name)]
                    meaning_length = 0
                results.append(Result(BaseCheck.HIGH, meanings_check, (name, 'flag_meanings'), msgs))

                #Check Flag Meaning and Flag mask/Values same length
                msgs = []
                if mask_length == meaning_length:
                    length_check = True
                else:
                    length_check = False
                    msgs = ['the length of flag_mask/values does not match flag_meanings for {}'.format(name)]
                results.append(Result(BaseCheck.HIGH, length_check, (name, 'flag_attributes_lengths'), msgs))

                #Check Comment
                msgs = []
                if hasattr(dataset.variables[name], 'comment'):
                    comment_check = True
                else: 
                    msgs = ['comment is missing for {}'.format(name)]
                    comment_check = False
                results.append(Result(BaseCheck.MEDIUM, comment_check, (name,'comment'), msgs))
     
                #Check Long Name
                msgs = []
                if hasattr(dataset.variables[name], 'long_name'):
                    long_check = True
                else: 
                    msgs = ['long_name not present for {}'.format(name)]
                    long_check = False
                results.append(Result(BaseCheck.MEDIUM, long_check, (name,'long_name'), msgs)) 
            
                #Check References
                msgs = []
                if hasattr(dataset.variables[name], 'references'):
                    source_check = True
                else: 
                    msgs = ['references is missing for {}'.format(name)]
                    source_check = False
                results.append(Result(BaseCheck.MEDIUM, source_check, (name,'references'), msgs))

            else:
                continue
        return results

################################################################################
# Checks for Instrument and Platform Variables 
################################################################################
    @score_group('Instruments and Platforms')
    def check_platform(self, dataset):
        '''
                int platform_variable; //............................................ RECOMMENDED - a container variable storing information about the platform. If more than one, can expand each attribute into a variable. For example, platform_call_sign and platform_nodc_code. See instrument_parameter_variable for an example.
                platform_variable:long_name = "" ; //........................ RECOMMENDED - Provide a descriptive, long name for this variable. 
                platform_variable:comment = "" ; //.......................... RECOMMENDED - Add useful, additional information here.
                platform_variable:call_sign = "" ; //........................ RECOMMENDED - This attribute identifies the call sign of the platform. 	 
                platform_variable:nodc_code = ""; //......................... RECOMMENDED - This attribute identifies the NODC code of the platform. Look at http://www.nodc.noaa.gov/cgi-bin/OAS/prd/platform to find if NODC codes are available. 	 
                platform_variable:wmo_code = "";//........................... RECOMMENDED - This attribute identifies the wmo code of the platform. Information on getting WMO codes is available at http://www.wmo.int/pages/prog/amp/mmop/wmo-number-rules.html 	 
                platform_variable:imo_code  = "";//.......................... RECOMMENDED - This attribute identifies the International Maritime Organization (IMO) number assigned by Lloyd's register. 
                '''
        #Check for the platform variable
        platforms = _find_platform_variables(dataset)
        msgs = []
        results = []
        if len(platforms) == 0:
            return Result(BaseCheck.MEDIUM, False, ('platform_var','exists'), ['The platform variables do not exist']) 
        for platform in platforms:
            #Check Platform Var Exists
            if platform not in dataset.variables:
                return Result(BaseCheck.MEDIUM, False, ('platform_var','exists'), ['The platform variables do not exist']) 
            #Check Long Name
            has_var_attr = [
                    'comment',
                    'long_name',
                    'call_sign',
                    'nodc_code',
                    'wmo_code',
                    'imo_code'
                    ]
            var  = platform

            for attr in has_var_attr:
                results.append(hasattr_check(dataset, var, attr, BaseCheck.MEDIUM))
        
        return results

    @score_group('Instruments and Platforms')
    def check_instrument(self, dataset):
        '''
                int instrument_parameter_variable(timeSeries); //.................... RECOMMENDED - an instrument variable storing information about a parameter of the instrument used in the measurement, the dimensions don't have to be specified if the same instrument is used for all the measurements.
                instrument_parameter_variable:long_name = "" ; //............ RECOMMENDED - Provide a descriptive, long name for this variable. 
                instrument_parameter_variable:comment = "" ; //.............. RECOMMENDED - Add useful, additional information here.
                '''
        #Check for the instrument variable
        instruments = _find_instrument_variables(dataset)
        if not instruments:
            return Result(BaseCheck.MEDIUM, False, 'instrument variable exists', ['No instrument variables found'])
        results = []
        for instrument in instruments:
            test_ctx = TestCtx(BaseCheck.MEDIUM, '{} is a proper instrument variable'.format(instrument))
            var = dataset.variables[instrument]
            self.assert_is(test_ctx, getattr(var, 'long_name', '') != '', 'long_name attribute exists and is not empty')
            self.assert_is(test_ctx, getattr(var, 'comment', '') != '', 'comment attribute exists and is not empty')
            results.append(test_ctx.to_result())

        return results


################################################################################
# CF Checks
################################################################################
    @score_group('CRS Variable')
    def check_crs(self, dataset):
        '''
        int crs; //.......................................................... RECOMMENDED - A container variable storing information about the grid_mapping. All the attributes within a grid_mapping variable are described in http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#appendix-grid-mappings. For all the measurements based on WSG84, the default coordinate system used for GPS measurements, the values shown here should be used.
                crs:grid_mapping_name = "latitude_longitude"; //............. RECOMMENDED
                crs:epsg_code = "EPSG:4326" ; //............................. RECOMMENDED - European Petroleum Survey Group code for the grid mapping name.
                crs:semi_major_axis = 6378137.0 ; //......................... RECOMMENDED
                crs:inverse_flattening = 298.257223563 ; //.................. RECOMMENDED
        '''
        crs_variable = _find_crs_variable(dataset)
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Dataset contains valid grid_mapping variable')
        self.assert_is(test_ctx, crs_variable is not None, 'A container variable storing the grid mapping should exist for this dataset.')

        epsg_code = getattr(crs_variable, 'epsg_code', '')
        semi_major_axis = getattr(crs_variable, 'semi_major_axis', None)
        inverse_flattening = getattr(crs_variable, 'inverse_flattening', None)

        self.assert_is(test_ctx,
                       epsg_code != '',
                       'Attribute epsg_code should exist and not be empty: {}'.format(epsg_code))
        self.assert_is(test_ctx,
                       semi_major_axis is not None,
                       'Attribute semi_major_axis should exist and not be empty: {}'.format(epsg_code))
        self.assert_is(test_ctx,
                       inverse_flattening is not None,
                       'Attribute inverse_flattening should exist and not be empty: {}'.format(epsg_code))
        return test_ctx.to_result()

    @score_group('Global Attributes')
    def check_global_attributes(self, dataset):
        '''
        Returns a result that contains the result-values mapped from REQUIRED, RECOMMENDED appropriately based on the following global attributes:

        :title = "" ; //..................................................... RECOMMENDED - Provide a useful title for the data in the file. (ACDD)
        :summary = "" ; //................................................... RECOMMENDED - Provide a useful summary or abstract for the data in the file. (ACDD)
        :source = "" ; //.................................................... RECOMMENDED - The input data sources regardless of the method of production method used. (CF)
        :platform = "platform_variable" ; //................................. RECOMMENDED - Refers to a variable containing information about the platform. May also put this in individual variables. Use NODC or ICES platform table. (NODC)
        :instrument = "instrument_parameter_variable" ; //................... RECOMMENDED - Refers to a variable containing information about the instrument. May also put this in individual variables. Use NODC or GCMD instrument table. (NODC)
        :uuid = "" ; //...................................................... RECOMMENDED - Machine readable unique identifier for each file. A new uuid is created whenever the file is changed. (NODC)
        :sea_name = "" ; //.................................................. RECOMMENDED - The names of the sea in which the data were collected. Use NODC sea names table. (NODC)
        :id = "" ; //........................................................ RECOMMENDED - Should be a human readable unique identifier for data set. (ACDD)
        :naming_authority = "" ; //.......................................... RECOMMENDED - Backward URL of institution (for example, gov.noaa.nodc). (ACDD)
        :time_coverage_start = "" ; //....................................... RECOMMENDED - Use ISO8601 for date and time. (ACDD)
        :time_coverage_end = "" ; //......................................... RECOMMENDED - Use ISO8601 for date and time.(ACDD)
        :time_coverage_resolution = "" ; //.................................. RECOMMENDED - For example, "point" or "minute averages". (ACDD)
        :geospatial_lat_min = 0.0f ; //...................................... RECOMMENDED - Replace with correct value. (ACDD)
        :geospatial_lat_max = 0.0f ; //...................................... RECOMMENDED - Replace with correct value. (ACDD)
        :geospatial_lat_units = "degrees_north" ; //......................... RECOMMENDED - Use UDUNITS compatible units. (ACDD)
        :geospatial_lat_resolution= "" ; //.................................. RECOMMENDED - For example, "point" or "10 degree grid". (ACDD)
        :geospatial_lon_min = 0.0f ; //...................................... RECOMMENDED - Replace with correct value. (ACDD)
        :geospatial_lon_max = 0.0f ; //...................................... RECOMMENDED - Replace with correct value. (ACDD)
        :geospatial_lon_units = "degrees_east"; //........................... RECOMMENDED - Use UDUNITS compatible units. (ACDD)
        :geospatial_lon_resolution= "" ; //.................................. RECOMMENDED - For example, "point" or "10 degree grid". (ACDD)
        :geospatial_vertical_min = 0.0f ; //................................. RECOMMENDED - Replace with correct value. (ACDD)
        :geospatial_vertical_max = 0.0f ; //................................. RECOMMENDED - Replace with correct value. (ACDD)
        :geospatial_vertical_units = "" ; //................................. RECOMMENDED - Use UDUNITS compatible units. (ACDD)
        :geospatial_vertical_resolution = "" ; //............................ RECOMMENDED - For example, "point" or "1 meter binned". (ACDD)
        :geospatial_vertical_positive = "" ; //.............................. RECOMMENDED - Use "up" or "down". (ACDD)
        :institution = "" ; //............................................... RECOMMENDED - Institution of the person or group that collected the data.  An institution attribute can be used for each variable if variables come from more than one institution. (ACDD)
        :creator_name = "" ; //.............................................. RECOMMENDED - Name of the person who collected the data. (ACDD)
        :creator_url = "" ; //............................................... RECOMMENDED - URL for person who collected the data. (ACDD)
        :creator_email = "" ; //............................................. RECOMMENDED - Email address for person who collected the data. (ACDD)
        :project = "" ; //................................................... RECOMMENDED - Project the data was collected under. (ACDD)
        :processing_level = "" ; //.......................................... RECOMMENDED - Provide a description of the processing or quality control level of the data. (ACDD)
        :references = "" ; //................................................ RECOMMENDED - Published or web-based references that describe the data or methods used to produce it. (CF)
        :keywords_vocabulary = "" ; //....................................... RECOMMENDED - Identifies the controlled keyword vocabulary used to specify the values within the attribute "keywords". e.g. NASA/GCMD Earth Science Keywords (ACDD)
        :keywords = "" ; //.................................................. RECOMMENDED - A comma separated list of keywords coming from the keywords_vocabulary. (ACDD)
        :acknowledgment = "" ; //............................................ RECOMMENDED - Text to use to properly acknowledge use of the data. (ACDD)
        :comment = "" ; //................................................... RECOMMENDED - Provide useful additional information here. (ACDD and CF)
        :contributor_name = "" ; //.......................................... RECOMMENDED - A comma separated list of contributors to this data set. (ACDD)
        :contributor_role = "" ; //.......................................... RECOMMENDED - A comma separated list of their roles. (ACDD)
        :date_created = "" ; //.............................................. RECOMMENDED - Creation date of the netCDF.  Use ISO8601 for date and time. (ACDD)
        :date_modified = "" ; //............................................. RECOMMENDED - Modification date of the netCDF.  Use ISO8601 for date and time. (ACDD)
        :publisher_name = "" ; //............................................ RECOMMENDED - Publisher of the data. (ACDD)
        :publisher_email = "" ; //........................................... RECOMMENDED - Email address of the publisher of the data. (ACDD)
        :publisher_url = "" ; //............................................. RECOMMENDED - A URL for the publisher of the data. (ACDD)
        :history = "" ; //................................................... RECOMMENDED - Record changes made to the netCDF. (ACDD)
        :license = "" ; //................................................... RECOMMENDED - Describe the restrictions to data access and distribution. (ACDD)
        :metadata_link = "" ; //............................................. RECOMMENDED - This attribute provides a link to a complete metadata record for this data set or the collection that contains this data set. (ACDD)  
        '''

        should_exist = [
            'title',
            'summary',
            'source',
            'uuid',
            'id',
            'naming_authority',
            'geospatial_lat_min',
            'geospatial_lat_max',
            'geospatial_lat_resolution',
            'geospatial_lon_min',
            'geospatial_lon_max',
            'geospatial_lon_resolution',
            'geospatial_vertical_max',
            'geospatial_vertical_min',
            'geospatial_vertical_units',
            'geospatial_vertical_resolution',
            'institution',
            'creator_name',
            'creator_url',
            'creator_email',
            'project',
            'processing_level',
            'references',
            'keywords_vocabulary',
            'keywords',
            'comment',
            'publisher_name',
            'publisher_email',
            'publisher_url',
            'history',
            'license',
            'metadata_link'
        ]

        results = []
        for attr in should_exist:
            attr_ctx = TestCtx(BaseCheck.MEDIUM, '{} attribute exists'.format(attr))
            self.assert_is(attr_ctx, getattr(dataset, attr, '') != '', '{} exists and is not empty.'.format(attr))
            results.append(attr_ctx.to_result())

        # Do any of the variables define platform ?
        variable_defined_platform = any((hasattr(var, 'platform') for var in dataset.variables))
        if not variable_defined_platform:
            platform_ctx = TestCtx(BaseCheck.MEDIUM, 'platform attribute exists')
            platform_name = getattr(dataset, 'platform', '')
            self.assert_is(platform_ctx, platform_name and platform_name in dataset.variables, 'platform exists and is a variable.')
            results.append(platform_ctx.to_result())

        sea_names = get_sea_names()
        sea_name_ctx = TestCtx(BaseCheck.MEDIUM, 'sea_name attribute exists')
        sea_name = getattr(dataset, 'sea_name', '')
        self.assert_is(sea_name_ctx, sea_name and sea_name in sea_names, 'exists and is from the NODC sea names list')
        results.append(sea_name_ctx.to_result())

        # Source: http://www.pelagodesign.com/blog/2009/05/20/iso-8601-date-validation-that-doesnt-suck/
        iso8601_regex = r'^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$'
        for attr in ['time_coverage_start', 'time_coverage_end', 'date_created', 'date_modified']:
            attr_ctx = TestCtx(BaseCheck.MEDIUM, '{} exists and is ISO-8601'.format(attr))
            attr_value = getattr(dataset, attr, '')
            regex_match = re.match(iso8601_regex, attr_value)
            self.assert_is(attr_ctx, attr_value and regex_match is not None, '{} exists and is ISO-8601 valid string: {}'.format(attr, attr_value))
            results.append(attr_ctx.to_result())

        attr_ctx = TestCtx(BaseCheck.MEDIUM, 'geospatial_lat_units exists and is valid')
        units = getattr(dataset, 'geospatial_lat_units', '').lower()
        self.assert_is(attr_ctx, units == 'degrees_north', 'Units must be degrees_north: {}'.format(units))
        results.append(attr_ctx.to_result())

        attr_ctx = TestCtx(BaseCheck.MEDIUM, 'geospatial_lon_units exists and is valid')
        units = getattr(dataset, 'geospatial_lon_units', '').lower()
        self.assert_is(attr_ctx, units == 'degrees_east', 'Units must be degrees_east: {}'.format(units))
        results.append(attr_ctx.to_result())

        attr_ctx = TestCtx(BaseCheck.MEDIUM, 'geospatial_vertical_positive is either up or down')
        value = getattr(dataset, 'geospatial_vertical_positive', '')
        self.assert_is(attr_ctx, value.lower() in ['up', 'down'], 'value must be either up or down: {}'.format(value))
        results.append(attr_ctx.to_result())

        # I hate english.
        ack_exists = any((getattr(dataset, attr, '') != '' for attr in ['acknowledgment', 'acknowledgement']))
        attr_ctx = TestCtx(BaseCheck.MEDIUM, 'acknowledgment exists')
        self.assert_is(attr_ctx, ack_exists, 'exists and is not empty')
        results.append(attr_ctx.to_result())

        contributor_name = getattr(dataset, 'contributor_name', '')
        contributor_role = getattr(dataset, 'contributor_role', '')
        names = contributor_role.split(',')
        roles = contributor_role.split(',')
        contributors_ctx = TestCtx(BaseCheck.MEDIUM, 'contributor_name exists and is valid')
        self.assert_is(contributors_ctx, contributor_name != '', 'contributor_name exists and is not empty.')
        self.assert_is(contributors_ctx, len(names) == len(roles), 'length of contributor names matches length of roles')
        results.append(contributors_ctx.to_result())
        roles_ctx = TestCtx(BaseCheck.MEDIUM, 'contributor_role exists and is valid')
        self.assert_is(roles_ctx, contributor_role != '', 'contributor_role exists and is not empty.')
        self.assert_is(roles_ctx, len(names) == len(roles), 'length of contributor names matches length of roles')
        results.append(roles_ctx.to_result())

        return results
