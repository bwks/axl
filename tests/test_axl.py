"""
Unified Communications server will be required for these tests
Tests are performed against UCM 10.5.2
"""
import unittest

from axl.foley import AXL


wsdl = 'file:///Users/brad/Documents/code/python/axl/axlsqltoolkit/schema/10.5/AXLAPI.wsdl'
ucm = AXL('admin', 'asdfpoiu', wsdl, '192.168.200.10')


class TestAXL(unittest.TestCase):

    def test_add_location_is_successful(self):
        result = ucm.add_location('test_location')
        self.assertEqual(result['success'], True)

    def test_delete_location_is_successful(self):
        result = ucm.delete_location('test_location')
        self.assertEqual(result['success'], True)

    def test_add_duplicate_location_fails(self):
            location = 'test_dup_location'
            ucm.add_location(location)
            duplicate = ucm.add_location(location)

            # clean up
            ucm.delete_location(location)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_location_fails(self):
        location = 'i_dont_exist'
        duplicate = ucm.delete_location(location)
        self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'not found')

