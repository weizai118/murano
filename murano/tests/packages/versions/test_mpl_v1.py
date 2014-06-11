#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import imghdr
import murano.packages.load_utils as load_utils
import murano.tests.base as test_base
import murano.tests.utils as test_utils
import os
from oslo.config import cfg


class TestMplV1(test_base.MuranoTestCase):
    def setUp(self):
        super(TestMplV1, self).setUp()
        test_utils.setup_dummy_db()
        self.addCleanup(test_utils.reset_dummy_db)
        self.addCleanup(cfg.CONF.reset)
        self.addCleanup(test_utils.reset_dummy_db)

    def test_supplier_info_load(self):
        package_dir = os.path.abspath(
            os.path.join(__file__, '../../test_packages/test.mpl.v1.app')
        )
        package = load_utils.load_from_dir(package_dir)

        self.assertNotEqual(package.supplier, None)
        self.assertEqual(package.supplier['Name'], 'Supplier Name')
        self.assertEqual(package.supplier['CompanyUrl'], {
            'Link': 'http://example.com',
            'Text': 'Example Company'
        })
        self.assertEqual(
            package.supplier['Summary'],
            'Company summary goes here'
        )
        self.assertEqual(
            package.supplier['Description'],
            'Marked up company description goes here'
        )
        self.assertEqual(package.supplier['Logo'], 'test_supplier_logo.png')

        self.assertEqual(imghdr.what('', package.supplier_logo), 'png')
