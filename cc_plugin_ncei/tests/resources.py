from pkg_resources import resource_filename
import sh
import os

def get_filename(path):
    '''
    Returns the path to a valid dataset
    '''
    filename = resource_filename('cc_plugin_ncei', path)
    if not os.path.exists(filename):
        cdl_path = filename.replace('.nc', '.cdl')
        generate_dataset(cdl_path, filename)
    return filename

def generate_dataset(cdl_path, nc_path):
    sh.ncgen('-o', nc_path, cdl_path)

STATIC_FILES = {
    'point': get_filename('tests/data/NODC_point_template_v1.1_2016-06-14_125317.379316.nc'),
    'profile': get_filename('tests/data/NODC_profile_template_v1.1_2016-06-14_125318.375947.nc'),
    'timeseries': get_filename('tests/data/NODC_timeSeries_template_v1.1_2016-06-14_125320.125407.nc'),
    'timeseries-profile': get_filename('tests/data/NODC_timeSeriesProfile_template_v1.1_2016-06-14_125321.546019.nc'),
    'trajectory-profile': get_filename('tests/data/NODC_trajectoryProfile_template_v1.1_2016-06-14_125323.993167.nc'),
    'trajectory': get_filename('tests/data/NODC_trajectory_template_v1.1_2016-06-14_125322.975680.nc')
}

