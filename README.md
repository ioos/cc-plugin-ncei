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


### Usage

1. Activate your virtualenv/conda

2. Install the plugin:

   ```
   pip install 'git+git://github.com/ioos/cc-plugin-ncei.git'
   ```

3. Tests should now show up when you run compliance checker:

   ```
   usage: compliance-checker [-h] --test
                          {acdd,acdd:1.1,acdd:1.3,acdd:latest,cf,cf:1.6,cf:latest,gliderdac,ioos,ioos:0.1,ioos:latest,ncei-grid,ncei-grid:1.1,ncei-grid:latest,ncei-point,ncei-point:1.1,ncei-point:latest,ncei-profile-incomplete,ncei-profile-incomplete:1.1,ncei-profile-incomplete:latest,ncei-profile-orthogonal,ncei-profile-orthogonal:1.1,ncei-profile-orthogonal:latest,ncei-timeseries-incomplete,ncei-timeseries-incomplete:1.1,ncei-timeseries-incomplete:latest,ncei-timeseries-orthogonal,ncei-timeseries-orthogonal:1.1,ncei-timeseries-orthogonal:latest,ncei-timeseriesprofile-incomplete,ncei-timeseriesprofile-incomplete:1.1,ncei-timeseriesprofile-incomplete:latest,ncei-timeseriesprofile-incompletetime-orthdepth,ncei-timeseriesprofile-incompletetime-orthdepth:1.1,ncei-timeseriesprofile-incompletetime-orthdepth:latest,ncei-timeseriesprofile-orthogonal,ncei-timeseriesprofile-orthogonal:1.1,ncei-timeseriesprofile-orthogonal:latest,ncei-timeseriesprofile-orthtime-incompletedepth,ncei-timeseriesprofile-orthtime-incompletedepth:1.1,ncei-timeseriesprofile-orthtime-incompletedepth:latest,ncei-trajectory,ncei-trajectory:1.1,ncei-trajectory:latest,ncei-trajectoryProfile-orthogonal,ncei-trajectoryProfile-orthogonal:1.1,ncei-trajectoryProfile-orthogonal:latest}
                          [{acdd,acdd:1.1,acdd:1.3,acdd:latest,cf,cf:1.6,cf:latest,gliderdac,ioos,ioos:0.1,ioos:latest,ncei-grid,ncei-grid:1.1,ncei-grid:latest,ncei-point,ncei-point:1.1,ncei-point:latest,ncei-profile-incomplete,ncei-profile-incomplete:1.1,ncei-profile-incomplete:latest,ncei-profile-orthogonal,ncei-profile-orthogonal:1.1,ncei-profile-orthogonal:latest,ncei-timeseries-incomplete,ncei-timeseries-incomplete:1.1,ncei-timeseries-incomplete:latest,ncei-timeseries-orthogonal,ncei-timeseries-orthogonal:1.1,ncei-timeseries-orthogonal:latest,ncei-timeseriesprofile-incomplete,ncei-timeseriesprofile-incomplete:1.1,ncei-timeseriesprofile-incomplete:latest,ncei-timeseriesprofile-incompletetime-orthdepth,ncei-timeseriesprofile-incompletetime-orthdepth:1.1,ncei-timeseriesprofile-incompletetime-orthdepth:latest,ncei-timeseriesprofile-orthogonal,ncei-timeseriesprofile-orthogonal:1.1,ncei-timeseriesprofile-orthogonal:latest,ncei-timeseriesprofile-orthtime-incompletedepth,ncei-timeseriesprofile-orthtime-incompletedepth:1.1,ncei-timeseriesprofile-orthtime-incompletedepth:latest,ncei-trajectory,ncei-trajectory:1.1,ncei-trajectory:latest,ncei-trajectoryProfile-orthogonal,ncei-trajectoryProfile-orthogonal:1.1,ncei-trajectoryProfile-orthogonal:latest} ...]
                          [--criteria [{lenient,normal,strict}]] [--verbose]
                          [-f {text,html,json}] [-o OUTPUT] [-V]
                          [dataset_location [dataset_location ...]]
   compliance-checker: error: argument --test/-t/--test=/-t= is required
   ```

