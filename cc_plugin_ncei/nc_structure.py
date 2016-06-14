#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
cc_plugin_ncei/features.py
'''
from compliance_checker.cf.util import is_vertical_coordinate


class NCStructure(object):
    '''
    Helper class to pull out types of variables and dataset metadata
    '''

    def __init__(self, dataset):
        self.nc = dataset

    def get_time(self):
        '''
        Returns the variable corresponding to dataset time.

        Notes: axis=T takes precendence over having a standard_name of time
        '''
        axis_candidates = self.nc.get_variables_by_attributes(axis='T')
        if axis_candidates:
            return axis_candidates[0].name
        std_name_candidates = self.nc.get_variables_by_attributes(standard_name='time')
        if std_name_candidates:
            return std_name_candidates[0].name
        return None

    def get_lat(self):
        axis_candidates = self.nc.get_variables_by_attributes(axis='Y')
        if axis_candidates:
            return axis_candidates[0].name
        std_name_candidates = self.nc.get_variables_by_attributes(standard_name='latitude')
        if std_name_candidates:
            return std_name_candidates[0].name
        return None

    def get_lon(self):
        axis_candidates = self.nc.get_variables_by_attributes(axis='X')
        if axis_candidates:
            return axis_candidates[0].name
        std_name_candidates = self.nc.get_variables_by_attributes(standard_name='longitude')
        if std_name_candidates:
            return std_name_candidates[0].name
        return None

    def get_height(self):
        candidates = []
        for var in self.nc.variables:
            if is_vertical_coordinate(var, self.nc.variables[var]):
                if var not in candidates:
                    candidates.append(var)
        if candidates:
            return candidates[0]
        return None

    def get_coordinates(self):
        coordinates = [
            self.get_time(),
            self.get_lat(),
            self.get_lon(),
            self.get_height()
        ]
        coordinates = [c for c in coordinates if c is not None]
        return coordinates

    def get_grid_mappings(self):
        have_grid_mapping = self.nc.get_variables_by_attributes(grid_mapping=lambda v: v is not None)
        grid_mappings = []
        for var in have_grid_mapping:
            grid_mapping = var.grid_mapping
            if grid_mapping in self.nc.variables:
                grid_mappings.append(grid_mapping)
        return grid_mappings

    def get_platform_variables(self):
        candidates = []
        for var in self.nc.get_variables_by_attributes(platform=lambda v: v is not None):
            platform = var.platform
            if platform in self.nc.variables and platform not in candidates:
                candidates.append(platform)
        global_platform = getattr(self.nc, 'platform', '')
        if global_platform and global_platform in self.nc.variables and global_platform not in candidates:
            candidates.append(global_platform)
        return candidates

    def get_instrument_variables(self):
        candidates = []
        for var in self.nc.get_variables_by_attributes(instrument=lambda v: v is not None):
            instrument = var.instrument
            if instrument in self.nc.variables and instrument not in candidates:
                candidates.append(instrument)
        global_instrument = getattr(self.nc, 'instrument', '')
        if global_instrument and global_instrument in self.nc.variables and global_instrument not in candidates:
            candidates.append(global_instrument)
        return candidates

    def get_ancillary_variables(self):
        candidates = []
        for var in self.nc.get_variables_by_attributes(ancillary_variables=lambda v: v is not None):
            ancillary_variables = var.ancillary_variables.split(' ')
            for ancillary in ancillary_variables:
                if ancillary and ancillary in self.nc.variables and ancillary not in candidates:
                    candidates.append(ancillary)
        return candidates

    def get_timeseries_id(self):
        return self.nc.get_variables_by_attributes(cf_role='timeseries_id')

    def get_geophysical_variables(self):
        others = []
        for var in self.nc.get_variables_by_attributes(axis=lambda v: v is not None):
            others.append(var.name)
        others.extend(self.get_grid_mappings())
        others.extend(self.get_platform_variables())
        others.extend(self.get_instrument_variables())
        others.extend(self.get_ancillary_variables())
        others.extend(self.get_timeseries_id())

        candidates = []

        for var in self.nc.variables:
            if var in others:
                continue
            if var in ('platform_name', 'station_name', 'instrument_name', 'station_id', 'platform_id', 'surface_altitude'):
                continue
            candidates.append(var)

        return candidates


