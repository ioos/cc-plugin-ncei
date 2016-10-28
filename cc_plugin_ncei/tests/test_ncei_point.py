from compliance_checker.suite import CheckSuite
from cc_plugin_ncei.tests.ncei_test_case import NCEITestCase
from cc_plugin_ncei.tests.resources import STATIC_FILES


class TestNCEIPoint1_1(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-point:1.1', STATIC_FILES['nodc-point'])

    def test_global_point_score(self):
        assert not self.errors

        assert self.results['scored_points'] == 121
        assert self.results['possible_points'] == 124
        known_messages = [
            'geospatial_lat_resolution should exist and not be empty.',
            'geospatial_lon_resolution should exist and not be empty.',
            'geospatial_vertical_resolution should exist and not be empty.'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)


class TestNCEIPoint2_0(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-point:2.0', STATIC_FILES['ncei-point:2.0'])

    def test_global_point_score(self):
        assert not self.errors

        assert self.results['scored_points'] == 141
        assert self.results['possible_points'] == 144
        known_messages = [
            'wmo_code should not be empty if specified',
            'imo_code should not be empty if specified',
            'call_sign attribute should not be empty if specified'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)
