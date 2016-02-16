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
    'station_timeseries' : get_filename('tests/data/station_timeseries.nc'),
}

