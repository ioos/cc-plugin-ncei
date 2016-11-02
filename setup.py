from __future__ import with_statement
from setuptools import setup, find_packages
from cc_plugin_ncei import __version__


def readme():
    with open('README.md') as f:
        return f.read()

reqs = [line.strip() for line in open('requirements.txt')]

setup(name                 = "cc-plugin-ncei",
      version              = __version__,
      description          = "Compliance Checker NCEI Templates Compliance plugin",
      long_description     = readme(),
      license              = 'Apache License 2.0',
      author               = "Luke Campbell",
      author_email         = "luke.campbell@rpsgroup.com",
      url                  = "https://github.com/ioos/cc-plugin-ncei/",
      packages             = find_packages(),
      install_requires     = reqs,
      package_data         = {'cc_plugin_ncei': ['data/*.json', 'data/*.xml']},
      classifiers          = [
                             'Development Status :: 5 - Production/Stable',
                             'Intended Audience :: Developers',
                             'Intended Audience :: Science/Research',
                             'License :: OSI Approved :: Apache Software License',
                             'Operating System :: POSIX :: Linux',
                             'Programming Language :: Python',
                             'Topic :: Scientific/Engineering',
      ],
      entry_points         = {
        'compliance_checker.suites': [
            'ncei-timeseries-orthogonal-1.1 = cc_plugin_ncei.ncei_timeseries:NCEITimeSeriesOrthogonal1_1',
            'ncei-grid-1.1 = cc_plugin_ncei.ncei_grid:NCEIGrid1_1',
            'ncei-point-1.1 = cc_plugin_ncei.ncei_point:NCEIPoint1_1',
            'ncei-timeseries-incomplete-1.1 = cc_plugin_ncei.ncei_timeseries:NCEITimeSeriesIncomplete1_1',
            'ncei-trajectory-1.1 = cc_plugin_ncei.ncei_trajectory:NCEITrajectory1_1',
            'ncei-profile-incomplete-1.1 = cc_plugin_ncei.ncei_profile:NCEIProfileIncomplete1_1',
            'ncei-profile-orthogonal-1.1 = cc_plugin_ncei.ncei_profile:NCEIProfileOrthogonal1_1',
            'ncei-timeseries-profile-orthogonal-1.1 = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileOrthogonal1_1',
            'ncei-timeseries-profile-orthtime-incompletedepth-1.1 = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileOrthTimeIncompleteDepth1_1',
            'ncei-timeseries-profile-incomplete-1.1 = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileIncomplete1_1',
            'ncei-timeseries-profile-incompletetime-orthdepth-1.1 = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileIncompleteTimeOrthDepth1_1',
            'ncei-trajectory-profile-orthogonal-1.1 = cc_plugin_ncei.ncei_trajectory_profile:NCEITrajectoryProfileOrthogonal1_1',
            'ncei-trajectory-profile-incomplete-1.1 = cc_plugin_ncei.ncei_trajectory_profile:NCEITrajectoryProfileIncomplete1_1',
            'ncei-timeseries-orthogonal-2.0 = cc_plugin_ncei.ncei_timeseries:NCEITimeSeriesOrthogonal2_0',
            'ncei-grid-2.0 = cc_plugin_ncei.ncei_grid:NCEIGrid2_0',
            'ncei-point-2.0 = cc_plugin_ncei.ncei_point:NCEIPoint2_0',
            'ncei-timeseries-incomplete-2.0 = cc_plugin_ncei.ncei_timeseries:NCEITimeSeriesIncomplete2_0',
            'ncei-trajectory-2.0 = cc_plugin_ncei.ncei_trajectory:NCEITrajectory2_0',
            'ncei-profile-incomplete-2.0 = cc_plugin_ncei.ncei_profile:NCEIProfileIncomplete2_0',
            'ncei-profile-orthogonal-2.0 = cc_plugin_ncei.ncei_profile:NCEIProfileOrthogonal2_0',
            'ncei-timeseries-profile-orthogonal-2.0 = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileOrthogonal2_0',
            'ncei-timeseries-profile-orthtime-incompletedepth-2.0 = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileOrthTimeIncompleteDepth2_0',
            'ncei-timeseries-profile-incomplete-2.0 = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileIncomplete2_0',
            'ncei-timeseries-profile-incompletetime-orthdepth-2.0 = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileIncompleteTimeOrthDepth2_0',
            'ncei-trajectory-profile-orthogonal-2.0 = cc_plugin_ncei.ncei_trajectory_profile:NCEITrajectoryProfileOrthogonal2_0',
            'ncei-trajectory-profile-incomplete-2.0 = cc_plugin_ncei.ncei_trajectory_profile:NCEITrajectoryProfileIncomplete2_0'
        ]
      }
)
