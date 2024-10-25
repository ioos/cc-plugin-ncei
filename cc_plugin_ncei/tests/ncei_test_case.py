import unittest

from compliance_checker.suite import CheckSuite
from netCDF4 import Dataset


class NCEITestCase(unittest.TestCase):
    def __repr__(self):
        """Override __str__ and __repr__ behavior to show a copy-pastable nosetest name for ion tests
        ion.module:TestClassName.test_function_name.
        """
        name = self.id()
        name = name.split(".")
        if name[0] not in ["ion", "pyon"]:
            return "{} ({})".format(name[-1], ".".join(name[:-1]))
        return "{} ( {} )".format(
            name[-1],
            ".".join(name[:-2]) + ":" + ".".join(name[-2:]),
        )

    __str__ = __repr__

    def load_dataset(self, nc_dataset):
        """Return a pairwise object for the dataset."""
        if isinstance(nc_dataset, str):
            nc_dataset = Dataset(nc_dataset, "r")
            self.addCleanup(nc_dataset.close)
        return nc_dataset

    def get_failed_results(self, results):
        return [
            r for r in results if r.value is False or r.value[0] != r.value[1]
        ]

    def get_failed_messages(self, results):
        failed_results = self.get_failed_results(results)
        messages = []
        for result in failed_results:
            messages.extend(result.msgs)
        return messages

    def run_checker(self, checker, dataset_location):
        cs = CheckSuite()
        cs.load_all_available_checkers()
        ds = cs.load_dataset(dataset_location)
        score_groups = cs.run(ds, [], checker)
        results, self.errors = score_groups[checker]
        self.results = cs.build_structure(checker, results, dataset_location)
