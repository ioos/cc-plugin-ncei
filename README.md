# NCEI Template Compliance Checker

This is a checker for [NCEI netCDF Templates v1.1](http://www.nodc.noaa.gov/data/formats/netcdf/v1.1/) files.

It works with the [ioos/compliance-checker](https://github.com/ioos/compliance-checker).

Copyright 2015-2016 RPS ASA

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Please see LICENSE for the full license text.


### Installation

1. Activate your virtualenv/conda

2. Install the plugin:

   ```
   pip install 'git+git://github.com/ioos/cc-plugin-ncei.git'
   ```

3. Tests should now show up when you run compliance checker:

   ```
   compliance-checker -t ncei-trajectoryprofile-orthogonal -v https://data.nodc.noaa.gov/thredds/dodsC/testdata/mbiddle/GOLD_STANDARD_NETCDF/1.1/NODC_trajectoryProfile_template_v1.1_2016-06-14_125323.993167.nc

   --------------------------------------------------------------------------------
                       The dataset scored 124 out of 127 points
                  during the ncei-trajectoryprofile-orthogonal check
   --------------------------------------------------------------------------------
                              Verbose Scoring Breakdown:
   
                                    High Priority
   --------------------------------------------------------------------------------
       Name                            :Priority: Score
   All geophysical variables are trajector :3:     2/2
   Required Global Attributes for Trajecto :3:     1/3
   Required attributes for variable lat    :3:     3/3
   Required attributes for variable lon    :3:     3/3
   Required attributes for variable sal    :3:     3/3
   Required attributes for variable temp   :3:     3/3
   Required attributes for variable time   :3:     3/3
   Required attributes for variable z      :3:     5/5
   Required global attributes              :3:     5/5
   ...
   ```

### Usage

```
usage: compliance-checker [-h] [--test TEST]
                          [--criteria [{lenient,normal,strict}]] [--verbose]
                          [-f {text,html,json}] [-o OUTPUT] [-V] [-l]
                          [dataset_location [dataset_location ...]]

positional arguments:
  dataset_location      Defines the location of the dataset to be checked.

optional arguments:
  -h, --help            show this help message and exit
  --test TEST, -t TEST, --test= TEST, -t= TEST
                        Select the Checks you want to perform. Defaults to
                        'acdd' if unspecified
  --criteria [{lenient,normal,strict}], -c [{lenient,normal,strict}]
                        Define the criteria for the checks. Either Strict,
                        Normal, or Lenient. Defaults to Normal.
  --verbose, -v         Increase output. May be specified up to three times.
  -f {text,html,json}, --format {text,html,json}
                        Output format
  -o OUTPUT, --output OUTPUT
                        Output filename
  -V, --version         Display the IOOS Compliance Checker version
                        information.
  -l, --list-tests      List the available tests
```


### Examples

1. Running NCEI Point check on a THREDDS Endpoint

```
compliance-check -t ncei-point -v https://data.nodc.noaa.gov/thredds/dodsC/testdata/mbiddle/GOLD_STANDARD_NETCDF/1.1/NODC_point_template_v1.1_2016-06-14_125317.379316.nc
```

2. Running NCEI Trajectory Profile Orthogonal Check on local dataset

```
compliance-checker -t ncei-trajectory-profile-orthogonal -v ~/data/sample-trajectory-profile.nc
```

3. Outputting JSON trom a gridded file check

```
compliance-checker -t ncei-grid -f json -o ~/Documents/sample_grid_report.json ~/Documents/sample_grid_report.nc
```
