#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/ncei_base.py
'''
from __future__ import print_function

from compliance_checker.base import Result, BaseCheck, BaseNCCheck
from compliance_checker.cf.util import StandardNameTable, units_convertible
from cc_plugin_ncei import util
from cf_units import Unit
from isodate import parse_datetime, ISO8601Error
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

    def assert_true(self, test, message):
        '''
        Increments score if test is true otherwise appends a message
        '''
        self.out_of += 1

        if test:
            self.score += 1
        else:
            self.messages.append(message)


class BaseNCEICheck(BaseNCCheck):
    register_checker = True

    @classmethod
    def __init__(self):
        self._std_names = StandardNameTable('cf-standard-name-table.xml')
        self.high_rec_atts = []
        self.rec_atts  = [
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
            'publisher_name',
            'publisher_email',
            'publisher_url',
            'history',
            'license',
            'metadata_link'
        ]
        self.sug_atts = []

    def setup(self, ds):
        pass

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

        results = []
        lat = util.get_lat_variable(dataset)
        if not lat:
            return Result(BaseCheck.HIGH, False, 'latitude', ['a variable for latitude doesn\'t exist'])
        lat_var = dataset.variables[lat]
        test_ctx = TestCtx(BaseCheck.HIGH, 'Required attributes for variable {}'.format(lat))
        test_ctx.assert_true(getattr(lat_var, 'standard_name', '') == 'latitude', 'standard_name attribute must be latitude')
        units = getattr(lat_var, 'units', '')
        test_ctx.assert_true(units and units_convertible(units, 'degrees_north'), 'units are valid UDUNITS for latitude')
        test_ctx.assert_true(getattr(lat_var, 'axis', '') == 'Y', '{} axis attribute must be Y'.format(lat))

        results.append(test_ctx.to_result())

        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for variable {}'.format(lat))
        test_ctx.assert_true(getattr(lat_var, 'long_name', '') != '', 'long_name attribute should exist and not be empty')
        test_ctx.assert_true(getattr(lat_var, 'valid_min', '') != '', 'valid_min attribute should exist and not be empty')
        test_ctx.assert_true(getattr(lat_var, 'valid_max', '') != '', 'valid_max attribute should exist and not be empty')
        if hasattr(lat_var, 'comment'):
            test_ctx.assert_true(getattr(lat_var, 'comment', '') != '', 'comment attribute should not be empty if specified')
        test_ctx.assert_true(getattr(lat_var, 'comment', '') != '', 'comment attribute should exist and not be empty')
        test_ctx.assert_true(units == 'degrees_north', '{} should have units degrees_north'.format(lat))
        results.append(test_ctx.to_result())
        return results

    def check_lon(self, dataset):
        '''
        float lon(timeSeries) ; //........................................ Depending on the precision used for the variable, the data type could be int or double instead of float.
            lon:long_name = "" ; //...................................... RECOMMENDED
            lon:standard_name = "longitude" ; //......................... REQUIRED    - This is fixed, do not change.
            lon:units = "degrees_east" ; //.............................. REQUIRED    - CF recommends degrees_east, but at least use UDUNITS.
            lon:axis = "X" ; //.......................................... REQUIRED    - Do not change.
            lon:valid_min = 0.0f ; //.................................... RECOMMENDED - Replace this with correct value.
            lon:valid_max = 0.0f ; //.................................... RECOMMENDED - Replace this with correct value.
            lon:_FillValue = 0.0f;//..................................... REQUIRED  if there could be missing values in the data.
            lon:ancillary_variables = "" ; //............................ RECOMMENDED - List other variables providing information about this variable.
            lon:comment = "" ; //........................................ RECOMMENDED - Add useful, additional information here.
        '''
        results = []
        lon = util.get_lon_variable(dataset)
        if not lon:
            return Result(BaseCheck.HIGH, False, 'longitude', ['a variable for longitude doesn\'t exist'])
        lon_var = dataset.variables[lon]
        test_ctx = TestCtx(BaseCheck.HIGH, 'Required attributes for variable {}'.format(lon))
        test_ctx.assert_true(getattr(lon_var, 'standard_name', '') == 'longitude', 'standard_name attribute must be longitude')
        units = getattr(lon_var, 'units', '')
        test_ctx.assert_true(units and units_convertible(units, 'degrees_east'), 'units are valid UDUNITS for longitude')
        test_ctx.assert_true(getattr(lon_var, 'axis', '') == 'X', '{} axis attribute must be X'.format(lon))

        results.append(test_ctx.to_result())

        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for variable {}'.format(lon))
        test_ctx.assert_true(getattr(lon_var, 'long_name', '') != '', 'long_name attribute should exist and not be empty')
        test_ctx.assert_true(getattr(lon_var, 'valid_min', '') != '', 'valid_min attribute should exist and not be empty')
        test_ctx.assert_true(getattr(lon_var, 'valid_max', '') != '', 'valid_max attribute should exist and not be empty')

        if hasattr(lon_var, 'comment'):
            test_ctx.assert_true(getattr(lon_var, 'comment', '') != '', 'comment attribute should not be empty if specified')
        test_ctx.assert_true(units == 'degrees_east', '{} should have units degrees_east'.format(lon))
        results.append(test_ctx.to_result())
        return results

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
        results = []
        time_var = util.get_time_variable(dataset)
        if not time_var:
            return Result(BaseCheck.HIGH, False, 'Coordinate variable time', ['Time coordinate variable was not found'])
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required attributes for variable time')
        required_ctx.assert_true(getattr(dataset.variables[time_var], 'standard_name', '') == 'time', 'standard_name is "time"')
        time_regex = r'(seconds|minutes|hours|days) since.*'
        time_units = getattr(dataset.variables[time_var], 'units', '')
        required_ctx.assert_true(re.match(time_regex, time_units) is not None, 'Valid units for time')
        calendar = getattr(dataset.variables[time_var], 'calendar', '')
        valid_calendars = [
            'standard',
            'gregorian',
            'proleptic_gregorian',
            'noleap',
            '365_day',
            '360_day',
            'julian',
            'all_leap',
            '366_day'
        ]

        if calendar:
            required_ctx.assert_true(calendar.lower() in valid_calendars, 'calendar attribute should be a valid calendar in ({})'.format(', '.join(valid_calendars)))

        results.append(required_ctx.to_result())
        recommended_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for variable time')
        recommended_ctx.assert_true(getattr(dataset.variables[time_var], 'long_name', '') != '', 'long_name attribute should exist and not be empty')
        if hasattr(dataset.variables[time_var], 'comment'):
            recommended_ctx.assert_true(getattr(dataset.variables[time_var], 'comment', '') != '', 'comment attribute should not be empty if specified')
        results.append(recommended_ctx.to_result())

        return results

    def check_height(self, dataset):
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
        results = []

        exists_ctx = TestCtx(BaseCheck.HIGH, 'Variable for height must exist')
        var = util.get_z_variable(dataset)
        exists_ctx.assert_true(var is not None, "A variable for height must exist")
        if var is None:
            return exists_ctx.to_result()

        # Check Height Name
        required_ctx = TestCtx(BaseCheck.HIGH, 'Required attributes for variable {}'.format(var))

        # Check Standard Name
        standard_name = getattr(dataset.variables[var], 'standard_name', '')
        required_ctx.assert_true(
            standard_name in ('depth', 'height', 'altitude'),
            '{} is not a valid standard_name for height'.format(standard_name)
        )

        axis = getattr(dataset.variables[var], 'axis', '')
        required_ctx.assert_true(
            axis == 'Z',
            '{} must have an axis of Z'.format(var)
        )

        # Check Units
        valid_units = False
        units = getattr(dataset.variables[var], 'units', '1')
        try:
            # If cf_units fails to read the units, then it's not a valid unit
            Unit(units)
            valid_units = True
        except:
            pass
        required_ctx.assert_true(valid_units, '{} are not valid units for height'.format(units))

        positive = getattr(dataset.variables[var], 'positive', '')
        required_ctx.assert_true(positive in ('up', 'down'), 'height must have a positive attribute that is equal to "up" or "down"')
        results.append(required_ctx.to_result())

        # Check has these attributes
        # We ommit checking ancillary_variables because that only applies if this variable HAS ancillary variables
        recommended_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for coordinate variable {}'.format(var))
        recommended_attrs = [
            'valid_min',
            'valid_max'
        ]

        for attr in recommended_attrs:
            varattr = getattr(dataset.variables[var], attr, '')
            recommended_ctx.assert_true(varattr != '', 'it is recommended for height to have a {} attribute and it not be empty'.format(attr))

        if hasattr(dataset.variables[var], 'comment'):
            recommended_ctx.assert_true(getattr(dataset.variables[var], 'comment', '') != '', 'comment attribute should not be empty if specified')

        results.append(recommended_ctx.to_result())
        return results

    def check_qaqc(self, dataset):
        '''
        byte boolean_flag_variable(timeSeries,time); //............................. A boolean flag variable, in which each bit of the flag can be a 1 or 0.
                boolean_flag_variable:standard_name= "" ; //................. RECOMMENDED - This attribute should include the standard name of the variable which this flag contributes plus the modifier: "status_flag" (for example, "sea_water_temperature status_flag"). See CF standard name modifiers.
                boolean_flag_variable:long_name = "" ; //.................... RECOMMENDED - Provide a descriptive, long name for this variable.
                boolean_flag_variable:flag_masks = ; //...................... REQUIRED    - Provide a comma-separated list describing the binary condition of the flags.
                boolean_flag_variable:flag_meanings = "" ; //................ REQUIRED    - Provide a comma-separated list of flag values that map to the flag_masks.
                boolean_flag_variable:references = "" ; //................... RECOMMENDED - Published or web-based references that describe the data or methods used to produce it.
                boolean_flag_variable:comment = "" ; //...................... RECOMMENDED - Add useful, additional information here.
        int enumerated_flag_variable(timeSeries,time);  //...................... An enumerated flag variable, in which numeric values refer to defined, exclusive conditions.
                enumerated_flag_variable:standard_name= "" ; //.............. RECOMMENDED - This attribute should include the standard name of the variable which this flag contributes plus the modifier: "status_flag" (for example, "sea_water_temperature status_flag"). See CF standard name modifiers.
                enumerated_flag_variable:long_name = "" ; //................. RECOMMENDED - Provide a descriptive, long name for this variable.
                enumerated_flag_variable:flag_values = ; //.................. REQUIRED    - Provide a comma-separated list of flag values that map to the flag_meanings.
                enumerated_flag_variable:flag_meanings = "" ; //............. REQUIRED    - Provide a space-separated list of meanings corresponding to each of the flag_values
                enumerated_flag_variable:references = "" ; //................ RECOMMENDED - Published or web-based references that describe the data or methods used to produce it.
                enumerated_flag_variable:comment = "" ; //................... RECOMMENDED - Add useful, additional information here.
        '''
        # Check the qaqc variables to ensure they are good
        results = []

        flag_variables = dataset.get_variables_by_attributes(flag_meanings=lambda x: x is not None)
        for flag_variable in flag_variables:
            required_ctx = TestCtx(BaseCheck.HIGH, 'Required attributes for flag variable {}'.format(flag_variable.name))
            flag_values = getattr(flag_variable, 'flag_values', None)
            flag_masks = getattr(flag_variable, 'flag_masks', None)
            required_ctx.assert_true(flag_values is not None or flag_masks is not None, 'flag variable must define either flag_values or flag_masks')
            results.append(required_ctx.to_result())

            recommended_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for flag variable {}'.format(flag_variable.name))
            standard_name = getattr(flag_variable, 'standard_name', '')
            recommended_ctx.assert_true(standard_name.endswith(' status_flag'), 'The standard_name attribute should end with status_flag')

            varattr = getattr(flag_variable, 'long_name', '')
            recommended_ctx.assert_true(varattr != '', 'The {} attribute should exist and not be empty'.format('long_name'))

            if hasattr(flag_variable, 'comment'):
                recommended_ctx.assert_true(getattr(flag_variable, 'comment', '') != '', 'comment attribute should not be empty if specified')

            results.append(recommended_ctx.to_result())
        return results

    def check_instrument(self, dataset):
        '''
        int instrument_parameter_variable(timeSeries); // ... RECOMMENDED - an instrument variable storing information about a parameter of the instrument used in the measurement, the dimensions don't have to be specified if the same instrument is used for all the measurements.
            instrument_parameter_variable:long_name = "" ; // RECOMMENDED - Provide a descriptive, long name for this variable.
            instrument_parameter_variable:comment = "" ; //.. RECOMMENDED - Add useful, additional information here.
        '''
        # Check for the instrument variable
        instruments = util.get_instrument_variables(dataset)
        if not instruments:
            return Result(BaseCheck.MEDIUM, False, 'Recommended variable for instrument should exist', ['No instrument variables found'])
        results = []
        for instrument in instruments:
            test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for instrument variable {}'.format(instrument))
            var = dataset.variables[instrument]
            test_ctx.assert_true(getattr(var, 'long_name', '') != '', 'long_name attribute should exist and not be empty')

            if hasattr(var, 'comment'):
                test_ctx.assert_true(getattr(var, 'comment', '') != '', 'comment attribute should not be empty if specified')

            results.append(test_ctx.to_result())

        return results

    def check_crs(self, dataset):
        '''
        int crs; //.......................................................... RECOMMENDED - A container variable storing information about the grid_mapping. All the attributes within a grid_mapping variable are described in http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#appendix-grid-mappings. For all the measurements based on WSG84, the default coordinate system used for GPS measurements, the values shown here should be used.
                crs:grid_mapping_name = "latitude_longitude"; //............. RECOMMENDED
                crs:epsg_code = "EPSG:4326" ; //............................. RECOMMENDED - European Petroleum Survey Group code for the grid mapping name.
                crs:semi_major_axis = 6378137.0 ; //......................... RECOMMENDED
                crs:inverse_flattening = 298.257223563 ; //.................. RECOMMENDED
        '''
        grid_mapping = util.get_crs_variable(dataset)
        if grid_mapping is None:
            return Result(
                BaseCheck.MEDIUM,
                False,
                'Recommended variable for grid mapping should exist',
                ['A variable to describe the grid mapping should exist']
            )
        crs_variable = dataset.variables[grid_mapping]
        test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for grid mapping variable {}'.format(crs_variable.name))
        test_ctx.assert_true(crs_variable is not None, 'A container variable storing the grid mapping should exist for this dataset.')

        epsg_code = getattr(crs_variable, 'epsg_code', '')
        semi_major_axis = getattr(crs_variable, 'semi_major_axis', None)
        inverse_flattening = getattr(crs_variable, 'inverse_flattening', None)

        test_ctx.assert_true(epsg_code != '',
                             'Attribute epsg_code should exist and not be empty: {}'.format(epsg_code))
        test_ctx.assert_true(semi_major_axis is not None,
                             'Attribute semi_major_axis should exist and not be empty: {}'.format(epsg_code))
        test_ctx.assert_true(inverse_flattening is not None,
                             'Attribute inverse_flattening should exist and not be empty: {}'.format(epsg_code))
        return test_ctx.to_result()

    def check_high(self, ds):
        highly_recommended = TestCtx(BaseCheck.HIGH, 'Highly Recommended global attributes')
        for attr in self.high_rec_atts:
            highly_recommended.assert_true(getattr(ds, attr, '') != '', '{} should exist and not be empty.'.format(attr))
        return highly_recommended.to_result()

    def check_recommended(self, ds):
        recommended_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended global attributes')
        for attr in self.rec_atts:
            recommended_ctx.assert_true(getattr(ds, attr, '') != '', '{} should exist and not be empty.'.format(attr))
        return recommended_ctx.to_result()

    def check_suggested(self, ds):
        suggested_ctx = TestCtx(BaseCheck.LOW, 'Suggested global attributes')
        for attr in self.sug_atts:
            suggested_ctx.assert_true(getattr(ds, attr, '') != '', '{} should exist and not be empty.'.format(attr))
        return suggested_ctx.to_result()


class NCEI1_1Check(BaseNCEICheck):
    def __init__(self):
        super(NCEI1_1Check, self).__init__()

    def check_base_required_attributes(self, dataset):
        '''
        Check the global required and highly recommended attributes for 1.1 templates. These go an extra step besides
        just checking that they exist.

        :param netCDF4.Dataset dataset: An open netCDF dataset


        :Conventions = "CF-1.6" ; //......................................... REQUIRED    - Always try to use latest value. (CF)
        :Metadata_Conventions = "Unidata Dataset Discovery v1.0" ; //........ REQUIRED    - Do not change. (ACDD)
        :featureType = "timeSeries" ; //..................................... REQUIRED - CF attribute for identifying the featureType.
        :cdm_data_type = "Station" ; //...................................... REQUIRED (ACDD)
        :nodc_template_version = "NODC_NetCDF_TimeSeries_Orthogonal_Template_v1.1" ; //....... REQUIRED (NODC)
        :standard_name_vocabulary = "NetCDF Climate and Forecast (CF) Metadata Convention Standard Name Table "X"" ; //........ REQUIRED    - If using CF standard name attribute for variables. "X" denotes the table number  (ACDD)
        '''
        test_ctx = TestCtx(BaseCheck.HIGH, 'Required global attributes')

        conventions = getattr(dataset, 'Conventions', '')
        metadata_conventions = getattr(dataset, 'Metadata_Conventions', '')
        feature_type = getattr(dataset, 'featureType', '')
        cdm_data_type = getattr(dataset, 'cdm_data_type', '')
        standard_name_vocab = getattr(dataset, 'standard_name_vocabulary', '')

        accepted_conventions = 'CF-1.6'

        test_ctx.assert_true(conventions == accepted_conventions,
                             'Conventions attribute is missing or is not equal to CF-1.6: {}'.format(conventions))
        test_ctx.assert_true(metadata_conventions == 'Unidata Dataset Discovery v1.0',
                             "Metadata_Conventions attribute is required to be 'Unidata Dataset Discovery v1.0': {}".format(metadata_conventions))
        test_ctx.assert_true(feature_type in ['point', 'timeSeries', 'trajectory', 'profile', 'timeSeriesProfile', 'trajectoryProfile'],
                             'Feature type must be one of point, timeSeries, trajectory, profile, timeSeriesProfile, trajectoryProfile: {}'.format(feature_type))
        test_ctx.assert_true(cdm_data_type.lower() in ['grid', 'image', 'point', 'radial', 'station', 'swath', 'trajectory'],
                             'cdm_data_type must be one of Grid, Image, Point, Radial, Station, Swath, Trajectory: {}'.format(cdm_data_type))

        regex = re.compile(r'[sS]tandard [nN]ame [tT]able')
        test_ctx.assert_true(regex.search(standard_name_vocab),
                             "standard_name_vocabulary doesn't contain 'Standard Name Table': {}".format(standard_name_vocab))

        return test_ctx.to_result()

    def check_recommended_global_attributes(self, dataset):
        '''
        Check the global recommended attributes for 1.1 templates. These go an extra step besides
        just checking that they exist.

        :param netCDF4.Dataset dataset: An open netCDF dataset

        Basic "does it exist" checks are done in BaseNCEICheck:check_recommended
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

        recommended_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended global attributes')

        # Do any of the variables define platform ?
        variable_defined_platform = any((hasattr(var, 'platform') for var in dataset.variables))
        if not variable_defined_platform:
            platform_name = getattr(dataset, 'platform', '')
            recommended_ctx.assert_true(platform_name and platform_name in dataset.variables, 'platform should exist and point to a variable.')

        sea_names = [sn.lower() for sn in util.get_sea_names()]
        sea_name = getattr(dataset, 'sea_name', '')
        sea_name = sea_name.replace(', ', ',')
        sea_name = sea_name.split(',') if sea_name else []
        for sea in sea_name:
            recommended_ctx.assert_true(
                sea.lower() in sea_names,
                'sea_name attribute should exist and should be from the NODC sea names list: {} is not a valid sea name'.format(sea)
            )

        # Parse dates, check for ISO 8601
        for attr in ['time_coverage_start', 'time_coverage_end', 'date_created', 'date_modified']:
            attr_value = getattr(dataset, attr, '')
            try:
                parse_datetime(attr_value)
                recommended_ctx.assert_true(True, '')  # Score it True!
            except ISO8601Error:
                recommended_ctx.assert_true(False, '{} should exist and be ISO-8601 format (example: PT1M30S), currently: {}'.format(attr, attr_value))

        units = getattr(dataset, 'geospatial_lat_units', '').lower()
        recommended_ctx.assert_true(units == 'degrees_north', 'geospatial_lat_units attribute should be degrees_north: {}'.format(units))

        units = getattr(dataset, 'geospatial_lon_units', '').lower()
        recommended_ctx.assert_true(units == 'degrees_east', 'geospatial_lon_units attribute should be degrees_east: {}'.format(units))

        value = getattr(dataset, 'geospatial_vertical_positive', '')
        recommended_ctx.assert_true(value.lower() in ['up', 'down'], 'geospatial_vertical_positive attribute should be up or down: {}'.format(value))

        # I hate english.
        ack_exists = any((getattr(dataset, attr, '') != '' for attr in ['acknowledgment', 'acknowledgement']))
        recommended_ctx.assert_true(ack_exists, 'acknowledgement attribute should exist and not be empty')

        contributor_name = getattr(dataset, 'contributor_name', '')
        contributor_role = getattr(dataset, 'contributor_role', '')
        names = contributor_role.split(',')
        roles = contributor_role.split(',')
        recommended_ctx.assert_true(contributor_name != '', 'contributor_name should exist and not be empty.')
        recommended_ctx.assert_true(len(names) == len(roles), 'length of contributor names matches length of roles')
        recommended_ctx.assert_true(contributor_role != '', 'contributor_role should exist and not be empty.')
        recommended_ctx.assert_true(len(names) == len(roles), 'length of contributor names matches length of roles')

        if hasattr(dataset, 'comment'):
            recommended_ctx.assert_true(getattr(dataset, 'comment', '') != '', 'comment attribute should not be empty if specified')

        return recommended_ctx.to_result()

    def check_geophysical(self, dataset):
        '''
        Check the geophysical variable attributes for 1.1 templates.

        :param netCDF4.Dataset dataset: An open netCDF dataset

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
        # Check the science variables to ensure they are good

        results = []
        for var in util.get_geophysical_variables(dataset):
            ncvar = dataset.variables[var]
            test_ctx = TestCtx(BaseCheck.HIGH, 'Required attributes for variable {}'.format(var))
            test_ctx.assert_true(getattr(ncvar, 'standard_name', '') != '', 'standard_name attribute must exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'units', '') != '', 'units attribute must exist and not be empty')
            coordinates = getattr(ncvar, 'coordinates', '')
            test_ctx.assert_true(coordinates != '', 'coordinates must exist and not be empty')
            results.append(test_ctx.to_result())

            test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for variable {}'.format(var))
            test_ctx.assert_true(getattr(ncvar, 'long_name', '') != '', 'long_name should exist and not be empty')
            if not hasattr(ncvar, 'standard_name'):
                test_ctx.assert_true(getattr(ncvar, 'nodc_name', '') != '', 'nodc_name should exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'valid_min', '') != '', 'valid_min should exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'valid_max', '') != '', 'valid_max should exist and not be empty')
            grid_mapping = getattr(ncvar, 'grid_mapping', '')
            test_ctx.assert_true(grid_mapping != '', 'grid_mapping should exist and not be empty')
            if grid_mapping:
                test_ctx.assert_true(grid_mapping in dataset.variables, 'grid_mapping attribute is a variable')
            test_ctx.assert_true(getattr(ncvar, 'source', '') != '', 'source should exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'references', '') != '', 'references should exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'cell_methods', '') != '', 'cell_methods should exist and not be empty')
            ancillary_variables = getattr(ncvar, 'ancillary_variables', '')
            if ancillary_variables:
                ancillary_variables = ancillary_variables.split(' ')
            all_variables = all([v in dataset.variables for v in ancillary_variables])
            if ancillary_variables:
                test_ctx.assert_true(all_variables, 'ancillary_variables point to variables')
            platform = getattr(ncvar, 'platform', '')
            if platform:
                test_ctx.assert_true(platform in dataset.variables, 'platform attribute points to variable')
            instrument = getattr(ncvar, 'instrument', '')
            if instrument:
                test_ctx.assert_true(instrument in dataset.variables, 'instrument attribute points to variable')

            if hasattr(ncvar, 'comment'):
                test_ctx.assert_true(getattr(ncvar, 'comment', '') != '', 'comment attribute should not be empty if specified')

            results.append(test_ctx.to_result())

        return results

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
        # Check for the platform variable
        platforms = util.get_platform_variables(dataset)
        if not platforms:
            return Result(BaseCheck.MEDIUM,
                          False,
                          'A container variable storing information about the platform exists',
                          ['Create a variable to store the platform information'])

        results = []
        for platform in platforms:
            test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for platform variable {}'.format(platform))
            pvar = dataset.variables[platform]
            test_ctx.assert_true(getattr(pvar, 'long_name', '') != '', 'long_name attribute should exist and not be empty')
            if hasattr(pvar, 'comment'):
                test_ctx.assert_true(getattr(pvar, 'comment', '') != '', 'comment attribute should not be empty if specified')
            # We only check to see if nodc_code, wmo_code and imo_code are empty. They are only recommended if they exist for the platform.
            found_identifier = False
            if hasattr(pvar, 'nodc_code'):
                test_ctx.assert_true(getattr(pvar, 'nodc_code', '') != '', 'nodc_code should not be empty if specified')
                found_identifier = True
            if hasattr(pvar, 'wmo_code'):
                test_ctx.assert_true(getattr(pvar, 'wmo_code', '') != '', 'wmo_code should not be empty if specified')
                found_identifier = True
            if hasattr(pvar, 'imo_code'):
                test_ctx.assert_true(getattr(pvar, 'imo_code', '') != '', 'imo_code should not be empty if specified')
                found_identifier = True
            if hasattr(pvar, 'call_sign'):
                test_ctx.assert_true(getattr(pvar, 'call_sign', '') != '', 'call_sign attribute should not be empty if specified')
                found_identifier = True
            test_ctx.assert_true(found_identifier, 'At least one attribute should be defined to identify the platform: nodc_code, wmo_code, imo_code, call_sign.')
            results.append(test_ctx.to_result())

        return results


class NCEI2_0Check(BaseNCEICheck):
    def __init__(self):
        super(NCEI2_0Check, self).__init__()
        self.high_rec_atts = [
            'title',
            'summary',
            'keywords',
        ]
        self.rec_atts  = [
            'source',
            'uuid',
            'id',
            'naming_authority',
            'geospatial_lat_min',
            'geospatial_lat_max',
            'geospatial_lon_min',
            'geospatial_lon_max',
            'geospatial_vertical_max',
            'geospatial_vertical_min',
            'institution',
            'creator_name',
            'creator_url',
            'creator_email',
            'project',
            'processing_level',
            'publisher_name',
            'publisher_email',
            'publisher_url',
            'history',
            'license',
            'geospatial_bounds',
            'geospatial_bounds_crs',
            'geospatial_bounds_vertical_crs'
        ]
        self.sug_atts = [
            'creator_type',
            'creator_institution',
            'publisher_type',
            'publisher_institution',
            'program',
            'contributor_name',
            'contributor_role',
            'geospatial_lat_units',
            'geospatial_lon_units',
            'geospatial_vertical_units',
            'product_version',
            'keywords_vocabulary',
            'platform_vocabulary',
            'instrument',
            'instrument_vocabulary',
            'metadata_link',
            'references'
        ]

    def check_base_required_attributes(self, dataset):
        '''
        Check the global required and highly recommended attributes for 2.0 templates. These go an extra step besides
        just checking that they exist.

        :param netCDF4.Dataset dataset: An open netCDF dataset

        :Conventions = "CF-1.6, ACDD-1.3" ; //............................... REQUIRED - Always try to use latest value. (CF)
        :featureType = "timeSeries" ; //..................................... REQUIRED - CF attribute for identifying the featureType.
        :cdm_data_type = "Station" ; //...................................... REQUIRED (ACDD)
        :ncei_template_version = "NCEI_NetCDF_TimeSeries_Orthogonal_Template_v1.1" ; //....... REQUIRED (NCEI)
        :title = "" ; //............................................... HIGHLY RECOMMENDED - Provide a useful title for the data in the file. (ACDD)
        :summary = "" ; //............................................. HIGHLY RECOMMENDED - Provide a useful summary or abstract for the data in the file. (ACDD)
        :keywords = "" ; //............................................ HIGHLY RECOMMENDED - A comma separated list of keywords coming from the keywords_vocabulary. (ACDD)
        :Conventions = "CF-1.6, ACDD-1.3" ; //......................... HIGHLY RECOMMENDED    - A comma separated list of the conventions being followed. Always try to use latest version. (CF/ACDD)
        '''
        test_ctx = TestCtx(BaseCheck.HIGH, 'Required global attributes')

        conventions = getattr(dataset, 'Conventions', '')
        feature_type = getattr(dataset, 'featureType', '')

        # Define conventions
        accepted_conventions = ['CF-1.6', 'ACDD-1.3']
        dataset_conventions = conventions.replace(' ', '').split(',')
        for accepted_convention in accepted_conventions:
            if accepted_convention not in dataset_conventions:
                test_ctx.assert_true(False, 'Conventions attribute is missing or is not equal to "CF-1.6, ACDD-1.3": {}'.format(conventions))
                break
        else:
            test_ctx.assert_true(True, '')

        # Check feature types
        test_ctx.assert_true(feature_type in ['point', 'timeSeries', 'trajectory', 'profile', 'timeSeriesProfile', 'trajectoryProfile'],
                             'Feature type must be one of point, timeSeries, trajectory, profile, timeSeriesProfile, trajectoryProfile: {}'.format(feature_type))

        return test_ctx.to_result()

    def check_recommended_global_attributes(self, dataset):
        '''
        Check the global recommended attributes for 2.0 templates. These go an extra step besides
        just checking that they exist.

        :param netCDF4.Dataset dataset: An open netCDF dataset

        :id = "" ; //.................................................. RECOMMENDED - Should be a human readable unique identifier for data set. (ACDD)
        :naming_authority = "" ; //.................................... RECOMMENDED - Backward URL of institution (for example, gov.noaa.ncei). (ACDD)
        :history = "" ; //............................................. RECOMMENDED - Provides an audit trail for modifications to the original data. (ACDD)
        :source = "" ; //.............................................. RECOMMENDED - The method of production of the original data. (CF)
        :processing_level = "" ; //.................................... RECOMMENDED - Provide a description of the processing or quality control level of the data. (ACDD)
        :comment = "" ; //............................................. RECOMMENDED - Provide useful additional information here. (CF)
        :acknowledgment = "" ; //...................................... RECOMMENDED - A place to acknowledge various types of support for the project that produced this data. (ACDD)
        :license = "" ; //............................................. RECOMMENDED - Describe the restrictions to data access and distribution. (ACDD)
        :standard_name_vocabulary = "CF Standard Name Table vNN" ; //.. RECOMMENDED   - If using CF standard name attribute for variables. Replace NN with the CF standard name table number  (CF)
        :date_created = "" ; //........................................ RECOMMENDED - Creation date of this version of the data(netCDF).  Use ISO 8601:2004 for date and time. (ACDD)
        :creator_name = "" ; //........................................ RECOMMENDED - The name of the person (or other creator type specified by the creator_type attribute) principally responsible for creating this data. (ACDD)
        :creator_email = "" ; //....................................... RECOMMENDED - The email address of the person (or other creator type specified by the creator_type attribute) principally responsible for creating this data. (ACDD)
        :creator_url = "" ; //......................................... RECOMMENDED - The URL of the person (or other creator type specified by the creator_type attribute) principally responsible for creating this data. (ACDD)
        :institution = "" ; //......................................... RECOMMENDED -The name of the institution principally responsible for originating this data..  An institution attribute can be used for each variable if variables come from more than one institution. (CF/ACDD)
        :project = "" ; //............................................. RECOMMENDED - The name of the project(s) principally responsible for originating this data. Multiple projects can be separated by commas. (ACDD)
        :publisher_name = "" ; //...................................... RECOMMENDED - The name of the person (or other entity specified by the publisher_type attribute) responsible for publishing the data file or product to users, with its current metadata and format. (ACDD)
        :publisher_email = "" ; //..................................... RECOMMENDED - The email address of the person (or other entity specified by the publisher_type attribute) responsible for publishing the data file or product to users, with its current metadata and format. (ACDD)
        :publisher_url = "" ; //....................................... RECOMMENDED - The URL of the person (or other entity specified by the publisher_type attribute) responsible for publishing the data file or product to users, with its current metadata and format. (ACDD)
        :geospatial_bounds = "" ; //................................... RECOMMENDED - Describes the data's 2D or 3D geospatial extent in OGC's Well-Known Text (WKT) Geometry format. (ACDD)
        :geospatial_bounds_crs = "" ; //............................... RECOMMENDED - The coordinate reference system (CRS) of the point coordinates in the geospatial_bounds attribute. (ACDD)
        :geospatial_bounds_vertical_crs = "" ; //...................... RECOMMENDED - The vertical coordinate reference system (CRS) for the Z axis of the point coordinates in the geospatial_bounds attribute. (ACDD)
        :geospatial_lat_min = 0.0d ; //................................ RECOMMENDED - Describes a simple lower latitude limit. (ACDD)
        :geospatial_lat_max = 0.0d ; //................................ RECOMMENDED - Describes a simple upper latitude limit. (ACDD)
        :geospatial_lon_min = 0.0d ; //................................ RECOMMENDED - Describes a simple lower longitude limit. (ACDD)
        :geospatial_lon_max = 0.0d ; //................................ RECOMMENDED - Describes a simple upper longitude limit. (ACDD)
        :geospatial_vertical_min = 0.0d ; //........................... RECOMMENDED - Describes the numerically smaller vertical limit. (ACDD)
        :geospatial_vertical_max = 0.0d ; //........................... RECOMMENDED - Describes the numerically larger vertical limit. (ACDD)
        :geospatial_vertical_positive = "" ; //........................ RECOMMENDED - Use "up" or "down". (ACDD)
        :time_coverage_start = "" ; //................................. RECOMMENDED - Describes the time of the first data point in the data set. Use ISO 8601:2004 for date and time. (ACDD)
        :time_coverage_end = "" ; //................................... RECOMMENDED - Describes the time of the last data point in the data set. Use ISO 8601:2004 for date and time.(ACDD)
        :time_coverage_duration = "" ; //.............................. RECOMMENDED - Describes the duration of the data set. Use ISO 8601:2004 for date and time. (ACDD)
        :time_coverage_resolution = "" ; //............................ RECOMMENDED - Describes the targeted time period between each value in the data set. Use ISO 8601:2004 for date and time. (ACDD)
        :uuid = "" ; //................................................ RECOMMENDED - Machine readable unique identifier for each file. A new uuid is created whenever the file is changed. (NCEI)
        :sea_name = "" ; //............................................ RECOMMENDED - The names of the sea in which the data were collected. Use NCEI sea names table. (NCEI)
        '''

        recommended_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended global attributes')

        sea_names = [sn.lower() for sn in util.get_sea_names()]
        sea_name = getattr(dataset, 'sea_name', '')
        sea_name = sea_name.replace(', ', ',')
        sea_name = sea_name.split(',') if sea_name else []
        for sea in sea_name:
            recommended_ctx.assert_true(
                sea.lower() in sea_names,
                'sea_name attribute should exist and should be from the NODC sea names list: {} is not a valid sea name'.format(sea)
            )

        # Parse dates, check for ISO 8601
        for attr in ['time_coverage_start', 'time_coverage_end', 'date_created', 'date_modified']:
            attr_value = getattr(dataset, attr, '')
            try:
                parse_datetime(attr_value)
                recommended_ctx.assert_true(True, '')  # Score it True!
            except ISO8601Error:
                recommended_ctx.assert_true(False, '{} should exist and be ISO-8601 format (example: PT1M30S), currently: {}'.format(attr, attr_value))

        value = getattr(dataset, 'geospatial_vertical_positive', '')
        recommended_ctx.assert_true(value.lower() in ['up', 'down'], 'geospatial_vertical_positive attribute should be up or down: {}'.format(value))

        # I hate english.
        ack_exists = any((getattr(dataset, attr, '') != '' for attr in ['acknowledgment', 'acknowledgement']))
        recommended_ctx.assert_true(ack_exists, 'acknowledgement attribute should exist and not be empty')

        standard_name_vocab = getattr(dataset, 'standard_name_vocabulary', '')
        regex = re.compile(r'[sS]tandard [nN]ame [tT]able')
        recommended_ctx.assert_true(regex.search(standard_name_vocab),
                                    "standard_name_vocabulary doesn't contain 'Standard Name Table': {}".format(standard_name_vocab))

        if hasattr(dataset, 'comment'):
            recommended_ctx.assert_true(getattr(dataset, 'comment', '') != '', 'comment attribute should not be empty if specified')
        return recommended_ctx.to_result()

    def check_base_suggested_attributes(self, dataset):
        '''
        Check the global suggested attributes for 2.0 templates. These go an extra step besides
        just checking that they exist.

        :param netCDF4.Dataset dataset: An open netCDF dataset

        :creator_type = "" ; //........................................ SUGGESTED - Specifies type of creator with one of the following: 'person', 'group', 'institution', or 'position'. (ACDD)
        :creator_institution = "" ; //................................. SUGGESTED - The institution of the creator; should uniquely identify the creator's institution. (ACDD)
        :publisher_type = "" ; //...................................... SUGGESTED - Specifies type of publisher with one of the following: 'person', 'group', 'institution', or 'position'. (ACDD)
        :publisher_institution = "" ; //............................... SUGGESTED - The institution that presented the data file or equivalent product to users; should uniquely identify the institution. (ACDD)
        :program = "" ; //............................................. SUGGESTED - The overarching program(s) of which the dataset is a part. (ACDD)
        :contributor_name = "" ; //.................................... SUGGESTED - The name of any individuals, projects, or institutions that contributed to the creation of this data. (ACDD)
        :contributor_role = "" ; //.................................... SUGGESTED - The role of any individuals, projects, or institutions that contributed to the creation of this data. (ACDD)
        :geospatial_lat_units = "degrees_north" ; //..................  SUGGESTED - Units for the latitude axis described in "geospatial_lat_min" and "geospatial_lat_max" attributes. Use UDUNITS compatible units. (ACDD)
        :geospatial_lon_units = "degrees_east"; //..................... SUGGESTED - Units for the longitude axis described in "geospatial_lon_min" and "geospatial_lon_max" attributes. Use UDUNITS compatible units. (ACDD)
        :geospatial_vertical_units = "" ; //........................... SUGGESTED - Units for the vertical axis described in "geospatial_vertical_min" and "geospatial_vertical_max" attributes. The default is EPSG:4979. (ACDD)
        :date_modified = "" ; //....................................... SUGGESTED - The date on which the data was last modified. Note that this applies just to the data, not the metadata. Use ISO 8601:2004 for date and time. (ACDD)
        :date_issued = "" ; //......................................... SUGGESTED - The date on which this data (including all modifications) was formally issued (i.e., made available to a wider audience). Note that these apply just to the data, not the metadata. Use ISO 8601:2004 for date and time. (ACDD)
        :date_metadata_modified = "" ; //.............................. SUGGESTED - The date on which the metadata was last modified. Use ISO 8601:2004 for date and time. (ACDD)
        :product_version = "" ; //..................................... SUGGESTED - Version identifier of the data file or product as assigned by the data creator. (ACDD)
        :keywords_vocabulary = "" ; //................................. SUGGESTED - Identifies the controlled keyword vocabulary used to specify the values within the attribute "keywords". Example: 'GCMD:GCMD Keywords' ACDD)
        :platform = "" ; //............................................ SUGGESTED - Name of the platform(s) that supported the sensor data used to create this data set or product. Platforms can be of any type, including satellite, ship, station, aircraft or other. (ACDD)
        :platform_vocabulary = "" ; //................................. SUGGESTED - Controlled vocabulary for the names used in the "platform" attribute . Example: ‘NASA/GCMD Platform Keywords Version 8.1’ (ACDD)
        :instrument = "" ; //.......................................... SUGGESTED - Name of the contributing instrument(s) or sensor(s) used to create this data set or product. (ACDD)
        :instrument_vocabulary = "" ; //............................... SUGGESTED - Controlled vocabulary for the names used in the "instrument" attribute. Example: ‘NASA/GCMD Instrument Keywords Version 8.1’ (ACDD)
        :cdm_data_type = "Point" ; //.................................. SUGGESTED - The data type, as derived from Unidata's Common Data Model Scientific Data types and understood by THREDDS. (ACDD)
        :metadata_link = "" ; //....................................... SUGGESTED - A URL that gives the location of more complete metadata. A persistent URL is recommended for this attribute. (ACDD)
        :references = "" ; //.......................................... SUGGESTED - Published or web-based references that describe the data or methods used to produce it. Recommend URIs (such as a URL or DOI) for papers or other references. (CF)
        '''
        suggested_ctx = TestCtx(BaseCheck.LOW, 'Suggested global attributes')

        # Do any of the variables define platform ?
        platform_name = getattr(dataset, 'platform', '')
        suggested_ctx.assert_true(platform_name != '', 'platform should exist and point to a term in :platform_vocabulary.')

        cdm_data_type = getattr(dataset, 'cdm_data_type', '')
        suggested_ctx.assert_true(cdm_data_type.lower() in ['grid', 'image', 'point', 'radial', 'station', 'swath', 'trajectory'],
                     'cdm_data_type must be one of Grid, Image, Point, Radial, Station, Swath, Trajectory: {}'.format(cdm_data_type))

        # Parse dates, check for ISO 8601
        for attr in ['date_modified', 'date_issued', 'date_metadata_modified']:
            attr_value = getattr(dataset, attr, '')
            try:
                parse_datetime(attr_value)
                suggested_ctx.assert_true(True, '')  # Score it True!
            except ISO8601Error:
                suggested_ctx.assert_true(False, '{} should exist and be ISO-8601 format (example: PT1M30S), currently: {}'.format(attr, attr_value))

        units = getattr(dataset, 'geospatial_lat_units', '').lower()
        suggested_ctx.assert_true(units == 'degrees_north', 'geospatial_lat_units attribute should be degrees_north: {}'.format(units))

        units = getattr(dataset, 'geospatial_lon_units', '').lower()
        suggested_ctx.assert_true(units == 'degrees_east', 'geospatial_lon_units attribute should be degrees_east: {}'.format(units))

        contributor_name = getattr(dataset, 'contributor_name', '')
        contributor_role = getattr(dataset, 'contributor_role', '')
        names = contributor_role.split(',')
        roles = contributor_role.split(',')
        suggested_ctx.assert_true(contributor_name != '', 'contributor_name should exist and not be empty.')
        suggested_ctx.assert_true(len(names) == len(roles), 'length of contributor names matches length of roles')
        suggested_ctx.assert_true(contributor_role != '', 'contributor_role should exist and not be empty.')
        suggested_ctx.assert_true(len(names) == len(roles), 'length of contributor names matches length of roles')

        return suggested_ctx.to_result()

    def check_geophysical(self, dataset):
        '''
        Check the geophysical variable attributes for 2.0 templates.
        Attributes missing_value and coverage_content_type have been added in NCEI 2.0

        :param netCDF4.Dataset dataset: An open netCDF dataset

        float geophysical_variable_1(time) ;//................................ This is an example of how each and every geophysical variable in the file should be represented. Replace the name of the variable("geophysical_variable_1") with a suitable name. Replace "float" by data type which is appropriate for the variable.
            geophysical_variable_1:long_name = "" ; //................... RECOMMENDED - Provide a descriptive, long name for this variable.
            geophysical_variable_1:standard_name = "" ; //............... REQUIRED    - If using a CF standard name and a suitable name exists in the CF standard name table.
            geophysical_variable_1:ncei_name = "" ; //................... RECOMMENDED - From the NCEI variables vocabulary, if standard_name does not exist.
            geophysical_variable_1:units = "" ; //....................... REQUIRED    - Use UDUNITS compatible units.
            geophysical_variable_1:scale_factor = 0.0f ; //.............. REQUIRED if the data uses a scale_factor other than 1.The data type should be the data type of the variable.
            geophysical_variable_1:add_offset = 0.0f ; // ............... REQUIRED if the data uses an add_offset other than 0. The data type should be the data type of the variable.
            geophysical_variable_1:_FillValue = 0.0f ; //................ REQUIRED  if there could be undefined values in the data.
            geophysical_variable_1:missing_value = 0.0f ; //............. RECOMMENDED  if there could be missing values in the data. Not necessary if there is only one value which is the same as _FillValue.
            geophysical_variable_1:valid_min = 0.0f ; //................. RECOMMENDED - Replace with correct value.
            geophysical_variable_1:valid_max = 0.0f ; //................. RECOMMENDED - Replace with correct value.
            geophysical_variable_1:coordinates = "time lat lon z" ; //... REQUIRED    - Include the auxiliary coordinate variables and optionally coordinate variables in the list. The order itself does not matter. Also, note that whenever any auxiliary coordinate variable contains a missing value, all other coordinate, auxiliary coordinate and data values corresponding to that element should also contain missing values.
            geophysical_variable_1:coverage_content_type = "" ; //....... RECOMMENDED - An ISO 19115-1 code to indicate the source of the data (image, thematicClassification, physicalMeasurement, auxiliaryInformation, qualityInformation, referenceInformation, modelResult, or coordinate). (ACDD)
            geophysical_variable_1:grid_mapping = "crs" ; //............. RECOMMENDED - It is highly recommended that the data provider put the data in a well known geographic coordinate system and provide the details of the coordinate system.
            geophysical_variable_1:source = "" ; //...................... RECOMMENDED - The method of production of the original data
            geophysical_variable_1:references = "" ; //.................. RECOMMENDED - Published or web-based references that describe the data or methods used to produce it.
            geophysical_variable_1: cell_methods = "" ; // .............. RECOMMENDED - Use the coordinate variables to define the cell values (ex., "time: point lon: point lat: point z: point").
            geophysical_variable_1:ancillary_variables = "instrument_parameter_variable platform_variable boolean_flag_variable enumerated_flag_variable" ; //......... RECOMMENDED - Identify the variable name(s) of the flag(s) and other ancillary variables relevant to this variable.  Use a space-separated list.
            geophysical_variable_1:platform = "platform_variable" ; //... RECOMMENDED - Refers to name of variable containing information on the platform from which this variable was collected.
            geophysical_variable_1:instrument = "instrument_variable";//..RECOMMENDED - Refers to name of variable containing information on the instrument from which this variable was collected.
            geophysical_variable_1:comment = "" ; //..................... RECOMMENDED - Add useful, additional information here.
        '''

        results = []
        for var in util.get_geophysical_variables(dataset):
            ncvar = dataset.variables[var]

            test_ctx = TestCtx(BaseCheck.HIGH, 'Required attributes for variable {}'.format(var))
            test_ctx.assert_true(getattr(ncvar, 'standard_name', '') != '', 'standard_name attribute must exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'units', '') != '', 'units attribute must exist and not be empty')
            coordinates = getattr(ncvar, 'coordinates', '')
            test_ctx.assert_true(coordinates != '', 'coordinates must exist and not be empty')
            results.append(test_ctx.to_result())

            test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for variable {}'.format(var))
            test_ctx.assert_true(getattr(ncvar, 'long_name', '') != '', 'long_name should exist and not be empty')
            if not hasattr(ncvar, 'standard_name'):
                test_ctx.assert_true(getattr(ncvar, 'ncei_name', '') != '', 'ncei_name should exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'valid_min', '') != '', 'valid_min should exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'valid_max', '') != '', 'valid_max should exist and not be empty')

            coverage_content_type_options = ['image', 'thematicClassification', 'physicalMeasurement', 'auxiliaryInformation',
                                             'qualityInformation', 'referenceInformation', 'modelResult', 'coordinate']
            test_ctx.assert_true(getattr(ncvar, 'coverage_content_type', '') in coverage_content_type_options,
                                 ('coverage_content_type should exist and be one of the following:'
                                  'image, thematicClassification, physicalMeasurement, auxiliaryInformation, '
                                  'qualityInformation, referenceInformation, modelResult, or coordinate'))

            grid_mapping = getattr(ncvar, 'grid_mapping', '')
            test_ctx.assert_true(grid_mapping != '', 'grid_mapping should exist and not be empty')
            if grid_mapping:
                test_ctx.assert_true(grid_mapping in dataset.variables, 'grid_mapping attribute is a variable')
            test_ctx.assert_true(getattr(ncvar, 'source', '') != '', 'source should exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'references', '') != '', 'references should exist and not be empty')
            test_ctx.assert_true(getattr(ncvar, 'cell_methods', '') != '', 'cell_methods should exist and not be empty')
            ancillary_variables = getattr(ncvar, 'ancillary_variables', '')
            if ancillary_variables:
                ancillary_variables = ancillary_variables.split(' ')
            all_variables = all([v in dataset.variables for v in ancillary_variables])
            if ancillary_variables:
                test_ctx.assert_true(all_variables, 'ancillary_variables point to variables')
            platform = getattr(ncvar, 'platform', '')
            if platform:
                test_ctx.assert_true(platform in dataset.variables, 'platform attribute points to variable')
            instrument = getattr(ncvar, 'instrument', '')
            if instrument:
                test_ctx.assert_true(instrument in dataset.variables, 'instrument attribute points to variable')

            if hasattr(ncvar, 'comment'):
                test_ctx.assert_true(getattr(dataset, 'comment', '') != '', 'comment attribute should not be empty if specified')
            results.append(test_ctx.to_result())

        return results

    def check_platform(self, dataset):
        '''
        int platform_variable; //............................................ RECOMMENDED - a container variable storing information about the platform. If more than one, can expand each attribute into a variable. For example, platform_call_sign and platform_nodc_code. See instrument_parameter_variable for an example.
                platform_variable:long_name = "" ; //........................ RECOMMENDED - Provide a descriptive, long name for this variable.
                platform_variable:comment = "" ; //.......................... RECOMMENDED - Add useful, additional information here.
                platform_variable:call_sign = "" ; //........................ RECOMMENDED - This attribute identifies the call sign of the platform.
                platform_variable:ncei_code = ""; //......................... RECOMMENDED - This attribute identifies the NCEI code of the platform. Look at http://www.nodc.noaa.gov/cgi-bin/OAS/prd/platform to find if NCEI codes are available.
                platform_variable:wmo_code = "";//........................... RECOMMENDED - This attribute identifies the wmo code of the platform. Information on getting WMO codes is available at http://www.wmo.int/pages/prog/amp/mmop/wmo-number-rules.html
                platform_variable:imo_code  = "";//.......................... RECOMMENDED - This attribute identifies the International Maritime Organization (IMO) number assigned by Lloyd's register.
        '''
        # Check for the platform variable
        platforms = util.get_platform_variables(dataset)
        if not platforms:
            return Result(BaseCheck.MEDIUM,
                          False,
                          'A container variable storing information about the platform exists',
                          ['Create a variable to store the platform information'])

        results = []
        for platform in platforms:
            test_ctx = TestCtx(BaseCheck.MEDIUM, 'Recommended attributes for platform variable {}'.format(platform))
            pvar = dataset.variables[platform]
            test_ctx.assert_true(getattr(pvar, 'long_name', '') != '', 'long_name attribute should exist and not be empty')
            if hasattr(pvar, 'comment'):
                test_ctx.assert_true(getattr(pvar, 'comment', '') != '', 'comment attribute should not be empty if specified')
            # We only check to see if nodc_code, wmo_code and imo_code are empty. They are only recommended if they exist for the platform.
            found_identifier = False
            if hasattr(pvar, 'ncei_code'):
                test_ctx.assert_true(getattr(pvar, 'ncei_code', '') != '', 'ncei_code should not be empty if specified')
                found_identifier = True
            if hasattr(pvar, 'wmo_code'):
                test_ctx.assert_true(getattr(pvar, 'wmo_code', '') != '', 'wmo_code should not be empty if specified')
                found_identifier = True
            if hasattr(pvar, 'imo_code'):
                test_ctx.assert_true(getattr(pvar, 'imo_code', '') != '', 'imo_code should not be empty if specified')
                found_identifier = True
            if hasattr(pvar, 'call_sign'):
                test_ctx.assert_true(getattr(pvar, 'call_sign', '') != '', 'call_sign attribute should not be empty if specified')
                found_identifier = True
            test_ctx.assert_true(found_identifier, 'At least one attribute should be defined to identify the platform: ncei_code, wmo_code, imo_code, call_sign.')
            results.append(test_ctx.to_result())

        return results
