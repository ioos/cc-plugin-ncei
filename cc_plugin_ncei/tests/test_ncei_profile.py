from cc_plugin_ncei.tests.ncei_test_case import NCEITestCase
from cc_plugin_ncei.tests.resources import STATIC_FILES


class TestNCEIProfile1_1(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-profile-orthogonal:1.1', STATIC_FILES['nodc-profile'])

    def test_global_profile_score(self):
        assert not self.errors

        assert self.results['scored_points'] == 125
        assert self.results['possible_points'] == 128
        known_messages = [
            'geospatial_lat_resolution should exist and not be empty.',
            'geospatial_lon_resolution should exist and not be empty.',
            'nodc_template_version attribute must be NODC_NetCDF_Profile_Orthogonal_Template_v1.1'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)


class TestNCEIProfile2_0(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-profile-orthogonal:2.0', STATIC_FILES['ncei-profile-orthogonal:2.0'])

    def test_global_profile_score(self):
        assert not self.errors

        assert self.results['scored_points'] == 145
        assert self.results['possible_points'] == 146
        known_messages = [
            'wmo_code should not be empty if specified'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)
