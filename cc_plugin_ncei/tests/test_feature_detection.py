#!/usr/bin/env python
"""tests/test_feature_detection.py"""

from unittest import TestCase

from netCDF4 import Dataset

from cc_plugin_ncei import util
from cc_plugin_ncei.tests import resources


class TestFeatureDetection(TestCase):
    """Tests the feature type detection of cdftools"""

    def test_point(self):
        """Ensures point detection works"""
        with Dataset(resources.STATIC_FILES["point"]) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_point(nc, variable), f"{variable} is point"

    def test_timeseries(self):
        """Ensures timeseries detection works"""
        with Dataset(resources.STATIC_FILES["timeseries"]) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_timeseries(
                    nc,
                    variable,
                ), f"{variable} is timeseries"

    def test_multi_timeseries_orthogonal(self):
        """Ensures multi-timeseries-orthogonal detection works"""
        with Dataset(
            resources.STATIC_FILES["multi-timeseries-orthogonal"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_multi_timeseries_orthogonal(
                    nc,
                    variable,
                ), f"{variable} is multi-timeseries orthogonal"

    def test_multi_timeseries_incomplete(self):
        """Ensures multi-timeseries-incomplete detection works"""
        with Dataset(
            resources.STATIC_FILES["multi-timeseries-incomplete"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_multi_timeseries_incomplete(
                    nc,
                    variable,
                ), f"{variable} is multi-timeseries incomplete"

    def test_trajectory(self):
        """Ensures trajectory detection works"""
        with Dataset(resources.STATIC_FILES["trajectory"]) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_cf_trajectory(
                    nc,
                    variable,
                ), f"{variable} is trajectory"

    def test_trajectory_single(self):
        """Ensures trajectory-single detection works"""
        with Dataset(resources.STATIC_FILES["trajectory-single"]) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_single_trajectory(
                    nc,
                    variable,
                ), f"{variable} is trajectory-single"

    def test_profile_orthogonal(self):
        """Ensures profile-orthogonal detection works"""
        with Dataset(resources.STATIC_FILES["profile-orthogonal"]) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_profile_orthogonal(
                    nc,
                    variable,
                ), f"{variable} is profile-orthogonal"

    def test_profile_incomplete(self):
        """Ensures profile-incomplete detection works"""
        with Dataset(resources.STATIC_FILES["profile-incomplete"]) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_profile_incomplete(
                    nc,
                    variable,
                ), f"{variable} is profile-incomplete"

    def test_timeseries_profile_single_station(self):
        """Ensures timeseries profile single station detection works"""
        with Dataset(
            resources.STATIC_FILES["timeseries-profile-single-station"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_timeseries_profile_single_station(
                    nc,
                    variable,
                ), f"{variable} is timeseries-profile-single-station"

    def test_timeseries_profile_multi_station(self):
        """Ensures timeseries profile multi station detection works"""
        with Dataset(
            resources.STATIC_FILES["timeseries-profile-multi-station"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_timeseries_profile_multi_station(
                    nc,
                    variable,
                ), f"{variable} is timeseries-profile-multi-station"

    def test_timeseries_profile_single_ortho_time(self):
        """Ensures timeseries profile single station ortho time detection works"""
        with Dataset(
            resources.STATIC_FILES["timeseries-profile-single-ortho-time"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_timeseries_profile_single_ortho_time(
                    nc,
                    variable,
                ), f"{variable} is timeseries-profile-single-ortho-time"

    def test_timeseries_profile_multi_ortho_time(self):
        """Ensures timeseries profile multi station ortho time detection works"""
        with Dataset(
            resources.STATIC_FILES["timeseries-profile-multi-ortho-time"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_timeseries_profile_multi_ortho_time(
                    nc,
                    variable,
                ), f"{variable} is timeseries-profile-multi-ortho-time"

    def test_timeseries_profile_ortho_depth(self):
        """Ensures timeseries profile ortho depth detection works"""
        with Dataset(
            resources.STATIC_FILES["timeseries-profile-ortho-depth"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_timeseries_profile_ortho_depth(
                    nc,
                    variable,
                ), f"{variable} is timeseries-profile-ortho-depth"

    def test_timeseries_profile_incomplete(self):
        """Ensures timeseries profile station incomplete detection works"""
        with Dataset(
            resources.STATIC_FILES["timeseries-profile-incomplete"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_timeseries_profile_incomplete(
                    nc,
                    variable,
                ), f"{variable} is timeseries-profile-incomplete"

    def test_trajectory_profile_orthogonal(self):
        """Ensures trajectory profile orthogonal detection works"""
        with Dataset(
            resources.STATIC_FILES["trajectory-profile-orthogonal"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_trajectory_profile_orthogonal(
                    nc,
                    variable,
                ), f"{variable} is trajectory profile orthogonal"

    def test_trajectory_profile_incomplete(self):
        """Ensures trajectory profile incomplete detection works"""
        with Dataset(
            resources.STATIC_FILES["trajectory-profile-incomplete"],
        ) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_trajectory_profile_incomplete(
                    nc,
                    variable,
                ), f"{variable} is trajectory profile incomplete"

    def test_2d_regular_grid(self):
        """Ensures 2D Regular Grid detection works"""
        with Dataset(resources.STATIC_FILES["2d-regular-grid"]) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_2d_regular_grid(
                    nc,
                    variable,
                ), f"{variable} is 2D regular grid"

    def test_3d_regular_grid(self):
        """Ensures 2U Regular Grid detection works"""
        with Dataset(resources.STATIC_FILES["3d-regular-grid"]) as nc:
            for variable in util.get_geophysical_variables(nc):
                assert util.is_3d_regular_grid(
                    nc,
                    variable,
                ), f"{variable} is 3d regular grid"
