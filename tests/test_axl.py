"""
Unified Communications server will be required for these tests
Tests are performed against UCM 10.5.2
"""
import unittest

from axl.foley import AXL

cucm = '10.10.11.14'
# cucm = '192.168.200.10'
wsdl = 'file:///Users/brad/Documents/code/python/axl/axlsqltoolkit/schema/10.5/AXLAPI.wsdl'
ucm = AXL('admin', 'asdfpoiu', wsdl, cucm)


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

    def test_delete_non_existing_location_fails(self):
        location = 'location_not_exist'
        result = ucm.delete_location(location)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # Region
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
        region = 'region_not_exist'
        result = ucm.delete_region(region)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    def test_update_region_with_non_existent_region_fails(self):
        result = ucm.update_region('reg_not_exists', 'blah')

        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    def test_update_region_is_successful(self):
        region = 'test_upr_reg'
        moh_region = 'test_upr_moh'
        other_region = 'test_upr_oth'
        ucm.add_region(region)
        ucm.add_region(moh_region)
        ucm.add_region(other_region)
        result = ucm.update_region(region, moh_region)

        # clean up
        ucm.delete_region(region)
        ucm.delete_region(moh_region)
        ucm.delete_region(other_region)

        self.assertEqual(result['success'], True)

    # SRST
    def test_add_srst_and_delete_srst_is_successful(self):
        add_srst = ucm.add_srst('test_srst', '192.168.100.100')
        del_srst = ucm.delete_srst('test_srst')
        self.assertEqual(add_srst['success'], True) and self.assertEqual(del_srst['success'], True)

    def test_add_duplicate_srst_fails(self):
            srst = 'test_dup_srst'
            ucm.add_srst(srst, '192.168.100.100')
            duplicate = ucm.add_srst(srst, '192.168.100.100')

            # clean up
            ucm.delete_srst(srst)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_srst_fails(self):
        srst = 'srst_not_exist'
        result = ucm.delete_srst(srst)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # Device Pool
    def test_add_device_pool_and_delete_device_pool_is_successful(self):
        device_pool = 'test_device_pool'
        add_device_pool = ucm.add_device_pool(device_pool)
        del_device_pool = ucm.delete_device_pool(device_pool)

        self.assertEqual(add_device_pool['success'], True) and self.assertEqual(del_device_pool['success'], True)

    def test_add_duplicate_device_pool_fails(self):
            device_pool = 'test_dup_device_pool'
            ucm.add_device_pool(device_pool)
            duplicate = ucm.add_device_pool(device_pool)

            # clean up
            ucm.delete_device_pool(device_pool)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_device_pool_fails(self):
        device_pool = 'dp_dont_exist'
        result = ucm.delete_device_pool(device_pool)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    def test_update_device_pool_rg_mrgl_is_successful(self):
        device_pool = 'test_dpu_dp'
        media_resource_group_list = 'test_dpu_mrgl'
        route_group = 'test_dpu_rg'
        ucm.add_device_pool(device_pool)
        ucm.add_media_resource_group_list(media_resource_group_list)
        ucm.add_route_group(route_group)

        result = ucm.update_device_pool_rg_mrgl(device_pool, route_group, media_resource_group_list)

        # clean up
        ucm.delete_device_pool(device_pool)
        ucm.delete_route_group(route_group)
        ucm.delete_media_resource_group_list(media_resource_group_list)

        self.assertEqual(result['success'], True)

    def test_update_device_pool_rg_mrgl_with_non_existent_device_pool_fails(self):
        result = ucm.update_device_pool_rg_mrgl('rg_not_exists', 'blah', 'blah')

        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    def test_update_device_pool_rg_mrgl_with_non_existent_route_group_fails(self):
        device_pool = 'test_dpu_no_rg_dp'
        ucm.add_device_pool(device_pool)

        result = ucm.update_device_pool_rg_mrgl(device_pool, 'rg_not_exist', 'blah')

        # clean up
        ucm.delete_device_pool(device_pool)

        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    def test_update_device_pool_rg_mrgl_with_non_existent_media_resource_group_list_fails(self):
        device_pool = 'test_dpu_no_mrgl_dp'
        route_group = 'test_dpu_no_mrgl_rg'

        ucm.add_device_pool(device_pool)
        ucm.add_route_group(route_group)

        result = ucm.update_device_pool_rg_mrgl(device_pool, route_group, 'mrgl_not_exist')

        # clean up
        ucm.delete_route_group(route_group)
        ucm.delete_device_pool(device_pool)

        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # Conference Bridge
    def test_add_conference_bridge_and_delete_conference_bridge_is_successful(self):
        conference_bridge = 'test_cfb'
        add_conf_bridge = ucm.add_conference_bridge(conference_bridge)
        del_conf_bridge = ucm.delete_conference_bridge(conference_bridge)

        self.assertEqual(add_conf_bridge['success'], True) and self.assertEqual(del_conf_bridge['success'], True)

    def test_add_duplicate_conference_bridge_fails(self):
            conference_bridge = 'test_dup_cfb'
            ucm.add_conference_bridge(conference_bridge)
            duplicate = ucm.add_conference_bridge(conference_bridge)

            # clean up
            ucm.delete_conference_bridge(conference_bridge)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_conference_bridge_fails(self):
        conference_bridge = 'cfb_not_exist'
        result = ucm.delete_conference_bridge(conference_bridge)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # Transcoder
    def test_add_transcoder_and_delete_transcoder_is_successful(self):

        transcoder = 'test_trans'
        add_transcoder = ucm.add_transcoder(transcoder)
        del_transcoder = ucm.delete_transcoder(transcoder)

        self.assertEqual(add_transcoder['success'], True) and self.assertEqual(del_transcoder['success'], True)

    def test_add_duplicate_transcoder_fails(self):
            transcoder = 'test_dup_trans'
            ucm.add_transcoder(transcoder)
            duplicate = ucm.add_transcoder(transcoder)

            # clean up
            ucm.delete_transcoder(transcoder)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_transcoder_fails(self):
        transcoder = 'trans_not_exist'
        result = ucm.delete_transcoder(transcoder)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # H323 Gateway
    def test_add_h323_gateway_and_delete_h323_gateway_is_successful(self):
        h323_gateway = '192.168.100.200'
        add_h323_gateway = ucm.add_h323_gateway(h323_gateway)
        del_h323_gateway = ucm.delete_h323_gateway(h323_gateway)

        self.assertEqual(add_h323_gateway['success'], True) and self.assertEqual(del_h323_gateway['success'], True)

    def test_add_duplicate_h323_gateway_fails(self):
            h323_gateway = 'test_dup_trans'
            ucm.add_h323_gateway(h323_gateway)
            duplicate = ucm.add_h323_gateway(h323_gateway)

            # clean up
            ucm.delete_h323_gateway(h323_gateway)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_h323_gateway_fails(self):
        h323_gateway = '6.6.6.6'
        result = ucm.delete_h323_gateway(h323_gateway)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    def test_update_h323_gateway_media_resource_group_list_is_successful(self):
        h323_gateway = '1.1.1.1'
        mrgl = 'test_h323_mrgl'
        ucm.add_h323_gateway(h323_gateway)
        ucm.add_media_resource_group_list(mrgl)
        result = ucm.update_h323_gateway_mrgl(h323_gateway, mrgl)

        # clean up
        ucm.delete_h323_gateway(h323_gateway)
        ucm.delete_media_resource_group_list(mrgl)

        self.assertEqual(result['success'], True)

    def test_update_h323_gateway_media_resource_group_list_with_non_existent_h323_gateway_fails(self):
        result = ucm.update_h323_gateway_mrgl('h323_not_exists', 'blah')

        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    def test_update_h323_gateway_media_resource_group_list_with_non_existent_media_resource_group_list_fails(self):
        h323_gateway = '2.2.2.2'
        ucm.add_h323_gateway(h323_gateway)

        result = ucm.update_h323_gateway_mrgl(h323_gateway, 'mrgl_not_exist')

        # clean up
        ucm.delete_h323_gateway(h323_gateway)

        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # Media resource group
    def test_add_media_resource_group_and_delete_media_resource_group_is_successful(self):
        media_resource_group = 'test_mrg'
        add_media_resource_group = ucm.add_media_resource_group(media_resource_group)
        del_media_resource_group = ucm.delete_media_resource_group(media_resource_group)

        self.assertEqual(add_media_resource_group['success'], True) and \
        self.assertEqual(del_media_resource_group['success'], True)

    def test_add_duplicate_media_resource_group_fails(self):
            media_resource_group = 'test_dup_mrg'
            ucm.add_media_resource_group(media_resource_group)
            duplicate = ucm.add_media_resource_group(media_resource_group)

            # clean up
            ucm.delete_media_resource_group(media_resource_group)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_media_resource_group_fails(self):
        media_resource_group = 'mrg_not_exist'
        result = ucm.delete_media_resource_group(media_resource_group)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # Media resource group list
    def test_add_media_resource_group_list_and_delete_media_resource_group_list_is_successful(self):
        media_resource_group_list = 'test_mrgl'
        add_media_resource_group_list = ucm.add_media_resource_group_list(media_resource_group_list)
        del_media_resource_group_list = ucm.delete_media_resource_group_list(media_resource_group_list)

        self.assertEqual(add_media_resource_group_list['success'], True) and \
        self.assertEqual(del_media_resource_group_list['success'], True)

    def test_add_duplicate_media_resource_group_list_fails(self):
            media_resource_group_list = 'test_dup_mrgl'
            ucm.add_media_resource_group_list(media_resource_group_list)
            duplicate = ucm.add_media_resource_group_list(media_resource_group_list)

            # clean up
            ucm.delete_media_resource_group_list(media_resource_group_list)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_media_resource_group_list_fails(self):
        media_resource_group_list = 'mrgl_not_exist'
        result = ucm.delete_media_resource_group_list(media_resource_group_list)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # Route group
    def test_add_route_group_and_delete_route_group_is_successful(self):
        route_group = 'test_route_group'
        add_route_group = ucm.add_route_group(route_group)
        del_route_group = ucm.delete_route_group(route_group)

        self.assertEqual(add_route_group['success'], True) and self.assertEqual(del_route_group['success'], True)

    def test_add_route_group_fails(self):
            route_group = 'test_dup_rg'
            ucm.add_route_group(route_group)
            duplicate = ucm.add_route_group(route_group)

            # clean up
            ucm.delete_route_group(route_group)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_route_group_fails(self):
        route_group = 'route_group_not_exist'
        result = ucm.delete_route_group(route_group)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # Directory number
    def test_add_directory_number_and_delete_directory_number_is_successful(self):
        directory_number = '12345678'
        add_directory_number = ucm.add_directory_number(directory_number)
        del_directory_number = ucm.delete_directory_number(directory_number)

        self.assertEqual(add_directory_number['success'], True) and \
        self.assertEqual(del_directory_number['success'], True)

    def test_add_directory_number_fails(self):
            directory_number = '9876543210'
            ucm.add_directory_number(directory_number)
            duplicate = ucm.add_directory_number(directory_number)

            # clean up
            ucm.delete_directory_number(directory_number)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_directory_number_fails(self):
        directory_number = '987654321'
        result = ucm.delete_route_group(directory_number)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # CTI route point
    def test_add_cti_route_point_and_delete_cti_route_point_is_successful(self):
        cti_route_point = 'test_cti_rp'
        add_cti_route_point = ucm.add_cti_route_point(cti_route_point)
        del_cti_route_point = ucm.delete_cti_route_point(cti_route_point)

        self.assertEqual(add_cti_route_point['success'], True) and \
        self.assertEqual(del_cti_route_point['success'], True)

    def test_add_cti_route_point_fails(self):
            cti_route_point = 'test_dup_cti'
            ucm.add_cti_route_point(cti_route_point)
            duplicate = ucm.add_cti_route_point(cti_route_point)

            # clean up
            ucm.delete_cti_route_point(cti_route_point)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_cti_route_point_fails(self):
        cti_route_point = 'cti_non_exist'
        result = ucm.delete_cti_route_point(cti_route_point)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')

    # Phones
    def test_add_phone_and_delete_phone_is_successful(self):
        phone = 'sepaaaabbbbcccc'
        add_phone = ucm.add_phone(phone)
        del_phone = ucm.delete_phone(phone)

        self.assertEqual(add_phone['success'], True) and self.assertEqual(del_phone['success'], True)

    def test_add_phone_fails(self):
            phone = 'sepaaaabbbbdddd'
            ucm.add_phone(phone)
            duplicate = ucm.add_phone(phone)

            # clean up
            ucm.delete_phone(phone)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['msg'], 'already exists')

    def test_delete_non_existing_phone_fails(self):
        phone = 'sepaaaabbbbeeee'
        result = ucm.delete_phone(phone)
        self.assertEqual(result['success'], False) and self.assertIn(result['msg'], 'not found')