from compliance_checker.suite import CheckSuite
from netCDF4 import Dataset
import unittest


class NCEITestCase(unittest.TestCase):
    # @see
    # http://www.saltycrane.com/blog/2012/07/how-prevent-nose-unittest-using-docstring-when-verbosity-2/
    def shortDescription(self):
        return None

    # override __str__ and __repr__ behavior to show a copy-pastable nosetest name for ion tests
    #  ion.module:TestClassName.test_function_name
    def __repr__(self):
        name = self.id()
        name = name.split('.')
        if name[0] not in ["ion", "pyon"]:
            return "%s (%s)" % (name[-1], '.'.join(name[:-1]))
        else:
            return "%s ( %s )" % (name[-1], '.'.join(name[:-2]) + ":" + '.'.join(name[-2:]))
    __str__ = __repr__

    def load_dataset(self, nc_dataset):
        '''
        Return a pairwise object for the dataset
        '''
        if isinstance(nc_dataset, basestring):
            nc_dataset = Dataset(nc_dataset, 'r')
            self.addCleanup(nc_dataset.close)
        return nc_dataset

    def get_failed_results(self, results):
        failed = []
        for r in results:
            if r.value is False or r.value[0] != r.value[1]:
                failed.append(r)
        return failed

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
        score_groups = cs.run(ds, checker)
        results, self.errors = score_groups[checker]
        self.results = cs.build_structure(checker, results, dataset_location)

