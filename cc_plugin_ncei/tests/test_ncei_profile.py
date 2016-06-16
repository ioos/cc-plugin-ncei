from cc_plugin_ncei.tests.ncei_test_case import NCEITestCase
from cc_plugin_ncei.tests.resources import STATIC_FILES


class TestNCEIProfile(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-profile-orthogonal', STATIC_FILES['nodc-profile'])

    def test_global_profile_score(self):
        assert not self.errors

        assert self.results['scored_points'] == 124
        assert self.results['possible_points'] == 128
        known_messages = [
            'geospatial_lat_resolution should exist and not be empty.',
            'geospatial_lon_resolution should exist and not be empty.',
            'sea_name attribute should exist and should be from the NODC sea names list: Cordell Bank National Marine Sanctuary is not a valid sea name',
            'nodc_template_version attribute must be NODC_NetCDF_Profile_Orthogonal_Template_v1.1'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)
