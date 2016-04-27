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
    'timeSeriesOrthogonal' : get_filename('tests/data/timeSeriesOrthogonal.nc'),
    'timeSeriesIncomplete' : get_filename('tests/data/timeSeriesIncomplete.nc'),
    'grid' : get_filename('tests/data/grid.nc'),
    'point' : get_filename('tests/data/point.nc'),
    'profileIncomplete' : get_filename('tests/data/profileIncomplete.nc'),
    'profileOrthogonal' : get_filename('tests/data/profileOrthogonal.nc'),
    'timeSeriesProfileIncomplete' : get_filename('tests/data/timeSeriesProfileIncomplete.nc'),
    'timeSeriesProfileIncompleteTimeOrthDepth' : get_filename('tests/data/timeSeriesProfileIncompleteTimeOrthDepth.nc'),
    'timeSeriesProfileOrthTimeIncompleteDepth' : get_filename('tests/data/timeSeriesProfileOrthTimeIncompleteDepth.nc'),
    'timeSeriesProfileOrthogonal' : get_filename('tests/data/timeSeriesProfileOrthogonal.nc'),
    'trajectory' : get_filename('tests/data/trajectory.nc'),
}

