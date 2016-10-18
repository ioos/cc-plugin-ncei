
from cc_plugin_ncei.tests.ncei_test_case import NCEITestCase
from cc_plugin_ncei.tests.resources import STATIC_FILES


class TestNCEITrajectory1_1(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-trajectory:1.1', STATIC_FILES['nodc-trajectory'])

    def test_global_profile_score(self):
        assert not self.errors

        assert self.results['scored_points'] == 127
        assert self.results['possible_points'] == 128
        known_messages = [
            'sea_name attribute should exist and should be from the NODC sea names list: Cordell Bank National Marine Sanctuary is not a valid sea name'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)


class TestNCEITrajectory2_0(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-trajectory:2.0', STATIC_FILES['ncei-trajectory:2.0'])

    def test_global_profile_score(self):
        assert not self.errors

        assert self.results['scored_points'] == 145
        assert self.results['possible_points'] == 148
        known_messages = [
            'wmo_code should not be empty if specified',
            'sea_name attribute should exist and should be from the NODC sea names list: Cordell Bank National Marine Sanctuary is not a valid sea name',
            'time_coverage_resolution should exist and be ISO-8601 format (example: PT1M30S), currently: PT10.S'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)
