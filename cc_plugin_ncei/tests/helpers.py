import tempfile

from netCDF4 import Dataset


class MockNetCDF(Dataset):
    """Wrapper object around NetCDF Dataset to write data only to memory."""

    def __init__(self, filename=None):
        # taken from test/tst_diskless.py NetCDF library
        # even though we aren't persisting data to disk, the constructor
        # requires a filename not currently in use by another Dataset object..
        if filename is None:
            with tempfile.NamedTemporaryFile(
                suffix=".nc",
                delete=True,
            ) as f:
                temp_filename = f.name
        else:
            temp_filename = filename
        super().__init__(
            temp_filename,
            "w",
            diskless=True,
            persist=False,
        )
