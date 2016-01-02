"""
Unified Communications server will be required for these tests
Tests are performed against UCM 10.5.2
"""
import unittest

from axl.foley import AXL


wsdl = 'file:///Users/brad/Documents/code/python/axl/axlsqltoolkit/schema/10.5/AXLAPI.wsdl'
ucm = AXL('admin', 'asdfpoiu', wsdl, '192.168.200.10')


class TestAXL(unittest.TestCase):

    # Location
    def test_add_location_and_delete_location_is_successful(self):
        add_loc = ucm.add_location('test_location')
        del_loc = ucm.delete_location('test_location')
        self.assertEqual(add_loc['success'], True) and self.assertEqual(del_loc['success'], True)

    def test_add_duplicate_location_fails(self):
            location = 'test_dup_location'
            ucm.add_location(location)
            duplicate = ucm.add_location(location)

            # clean up
            ucm.delete_location(location)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    # Region
    def test_delete_non_existing_location_fails(self):
        location = 'i_dont_exist'
        duplicate = ucm.delete_location(location)
        self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'not found')

    def test_add_region_and_delete_region_is_successful(self):
        add_reg = ucm.add_region('test_region')
        del_reg = ucm.delete_region('test_region')
        self.assertEqual(add_reg['success'], True) and self.assertEqual(del_reg['success'], True)

    def test_add_duplicate_region_fails(self):
            region = 'test_dup_region'
            ucm.add_region(region)
            duplicate = ucm.add_region(region)

            # clean up
            ucm.delete_region(region)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_region_fails(self):
        region = 'i_dont_exist'
        duplicate = ucm.delete_region(region)
        self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'not found')