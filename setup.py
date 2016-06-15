from __future__ import with_statement
import sys

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
    package_data         = {'cc_plugin_ncei': ['data/*.json', 'data/*.csv']},
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
            'ncei-timeseries-orthogonal = cc_plugin_ncei.ncei_timeseries:NCEITimeSeriesOrthogonal', 
            'ncei-grid = cc_plugin_ncei.ncei_grid:NCEIGrid',
            'ncei-point = cc_plugin_ncei.ncei_point:NCEIPoint',
            'ncei-timeseries-incomplete = cc_plugin_ncei.ncei_timeseries:NCEITimeSeriesIncomplete',
            'ncei-trajectory = cc_plugin_ncei.ncei_trajectory:NCEITrajectory',
            'ncei-profile-incomplete = cc_plugin_ncei.ncei_profile:NCEIProfileIncomplete',
            'ncei-profile-orthogonal = cc_plugin_ncei.ncei_profile:NCEIProfileOrthogonal',
            'ncei-timeseries-profile-orthogonal = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileOrthogonal',
            'ncei-timeseries-profile-orthtime-incompletedepth = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileOrthTimeIncompleteDepth',
            'ncei-timeseries-profile-incomplete = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileIncomplete',
            'ncei-timeseries-profile-incompletetime-orthdepth = cc_plugin_ncei.ncei_timeseries_profile:NCEITimeSeriesProfileIncompleteTimeOrthDepth',
            'ncei-trajectory-profile-orthogonal = cc_plugin_ncei.ncei_trajectory_profile:NCEITrajectoryProfileOrthogonal',
            'ncei-trajectory-profile-incomplete = cc_plugin_ncei.ncei_trajectory_profile:NCEITrajectoryProfileIncomplete',
        ]
    }
)

