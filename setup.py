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
    author_email         = "lcampbell@asascience.com",
    url                  = "https://github.com/ioos/compliance-checker",
    packages             = find_packages(),
    install_requires     = reqs,
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
        ]
    }
)

