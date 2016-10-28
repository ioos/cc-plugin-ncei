from cc_plugin_ncei.tests.ncei_test_case import NCEITestCase
from cc_plugin_ncei.tests.resources import STATIC_FILES


class TestNCEITimeSeries1_1(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-timeseries-orthogonal:1.1', STATIC_FILES['nodc-timeseries'])

    def test_global_profile_score(self):
        assert not self.errors

        assert self.results['scored_points'] == 121
        assert self.results['possible_points'] == 125
        known_messages = [
            'geospatial_lat_resolution should exist and not be empty.',
            'geospatial_lon_resolution should exist and not be empty.',
            'geospatial_vertical_resolution should exist and not be empty.',
            'nodc_template_version attribute must be NODC_NetCDF_TimeSeries_Orthogonal_Template_v1.1'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)


class TestNCEITimeSeries2_0(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-timeseries-orthogonal:2.0', STATIC_FILES['ncei-timeseries-orthogonal:2.0'])

    def test_global_profile_score(self):
        assert not self.errors

        assert self.results['scored_points'] == 143
        assert self.results['possible_points'] == 147
        known_messages = [
            'wmo_code should not be empty if specified',
            'imo_code should not be empty if specified',
            'call_sign attribute should not be empty if specified',
            'time_coverage_resolution should exist and be ISO-8601 format (example: PT1M30S), currently: PT10.S'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)
