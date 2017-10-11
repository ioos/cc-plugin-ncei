from netCDF4 import Dataset
import tempfile


# Taken from newer cchecker release.  Will be removed once cchecker release is
# update
class MockNetCDF(Dataset):
    """
    Wrapper object around NetCDF Dataset to write data only to memory.
    """

    def __init__(self):
        # taken from test/tst_diskless.py NetCDF library
        # even though we aren't persisting data to disk, the constructor
        # requires a filename not currently in use by another Dataset object..
        tmp_filename = tempfile.NamedTemporaryFile(suffix='.nc',
                                                   delete=True).name
        super(MockNetCDF, self).__init__(tmp_filename, 'w', diskless=True,
                                         persist=False)
