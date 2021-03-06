# Copyright (c) 2012 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import luigi
from luigi.mock import MockFile
import unittest
from luigi.util import Derived

File = MockFile


class A(luigi.Task):
    def output(self):
        return File('/tmp/a.txt')

    def run(self):
        f = self.output().open('w')
        print >>f, 'hello, world'
        f.close()


class B(luigi.Task):
    date = luigi.DateParameter()

    def output(self):
        return File(self.date.strftime('/tmp/b-%Y-%m-%d.txt'))

    def run(self):
        f = self.output().open('w')
        print >>f, 'goodbye, space'
        f.close()

def XMLWrapper(cls):
    class XMLWrapperCls(Derived(cls)):
        def requires(self):
            return self.parent_obj

        def run(self):
            f = self.input().open('r')
            g = self.output().open('w')
            print >>g, '<?xml version="1.0" ?>'
            for line in f:
                print >>g, '<dummy-xml>' + line.strip() + '</dummy-xml>'
            g.close()

    return XMLWrapperCls

@luigi.expose
class AXML(XMLWrapper(A)):
    def output(self):
        return File('/tmp/a.xml')

@luigi.expose
class BXML(XMLWrapper(B)):
    def output(self):
        return File(self.date.strftime('/tmp/b-%Y-%m-%d.xml'))

class WrapperTest(unittest.TestCase):
    ''' This test illustrates how a task class can wrap another task class by modifying its behavior.

    See instance_wrap_test.py for an example of how instances can wrap each other. '''

    def test_a(self):
        luigi.run(['--local-scheduler', 'AXML'])
        self.assertEqual(MockFile._file_contents['/tmp/a.xml'], '<?xml version="1.0" ?>\n<dummy-xml>hello, world</dummy-xml>\n')

    def test_b(self):
        luigi.run(['--local-scheduler', 'BXML', '--date', '2012-01-01'])
        self.assertEqual(MockFile._file_contents['/tmp/b-2012-01-01.xml'], '<?xml version="1.0" ?>\n<dummy-xml>goodbye, space</dummy-xml>\n')


if __name__ == '__main__':
    luigi.run()
