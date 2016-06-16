
from cc_plugin_ncei.tests.ncei_test_case import NCEITestCase
from cc_plugin_ncei.tests.resources import STATIC_FILES


class TestNCEITimeSeriesProfile(NCEITestCase):

    def setUp(self):
        self.run_checker('ncei-trajectory-profile-orthogonal', STATIC_FILES['nodc-trajectory-profile'])

    def test_global_profile_score(self):
        assert not self.errors
        assert self.results['scored_points'] == 125
        assert self.results['possible_points'] == 127
        known_messages = [
            'sea_name attribute should exist and should be from the NODC sea names list: Cordell Bank National Marine Sanctuary is not a valid sea name',
            'nodc_template_version attribute must be NODC_NetCDF_TrajectoryProfile_Orthogonal_Template_v1.1'
        ]
        failed_messages = self.get_failed_messages(self.results['all_priorities'])
        assert sorted(failed_messages) == sorted(known_messages)

