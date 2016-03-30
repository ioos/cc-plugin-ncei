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

    @score_group('Required Variables')
    def check_lat(self, dataset):
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

    @score_group('Science Variables')
    def check_science(self, dataset):
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
    
    @score_group('QA/QC Variables')
    def check_qaqc(self, dataset):
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

    @score_group('Instruments and Platforms')
    def check_platform(self, dataset):
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


    @score_group('CRS')
    def check_crs(self, dataset):
        cfbasecheck = CFBaseCheck()
        return CFBaseCheck.check_horz_crs_grid_mappings_projections(cfbasecheck, dataset)

