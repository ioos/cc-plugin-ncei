#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_base.py
'''

from compliance_checker.cf.cf import CFBaseCheck
from compliance_checker.base import Result, BaseCheck, score_group, BaseNCCheck
import cf_units
import numpy as np

def _find_platform_variables(self, ds):
    plat_vars = []
    platform_name = getattr(ds, 'platform', None)
    if platform_name is not None:
        plat_vars.append(platform_name)
        return list(set(plat_vars))

    for k, v in ds.variables.items():
        if 'platform' in k:
            if not v.shape:  # Empty dimension
                plat_vars.append(k)
    return list(set(plat_vars))

def _find_instrument_variables(self, ds):
    inst_vars = []
    instrument_name = getattr(ds, 'instrument', None)
    if instrument_name is not None:
        inst_vars.append(instrument_name)
        return list(set(inst_vars))
    
    for k, v in ds.variables.items():
        if 'instrument' in k:
            if not v.shape:  # Empty dimension
                inst_vars.append(k)
    return list(set(inst_vars))


class NCEIBaseCheck(BaseNCCheck):
    register_checker = True

    @classmethod
    def setup(self, ds):
        pass

    def check_required_attributes(self, dataset):
        '''
        Verifies that the dataset contains the NCEI required and highly recommended global attributes
        '''

        out_of = 4
        score = 0
        messages = []
        
        for attribute in ('title', 'summary', 'keywords', 'Conventions'):
            test = getattr(dataset, attribute, '') != ''

            if test:
                score += 1
            else:
                messages.append('Dataset is missing the global attribute {}'.format(attribute))

        return Result(BaseCheck.HIGH, (score, out_of), 'Dataset contains NCEI required and highly recommended attributes', messages)
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
        #Checks if the lat variable is formed properly
        msgs=[]
        results=[]
        valid_types = ['int', 'long', 'double', 'float']

       #Check 1) lat exist
        if u'lat' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.HIGH, exists_check, ('lat','exists'), msgs))
        else:
            msgs = ['lat does not exist']
            return Result(BaseCheck.HIGH, (0,1), ('lat','exists'), msgs)
       
        #Check 2) Data Type
        data_type = str(dataset.variables[u'lat'].dtype)
        if any(valid_type in data_type for valid_type in valid_types):
            data_check = True
        else:
            msgs = ['data type for lat is invalid']
            data_check = False
        results.append(Result(BaseCheck.HIGH, data_check, ('lat','data_type'), msgs))

        #Check 3) Standard Name
        if getattr(dataset.variables[u'lat'], 'standard_name', None) == 'latitude':
            std_check = True
        else: 
            msgs = ['standard name is wrong']
            std_check = False
        results.append(Result(BaseCheck.HIGH, std_check, ('lat','standard_name'), msgs))

        #Check 4) Units
        if getattr(dataset.variables[u'lat'], 'units', None) == 'degrees_north':
            units_check = True
        else: 
            msgs = ['units are wrong']
            units_check = False
        results.append(Result(BaseCheck.HIGH, units_check, ('lat','units'), msgs))

        #Check 5) Axis
        if getattr(dataset.variables[u'lat'], 'axis', None) == 'Y':
            axis_check = True
        else: 
            msgs = ['axis is wrong']
            axis_check = False
        results.append(Result(BaseCheck.HIGH, axis_check, ('lat','axis'), msgs))

        #Check 6) fill value
        if hasattr(dataset.variables[u'lat'],'_FillValue'):
            fill_check = True
        else: 
            msgs = ['fill value is missing']
            fill_check = False
        results.append(Result(BaseCheck.MEDIUM, fill_check, ('lat','fill_value'), msgs))

        #Check 7) Valid Min
        if hasattr(dataset.variables[u'lat'], 'valid_min'):
            min_check = True
        else: 
            msgs = ['valid min is missing']
            min_check = False
        results.append(Result(BaseCheck.MEDIUM, min_check, ('lat','valid_min'), msgs))

        #Check 8) Valid Max
        if hasattr(dataset.variables[u'lat'], 'valid_max'):
            max_check = True
        else: 
            msgs = ['valid max is missing']
            max_check = False
        results.append(Result(BaseCheck.MEDIUM, max_check, ('lat','valid_max'), msgs))

        #Check 9) Ancillary Variables
        if hasattr(dataset.variables[u'lat'], 'ancillary_variables'):
            anci_check = True
        else: 
            msgs = ['ancillary variables are missing']
            anci_check = False
        results.append(Result(BaseCheck.MEDIUM, anci_check, ('lat','ancillary_variables'), msgs))

        #Check 10) Comment
        if hasattr(dataset.variables[u'lat'], 'comment'):
            comment_check = True
        else: 
            msgs = ['comment is missing']
            comment_check = False
        results.append(Result(BaseCheck.MEDIUM, comment_check, ('lat','comment'), msgs))
        
        #Check 11) Long Name
        if hasattr(dataset.variables[u'lat'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('lat','long_name'), msgs))
        
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
        valid_types = ['int', 'long', 'double', 'float']

        #Check 1) lon exist
        if u'lon' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.HIGH, exists_check, ('lon','exists'), msgs))
        else:
            msgs = ['lon does not exist']
            return Result(BaseCheck.HIGH, (0,1), ('lon','exists'), msgs)

        #Check 2) Data Type
        data_type = str(dataset.variables[u'lon'].dtype)
        if any(valid_type in data_type for valid_type in valid_types):
            data_check = True
        else:
            msgs = ['data type for lon is invalid']
            data_check = False
        results.append(Result(BaseCheck.HIGH, data_check, ('lon','data_type'), msgs))

        #Check 3) Standard Name
        if getattr(dataset.variables[u'lon'], 'standard_name', None) == 'longitude':
            std_check = True
        else: 
            msgs = ['standard name is wrong']
            std_check = False
        results.append(Result(BaseCheck.HIGH, std_check, ('lon','standard_name'), msgs))

        #Check 4) Units
        if getattr(dataset.variables[u'lon'], 'units', None) == 'degrees_east':
            units_check = True
        else: 
            msgs = ['units are wrong']
            units_check = False
        results.append(Result(BaseCheck.HIGH, units_check, ('lon','units'), msgs))

        #Check 5) Axis
        if getattr(dataset.variables[u'lon'], 'axis', None) == 'X':
            axis_check = True
        else: 
            msgs = ['axis is wrong']
            axis_check = False
        results.append(Result(BaseCheck.HIGH, axis_check, ('lon','axis'), msgs))

        #Check 6) fill value
        if hasattr(dataset.variables[u'lon'],'_FillValue'):
            fill_check = True
        else: 
            msgs = ['fill value is missing']
            fill_check = False
        results.append(Result(BaseCheck.MEDIUM, fill_check, ('lon','fill_value'), msgs))

        #Check 7) Valid Min
        if hasattr(dataset.variables[u'lon'], 'valid_min'):
            min_check = True
        else: 
            msgs = ['valid min is missing']
            min_check = False
        results.append(Result(BaseCheck.MEDIUM, min_check, ('lon','valid_min'), msgs))

        #Check 8) Valid Max
        if hasattr(dataset.variables[u'lon'], 'valid_max'):
            max_check = True
        else: 
            msgs = ['valid max is missing']
            max_check = False
        results.append(Result(BaseCheck.MEDIUM, max_check, ('lon','valid_max'), msgs))

        #Check 9) Ancillary Variables
        if hasattr(dataset.variables[u'lon'], 'ancillary_variables'):
            anci_check = True
        else: 
            msgs = ['ancillary variables are missing']
            anci_check = False
        results.append(Result(BaseCheck.MEDIUM, anci_check, ('lon','ancillary_variables'), msgs))

        #Check 10) Comment
        if hasattr(dataset.variables[u'lon'], 'comment'):
            comment_check = True
        else: 
            msgs = ['comment is missing']
            comment_check = False
        results.append(Result(BaseCheck.MEDIUM, comment_check, ('lon','comment'), msgs))
        
        #Check 11) Long Name
        if hasattr(dataset.variables[u'lon'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('lon','long_name'), msgs))
        
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
        valid_types = ['int', 'long', 'double', 'float']

        #Check 1) Time Exist
        if u'time' in dataset.variables:
            exists_check = True
            results.append(Result(BaseCheck.HIGH, exists_check, ('time','exists'), msgs))
        else:
            msgs = ['time does not exist']
            return Result(BaseCheck.HIGH,(0,1) , ('time','exists'), msgs)
        
        #Check 2) Data Type
        data_type = str(dataset.variables[u'time'].dtype)
        if any(valid_type in data_type for valid_type in valid_types):
            data_check = True
        else:
            msgs = ['data type for lon is invalid']
            data_check = False
        results.append(Result(BaseCheck.HIGH, data_check, ('time','data_type'), msgs))
       
        #Check 3) Standard Name
        if getattr(dataset.variables[u'time'], 'standard_name', None) == 'time':
            std_check = True
        else: 
            msgs = ['standard name is wrong']
            std_check = False
        results.append(Result(BaseCheck.HIGH, std_check, ('time','standard_name'), msgs))

        #Check 4) Units
        if 'since' in getattr(dataset.variables[u'time'], 'units', None):
            units_check = True
        else: 
            msgs = ['units are wrong']
            units_check = False
        results.append(Result(BaseCheck.HIGH, units_check, ('time','units'), msgs))

        #Check 5) Axis
        if getattr(dataset.variables[u'time'], 'axis', None) == 'T':
            axis_check = True
        else: 
            msgs = ['axis is wrong']
            axis_check = False
        results.append(Result(BaseCheck.HIGH, axis_check, ('time','axis'), msgs))       
        
        #Check 6) Ancillary Variables
        if hasattr(dataset.variables[u'time'], 'ancillary_variables'):
            anci_check = True
        else: 
            msgs = ['ancillary variables are missing']
            anci_check = False
        results.append(Result(BaseCheck.MEDIUM, anci_check, ('time','ancillary_variables'), msgs))

        #Check 7) Comment
        if hasattr(dataset.variables[u'time'], 'comment'):
            comment_check = True
        else: 
            msgs = ['comment is missing']
            comment_check = False
        results.append(Result(BaseCheck.MEDIUM, comment_check, ('time','comment'), msgs))  
        
        #Check 8) Long Name
        if hasattr(dataset.variables[u'time'], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, ('time','long_name'), msgs))
        
        #Check 9) Calendar
        if hasattr(dataset.variables[u'time'], 'calendar'):
            cal_check = True
        else: 
            msgs = ['calendar is missing (which means gregorian calendar is assumed)']
            cal_check = False
        results.append(Result(BaseCheck.LOW, cal_check, ('time','calendar'), msgs))
        
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
        valid_types = ['int', 'long', 'double', 'float']
        valid_variable_names = ['z','depth','altitude','pressure','height', 'alt']
        valid_units = ['m','meters','meter','metre','metres','km','kilometers','kilometer','bar','millibar','decibar','atm','atmosphere','pascal','Pa','hPa']

        #Check 1) height exists and Check 2) Axis 
        no_height = True
        for name in dataset.variables:
            if getattr(dataset.variables[name],'axis',None) == 'Z':
                no_height = False
                results.append(Result(BaseCheck.HIGH, True, (name,'exists'), msgs))
                results.append(Result(BaseCheck.HIGH, True, (name,'axis'), msgs))
                break
        if no_height:
            return Result(BaseCheck.HIGH, (0,1), ('height_variable','exists'), msgs)

       #Check 3) Height Name
        if name in valid_variable_names:
            name_check = True
            results.append(Result(BaseCheck.HIGH, name_check, (name,'valid_height_name'), msgs))
        else:
            msgs = ['The name of the Height Variable is not in the approved vocab list']
            return Result(BaseCheck.HIGH, (0,1), (name,'valid_height_name'), msgs)
       
        #Check 4) Data Type
        data_type = str(dataset.variables[name].dtype)
        if any(valid_type in data_type for valid_type in valid_types):
            data_check = True
        else:
            msgs = ['data type for lat is invalid']
            data_check = False
        results.append(Result(BaseCheck.HIGH, data_check, (name,'data_type'), msgs))

        #Check 5) Standard Name
        if getattr(dataset.variables[name], 'standard_name', None) in ['depth','altitude']:
            std_check = True
        else: 
            msgs = ['standard name is wrong']
            std_check = False
        results.append(Result(BaseCheck.HIGH, std_check, (name,'standard_name'), msgs))

        #Check 6) Units
        if getattr(dataset.variables[name], 'units', None) in valid_units:
            units_check = True
        else: 
            msgs = ['units are wrong']
            units_check = False
        results.append(Result(BaseCheck.HIGH, units_check, (name,'units'), msgs))

        #Check 7) fill value
        if hasattr(dataset.variables[name],'_FillValue'):
            fill_check = True
        else: 
            msgs = ['fill value is missing']
            fill_check = False
        results.append(Result(BaseCheck.MEDIUM, fill_check, (name,'fill_value'), msgs))

        #Check 8) Valid Min
        if hasattr(dataset.variables[name], 'valid_min'):
            min_check = True
        else: 
            msgs = ['valid min is missing']
            min_check = False
        results.append(Result(BaseCheck.MEDIUM, min_check, (name,'valid_min'), msgs))

        #Check 9) Valid Max
        if hasattr(dataset.variables[name], 'valid_max'):
            max_check = True
        else: 
            msgs = ['valid max is missing']
            max_check = False
        results.append(Result(BaseCheck.MEDIUM, max_check, (name,'valid_max'), msgs))

        #Check 10) Ancillary Variables
        if hasattr(dataset.variables[name], 'ancillary_variables'):
            anci_check = True
        else: 
            msgs = ['ancillary variables are missing']
            anci_check = False
        results.append(Result(BaseCheck.MEDIUM, anci_check, (name,'ancillary_variables'), msgs))

        #Check 11) Comment
        if hasattr(dataset.variables[name], 'comment'):
            comment_check = True
        else: 
            msgs = ['comment is missing']
            comment_check = False
        results.append(Result(BaseCheck.MEDIUM, comment_check, (name,'comment'), msgs))
        
        #Check 12) Long Name
        if hasattr(dataset.variables[name], 'long_name'):
            long_check = True
        else: 
            msgs = ['long name is missing']
            long_check = False
        results.append(Result(BaseCheck.MEDIUM, long_check, (name,'long_name'), msgs))
        
        #Check 13) Positive
        if getattr(dataset.variables[name], 'positive', None) in ['up', 'down']:
            pos_check = True
        else: 
            msgs = ['positive is incorrect']
            pos_check = False
        results.append(Result(BaseCheck.MEDIUM, pos_check, (name,'positive'), msgs))
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
                #Check 1) Units
                if hasattr(dataset.variables[name], 'units'):
                    units_check = True
                else: 
                    msgs = ['units do not exist']
                    units_check = False
                results.append(Result(BaseCheck.HIGH, units_check, (name,'units'), msgs))

                #Check 2) fill value
                if hasattr(dataset.variables[name],'_FillValue'):
                    fill_check = True
                else: 
                    msgs = ['fill value is missing']
                    fill_check = False
                results.append(Result(BaseCheck.MEDIUM, fill_check, (name,'fill_value'), msgs))

                #Check 3) Valid Min
                if hasattr(dataset.variables[name], 'valid_min'):
                    min_check = True
                else: 
                    msgs = ['valid min is missing']
                    min_check = False
                results.append(Result(BaseCheck.MEDIUM, min_check, (name,'valid_min'), msgs))

                #Check 4) Valid Max
                if hasattr(dataset.variables[name], 'valid_max'):
                    max_check = True
                else: 
                    msgs = ['valid max is missing']
                    max_check = False
                results.append(Result(BaseCheck.MEDIUM, max_check, (name,'valid_max'), msgs))

                #Check 5) Ancillary Variables
                if hasattr(dataset.variables[name], 'ancillary_variables'):
                    anci_check = True
                else: 
                    msgs = ['ancillary variables are missing']
                    anci_check = False
                results.append(Result(BaseCheck.MEDIUM, anci_check, (name,'ancillary_variables'), msgs))

                #Check 6) Comment
                if hasattr(dataset.variables[name], 'comment'):
                    comment_check = True
                else: 
                    msgs = ['comment is missing']
                    comment_check = False
                results.append(Result(BaseCheck.MEDIUM, comment_check, (name,'comment'), msgs))
     
                #Check 7) Long Name
                if hasattr(dataset.variables[name], 'long_name'):
                    long_check = True
                else: 
                    msgs = ['long_name not present']
                    long_check = False
                results.append(Result(BaseCheck.MEDIUM, long_check, (name,'long_name'), msgs)) 
            
                #Check 8) NODC Name
                if hasattr(dataset.variables[name], 'nodc_name'):
                    nodc_check = True
                else: 
                    msgs = ['nodc_name not present']
                    nodc_check = False
                results.append(Result(BaseCheck.MEDIUM, nodc_check, (name,'nodc_name'), msgs))
             
                #Check 9) scale_factor
                level = BaseCheck.MEDIUM
                if hasattr(dataset.variables[name], 'scale_factor'):
                    scale_check = (1,2)
                    msgs = ['scale_factor exists, but the dtype is not the same as the data']
                else: 
                    msgs = ['scale_factor not present']
                    scale_check = False
                    level = BaseCheck.LOW
                try:
                    if dataset.variables[name].dtype == getattr(dataset.variables[name],'scale_factor',None).dtype:
                        scale_check = (2,2)
                        msgs = []
                except:
                    error_reached = True
                results.append(Result(level, scale_check, (name,'scale_factor'), msgs))

                 #Check 10) offset
                level = BaseCheck.MEDIUM
                if hasattr(dataset.variables[name], 'add_offset'):
                    msgs = ['add_offset present, but the dtype is not the same as the data']
                    offset_check = (1,2)
                else: 
                    msgs = ['scale_factor not present']
                    offset_check = False
                    level = BaseCheck.LOW
                try:
                    if dataset.variables[name].dtype == getattr(dataset.variables[name],'add_offset',None).dtype:
                        offset_check = (2,2)
                        msgs = []
                except: 
                    error_reached = True
                results.append(Result(level, offset_check, (name,'add_offset'), msgs))
 
                #Check 11) Grid Mapping
                if hasattr(dataset.variables[name], 'grid_mapping'):
                    map_check = True
                else: 
                    msgs = ['grid_mapping is missing']
                    map_check = False
                results.append(Result(BaseCheck.MEDIUM, map_check, (name,'grid_mapping'), msgs))

                #Check 12) Source
                if hasattr(dataset.variables[name], 'source'):
                    source_check = True
                else: 
                    msgs = ['source is missing']
                    source_check = False
                results.append(Result(BaseCheck.MEDIUM, source_check, (name,'source'), msgs))

                #Check 13) Reference
                if hasattr(dataset.variables[name], 'reference'):
                    source_check = True
                else: 
                    msgs = ['reference is missing']
                    source_check = False
                results.append(Result(BaseCheck.MEDIUM, source_check, (name,'reference'), msgs))

                #Check 14) Platform
                level = BaseCheck.MEDIUM
                if not hasattr(dataset.variables[name], 'platform'):
                    plat_check = False
                    level = BaseCheck.LOW
                    msgs = ['platform attribute is missing']
                elif getattr(dataset.variables[name], 'platform', None) in dataset.variables:
                    plat_check = (2,2)
                else:
                    plat_check = (1,2)
                    msgs = ['platform attribute is not present in the variables']
                results.append(Result(level, plat_check, (name,'platform'), msgs))
                    
                #Check 15) Instrument
                level = BaseCheck.MEDIUM
                if not hasattr(dataset.variables[name], 'instrument'):
                    inst_check = False
                    level = BaseCheck.LOW
                    msgs = ['instrument attribute is missing']
                elif getattr(dataset.variables[name], 'instrument', None) in dataset.variables:
                    inst_check = (2,2)
                else:
                    inst_check = (1,2)
                    msgs = ['instrument attribute is not present in the variables']
                results.append(Result(level, inst_check, (name,'instrument'), msgs)) 
            
            
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
        for name in dataset.variables:
            if hasattr(dataset.variables[name],'flag_meanings'):
                #Check 1) Standard Name
                std_check = 0
                msgs = []

                std_name = getattr(dataset.variables[name], 'flag_meanings',None)
                std_name_split = std_name.split(' ')
                if std_name_split[0] in dataset.variables:
                    std_check = std_check + 1
                else:
                    msgs.append('Standard Name does not reference a variable in the dataset.')
                if std_name_split[1] == 'status_flag':
                    std_check = std_check + 1
                else:
                    msgs.append('Standard Name does not end in "status_flag"')
                results.append(Result(BaseCheck.HIGH, (std_check,2), (name,'standard_name'), msgs))

                #Check 2) Flag Mask / Flag Values
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
                    msgs = ['flag_masks or flag_values are not present']
                    mask_length = 0
                results.append(Result(BaseCheck.HIGH, mask_val_check, (name,test_name), msgs))

                #Check 3) Flag Meaning
                if hasattr(dataset.variables[name],'flag_meanings'):
                    meanings_check = True
                    meaning_length = len(getattr(dataset.variables[name],'flag_meanings',None))
                else:
                    meanings_check = False
                    msgs = ['flag_meanings not present']
                    meaning_length = 0
                results.append(Result(BaseCheck.HIGH, meanings_check, (name, 'flag_meanings'), msgs))

                #Check 4) Flag Meaning and Flag mask/Values same length
                if mask_length == meaning_length:
                    length_check = True
                    msgs = []
                else:
                    length_check = False
                    msgs = ['the length of flag_mask/values does not match flag_meanings']
                results.append(Result(BaseCheck.HIGH, length_check, (name, 'flag_attributes_lengths'), msgs))

                #Check 5) Comment
                if hasattr(dataset.variables[name], 'comment'):
                    comment_check = True
                else: 
                    msgs = ['comment is missing']
                    comment_check = False
                results.append(Result(BaseCheck.MEDIUM, comment_check, (name,'comment'), msgs))
     
                #Check 6) Long Name
                if hasattr(dataset.variables[name], 'long_name'):
                    long_check = True
                else: 
                    msgs = ['long_name not present']
                    long_check = False
                results.append(Result(BaseCheck.MEDIUM, long_check, (name,'long_name'), msgs)) 
            
                #Check 7) References
                if hasattr(dataset.variables[name], 'reference'):
                    source_check = True
                else: 
                    msgs = ['reference is missing']
                    source_check = False
                results.append(Result(BaseCheck.MEDIUM, source_check, (name,'reference'), msgs))

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
        platforms = _find_platform_variables(self, dataset)
        msgs = []
        results = []
        if len(platforms) == 0:
            return Result(BaseCheck.MEDIUM, False, ('platform_var','exists'), ['The platform variables do not exist']) 
        for platform in platforms:
            #Check 1) Platform Var Exists
            if platform not in dataset.variables:
                return Result(BaseCheck.MEDIUM, False, ('platform_var','exists'), ['The platform variables do not exist']) 
            #Check 2) Long Name
            if hasattr(dataset.variables[platform], 'long_name'):
                long_check = True
            else: 
                msgs = ['long_name not present']
                long_check = False
            results.append(Result(BaseCheck.MEDIUM, long_check, (platform,'long_name'), msgs)) 

            #Check 3) Comment
            if hasattr(dataset.variables[platform], 'comment'):
                comment_check = True
            else: 
                msgs = ['comment not present']
                comment_check = False
            results.append(Result(BaseCheck.MEDIUM, comment_check, (platform,'comment'), msgs)) 
            
            #Check 4) Call Sign
            if hasattr(dataset.variables[platform], 'call_sign'):
                call_check = True
            else: 
                msgs = ['call_sign not present']
                call_check = False
            results.append(Result(BaseCheck.MEDIUM, call_check, (platform,'call_sign'), msgs)) 
            
            #Check 5) NODC Code
            if hasattr(dataset.variables[platform], 'nodc_code'):
                nodc_check = True
            else: 
                msgs = ['nodc_code not present']
                nodc_check = False
            results.append(Result(BaseCheck.MEDIUM, nodc_check, (platform,'nodc_code'), msgs)) 
            
            #Check 6) WMO Code
            if hasattr(dataset.variables[platform], 'wmo_code'):
                wmo_check = True
            else: 
                msgs = ['wmo_code not present']
                wmo_check = False
            results.append(Result(BaseCheck.MEDIUM, wmo_check, (platform,'wmo_code'), msgs)) 
            
            #Check 7) IMO Code
            if hasattr(dataset.variables[platform], 'imo_code'):
                imo_check = True
            else: 
                msgs = ['imo_code not present']
                imo_check = False
            results.append(Result(BaseCheck.MEDIUM, imo_check, (platform,'imo_code'), msgs)) 
        return results

    @score_group('Instruments and Platforms')
    def check_instrument(self, dataset):
        '''
                int instrument_parameter_variable(timeSeries); //.................... RECOMMENDED - an instrument variable storing information about a parameter of the instrument used in the measurement, the dimensions don't have to be specified if the same instrument is used for all the measurements.
                instrument_parameter_variable:long_name = "" ; //............ RECOMMENDED - Provide a descriptive, long name for this variable. 
                instrument_parameter_variable:comment = "" ; //.............. RECOMMENDED - Add useful, additional information here.
                '''
        #Check for the instrument variable
        instruments = _find_instrument_variables(self, dataset)
        msgs = []
        results = []
        var = dataset.variables
        instrument_bypass = all(hasattr(var[name],'instrument') for name in dataset.variables if hasattr(var[name], 'coordinates') and not hasattr(var[name],'flag_meanings'))
        if instrument_bypass:
            return Result(BaseCheck.MEDIUM, instrument_bypass, ('instrument_var', 'in_each_variable'), ['Instrument check passes because each variable has information about their isntrument'])
        
        if len(instruments) == 0:
            return Result(BaseCheck.MEDIUM, False, ('instrument_var','exists'), ['The instrument variables do not exist']) 
        
        for instrument in instruments:
            #Check 1) Instrument Var Exists
            if instrument not in dataset.variables:
                return Result(BaseCheck.MEDIUM, False, ('instrument_var','exists'), ['The instrument variables do not exist']) 
            #Check 2) Long Name
            if hasattr(dataset.variables[instrument], 'long_name'):
                long_check = True
            else: 
                msgs = ['long_name not present']
                long_check = False
            results.append(Result(BaseCheck.MEDIUM, long_check, (instrument,'long_name'), msgs)) 

            #Check 3) Comment
            if hasattr(dataset.variables[instrument], 'comment'):
                comment_check = True
            else: 
                msgs = ['comment not present']
                comment_check = False
            results.append(Result(BaseCheck.MEDIUM, comment_check, (instrument,'comment'), msgs)) 
        
        
        return results


################################################################################
# Check for CRS Variable (Uses CF Checker) 
################################################################################
    @score_group('CRS')
    def check_crs(self, dataset):
        '''        
        int crs; //.......................................................... RECOMMENDED - A container variable storing information about the grid_mapping. All the attributes within a grid_mapping variable are described in http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#appendix-grid-mappings. For all the measurements based on WSG84, the default coordinate system used for GPS measurements, the values shown here should be used.
                crs:grid_mapping_name = "latitude_longitude"; //............. RECOMMENDED
                crs:epsg_code = "EPSG:4326" ; //............................. RECOMMENDED - European Petroleum Survey Group code for the grid mapping name.
                crs:semi_major_axis = 6378137.0 ; //......................... RECOMMENDED
                crs:inverse_flattening = 298.257223563 ; //.................. RECOMMENDED
                '''
        cfbasecheck = CFBaseCheck()
        return CFBaseCheck.check_horz_crs_grid_mappings_projections(cfbasecheck, dataset)

