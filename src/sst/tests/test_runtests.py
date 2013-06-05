#
#   Copyright (c) 2013 Canonical Ltd.
#
#   This file is part of: SST (selenium-simple-test)
#   https://launchpad.net/selenium-simple-test
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from cStringIO import StringIO

from sst import (
    runtests,
    tests,
)


class TestRunTestsFilteringByTestId(tests.ImportingLocalFilesTest):

    def setUp(self):
        super(TestRunTestsFilteringByTestId, self).setUp()
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
file: t/test_foo.py
import unittest

class Test(unittest.TestCase):

    def test_me(self):
      self.assertTrue(True)
file: t/bar.py
Don't look at me !
file: t/too.py
Don't look at me !
''')

    def run_tests(self, tests, **kwargs):
        out = StringIO()
        runtests.runtests(tests, 'no results directory used', out,
                          test_dir='t', collect_only=True, **kwargs)
        lines = out.getvalue().splitlines()
        return lines

    def test_all(self):
        self.assertEqual(['t.bar', 't.test_foo', 't.too'],
                         self.run_tests(None))

    def test_single_include(self):
        self.assertEqual(['t.bar'],
                         self.run_tests(['t.b']))

    def test_multiple_includes(self):
        self.assertEqual(['t.bar', 't.too'],
                         self.run_tests(['t.b', 't.to']))

    def test_single_exclude(self):
        self.assertEqual(['t.bar'],
                         self.run_tests(None, excludes=['t.t']))

    def test_multiple_excludes(self):
        self.assertEqual(['t.test_foo'],
                         self.run_tests(None, excludes=['t.to', 't.b']))

    def test_mixed(self):
        self.assertEqual(['t.test_foo'],
                         self.run_tests(['t.t'], excludes=['to']))


class SSTRunExitCodeTestCase(tests.ImportingLocalFilesTest):

    def setUp(self):
        super(SSTRunExitCodeTestCase, self).setUp()
        tests.write_tree_from_desc('''dir: t
file: t/__init__.py
from sst import loader
discover = loader.discoverRegularTests

file: t/test_all_pass.py
import unittest
class TestAllPass(unittest.TestCase):
    def test_all_pass(self):
        self.assertTrue(True)

file: t/test_one_fail.py
import unittest
class TestOneFail(unittest.TestCase):
    def test_one_fail(self):
        self.assertTrue(False)

file: t/test_multi_fail.py
import unittest
class TestMultiFail(unittest.TestCase):
    def test_fail_1(self):
        self.assertTrue(False)
    def test_fail_2(self):
        self.assertTrue(False)
''')

    def run_tests(self, args):
        out = StringIO()
        failures = runtests.runtests(args, 'no results directory used', out)
        return bool(failures)

    def test_pass(self):
        self.assertEqual(0, self.run_tests(['test_all_pass$']))

    def test_fail(self):
        self.assertEqual(1, self.run_tests(['test_one_fail$']))

    def test_multi_fail(self):
        self.assertEqual(1, self.run_tests(['test_fail_.*']))
