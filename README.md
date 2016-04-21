# NCEI Template Compliance Checker

This is a checker for [NCEI netCDF Templates v1.1](http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/) files.

It works with the [ioos/compliance-checker](https://github.com/ioos/compliance-checker).

### Usage

Activate your virtualenv/conda env and `pip install git+git://github.com/ioos/cc-plugin-ncei.git`.  You should see the ncei checks in the list of `--test` suites when running `compliance-checker`.  If you do not, run `pip install -e .` to link the tests to your checker.  Then deactivate your virtual environment and run `workon <vertual_env_name>`.  The tests should now show.
