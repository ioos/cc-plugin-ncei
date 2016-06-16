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
    'nodc-point': get_filename('tests/data/NODC_point_template_v1.1_2016-06-14_125317.379316.nc'),
    'nodc-profile': get_filename('tests/data/NODC_profile_template_v1.1_2016-06-14_125318.375947.nc'),
    'nodc-timeseries': get_filename('tests/data/NODC_timeSeries_template_v1.1_2016-06-14_125320.125407.nc'),
    'nodc-timeseries-profile': get_filename('tests/data/NODC_timeSeriesProfile_template_v1.1_2016-06-14_125321.546019.nc'),
    'nodc-trajectory-profile': get_filename('tests/data/NODC_trajectoryProfile_template_v1.1_2016-06-14_125323.993167.nc'),
    'nodc-trajectory': get_filename('tests/data/NODC_trajectory_template_v1.1_2016-06-14_125322.975680.nc'),
    'point': get_filename('tests/data/point.nc'),
    'timeseries': get_filename('tests/data/timeseries.nc'),
    'multi-timeseries-orthogonal': get_filename('tests/data/multi-timeseries-orthogonal.nc'),
    'multi-timeseries-incomplete': get_filename('tests/data/multi-timeseries-incomplete.nc'),
    'trajectory': get_filename('tests/data/trajectory.nc'),
    'trajectory-single': get_filename('tests/data/trajectory-single.nc'),
    'profile-orthogonal': get_filename('tests/data/profile-orthogonal.nc'),
    'profile-incomplete': get_filename('tests/data/profile-incomplete.nc'),
    'timeseries-profile-single-station': get_filename('tests/data/timeseries-profile-single-station.nc'),
    'timeseries-profile-multi-station': get_filename('tests/data/timeseries-profile-multi-station.nc'),
    'timeseries-profile-single-ortho-time': get_filename('tests/data/timeseries-profile-single-ortho-time.nc'),
    'timeseries-profile-multi-ortho-time': get_filename('tests/data/timeseries-profile-multi-ortho-time.nc'),
    'timeseries-profile-ortho-depth': get_filename('tests/data/timeseries-profile-ortho-depth.nc'),
    'timeseries-profile-incomplete': get_filename('tests/data/timeseries-profile-incomplete.nc'),
    'trajectory-profile-orthogonal': get_filename('tests/data/trajectory-profile-orthogonal.nc'),
    'trajectory-profile-incomplete': get_filename('tests/data/trajectory-profile-incomplete.nc'),
    '2d-regular-grid': get_filename('tests/data/2d-regular-grid.nc'),
    '3d-regular-grid': get_filename('tests/data/3d-regular-grid.nc'),
}

