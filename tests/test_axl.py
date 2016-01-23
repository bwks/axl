"""
Unified Communications server will be required for these tests
Tests are performed against UCM 10.5.2
"""
import unittest

from axl.foley import AXL

# cucm = '10.10.11.14'
cucm = '192.168.200.10'
wsdl = 'file:///Users/brad/Documents/code/python/axl/axlsqltoolkit/schema/10.5/AXLAPI.wsdl'
ucm = AXL('admin', 'asdfpoiu', wsdl, cucm)


class TestAXL(unittest.TestCase):

    # Location
    def test_get_location_returns_successful_and_location_details(self):
        location = 'Hub_None'
        result = ucm.get_location(location)
        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], location)

    def test_get_locations_returns_all_location_details(self):
        result = ucm.get_locations(mini=False)
        self.assertIsInstance(result, list) and len(list) > 1 and self.assertIsInstance(result[0], dict)

    def test_get_locations_mini_returns_all_location_details_as_list_of_tuples(self):
        result = ucm.get_locations(mini=True)
        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

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

        self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_location_fails(self):
        location = 'location_not_exist'
        result = ucm.delete_location(location)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Region
    def test_get_region_returns_successful_and_region_details(self):
        region = 'Default'
        result = ucm.get_region(region)
        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], region)

    def test_get_regions_returns_all_region_details(self):
        result = ucm.get_regions(mini=False)
        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_regions_mini_returns_all_region_details_as_list_of_tuples(self):
        result = ucm.get_regions(mini=True)
        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_region_fails(self):
        region = 'region_not_exist'
        result = ucm.delete_region(region)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    def test_update_region_with_non_existent_region_fails(self):
        result = ucm.update_region('reg_not_exists', 'blah')

        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

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
    def test_get_srst_returns_successful_and_srst_details(self):
        srst = 'test_get_srst'
        ucm.add_srst(srst, '192.168.100.100')
        result = ucm.get_srst(srst)

        # clean up
        ucm.delete_srst('test_get_srst')

        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], srst)

    def test_get_srsts_returns_all_srst_details(self):
        result = ucm.get_srsts(mini=False)
        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_srsts_mini_returns_all_srst_details_as_list_of_tuples(self):
        result = ucm.get_srsts(mini=True)
        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_srst_fails(self):
        srst = 'srst_not_exist'
        result = ucm.delete_srst(srst)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Device Pool
    def test_get_device_pool_returns_successful_and_device_pool_details(self):
        device_pool = 'Default'
        result = ucm.get_device_pool(device_pool)

        # clean up
        ucm.delete_device_pool(device_pool)

        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], device_pool)

    def test_get_device_pools_returns_all_device_pool_details(self):
        result = ucm.get_device_pools(mini=False)
        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_device_pools_mini_returns_all_device_pool_details_as_list_of_tuples(self):
        result = ucm.get_device_pools(mini=True)
        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_device_pool_fails(self):
        device_pool = 'dp_dont_exist'
        result = ucm.delete_device_pool(device_pool)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

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

        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    def test_update_device_pool_rg_mrgl_with_non_existent_route_group_fails(self):
        device_pool = 'test_dpu_no_rg_dp'
        ucm.add_device_pool(device_pool)

        result = ucm.update_device_pool_rg_mrgl(device_pool, 'rg_not_exist', 'blah')

        # clean up
        ucm.delete_device_pool(device_pool)

        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    def test_update_device_pool_rg_mrgl_with_non_existent_media_resource_group_list_fails(self):
        device_pool = 'test_dpu_no_mrgl_dp'
        route_group = 'test_dpu_no_mrgl_rg'

        ucm.add_device_pool(device_pool)
        ucm.add_route_group(route_group)

        result = ucm.update_device_pool_rg_mrgl(device_pool, route_group, 'mrgl_not_exist')

        # clean up
        ucm.delete_route_group(route_group)
        ucm.delete_device_pool(device_pool)

        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Conference Bridge
    def test_get_conference_bridge_successful_and_conference_bridge_details(self):
        conference_bridge = 'test_get_cfb'
        ucm.add_conference_bridge(conference_bridge)
        result = ucm.get_conference_bridge(conference_bridge)

        # clean up
        ucm.delete_conference_bridge(conference_bridge)

        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], conference_bridge)

    def test_get_conference_bridges_returns_all_conference_bridge_details(self):
        result = ucm.get_conference_bridges(mini=False)
        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_conference_bridges_mini_returns_all_conference_bridge_details_as_list_of_tuples(self):
        result = ucm.get_conference_bridges(mini=True)
        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_conference_bridge_fails(self):
        conference_bridge = 'cfb_not_exist'
        result = ucm.delete_conference_bridge(conference_bridge)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Transcoder
    def test_get_transcoder_successful_and_transcoder_details(self):
        transcoder = 'test_get_tcdr'
        ucm.add_transcoder(transcoder)
        result = ucm.get_transcoder(transcoder)

        # clean up
        ucm.delete_transcoder(transcoder)

        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], transcoder)

    def test_get_transcoders_returns_all_transcoder_details(self):
        transcoder = 'test_get_tcdrs'
        ucm.add_transcoder(transcoder)
        result = ucm.get_transcoders(mini=False)

        # clean up
        ucm.delete_transcoder(transcoder)

        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_transcoders_mini_returns_all_transcoder_details_as_list_of_tuples(self):
        transcoder = 'test_get_tcdrs'
        ucm.add_transcoder(transcoder)
        result = ucm.get_transcoders(mini=True)

        # clean up
        ucm.delete_transcoder(transcoder)

        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_transcoder_fails(self):
        transcoder = 'trans_not_exist'
        result = ucm.delete_transcoder(transcoder)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # H323 Gateway
    def test_get_h323_gateway_successful_and_h323_gateway_details(self):
        h323_gateway = '192.168.100.111'
        ucm.add_h323_gateway(h323_gateway)
        result = ucm.get_h323_gateway(h323_gateway)

        # clean up
        ucm.delete_h323_gateway(h323_gateway)

        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], h323_gateway)

    def test_get_h323_gateways_returns_all_h323_gateway_details(self):
        h323_gateway = '192.168.100.112'
        ucm.add_h323_gateway(h323_gateway)
        result = ucm.get_h323_gateways(mini=False)

        # clean up
        ucm.delete_h323_gateway(h323_gateway)

        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_h323_gateways_mini_returns_all_h323_gateway_details_as_list_of_tuples(self):
        h323_gateway = '192.168.100.113'
        ucm.add_h323_gateway(h323_gateway)
        result = ucm.get_h323_gateways(mini=True)

        # clean up
        ucm.delete_h323_gateway(h323_gateway)

        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_h323_gateway_fails(self):
        h323_gateway = '6.6.6.6'
        result = ucm.delete_h323_gateway(h323_gateway)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

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

        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    def test_update_h323_gateway_media_resource_group_list_with_non_existent_media_resource_group_list_fails(self):
        h323_gateway = '2.2.2.2'
        ucm.add_h323_gateway(h323_gateway)

        result = ucm.update_h323_gateway_mrgl(h323_gateway, 'mrgl_not_exist')

        # clean up
        ucm.delete_h323_gateway(h323_gateway)

        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Media resource group
    def test_get_media_resource_group_successful_and_media_resource_group_details(self):
        media_resource_group = 'test_get_mrg'
        ucm.add_media_resource_group(media_resource_group)
        result = ucm.get_media_resource_group(media_resource_group)

        # clean up
        ucm.delete_media_resource_group(media_resource_group)

        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], media_resource_group)

    def test_get_media_resource_groups_returns_all_media_resource_group_details(self):
        media_resource_group = 'test_get_mrgs'
        ucm.add_media_resource_group(media_resource_group)
        result = ucm.get_media_resource_groups(mini=False)

        # clean up
        ucm.delete_media_resource_group(media_resource_group)

        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_media_resource_groups_mini_returns_all_media_resource_group_details_as_list_of_tuples(self):
        media_resource_group = 'test_get_mrgs'
        ucm.add_media_resource_group(media_resource_group)
        result = ucm.get_media_resource_groups(mini=True)

        # clean up
        ucm.delete_media_resource_group(media_resource_group)

        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)
        
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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_media_resource_group_fails(self):
        media_resource_group = 'mrg_not_exist'
        result = ucm.delete_media_resource_group(media_resource_group)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Media resource group list
    def test_get_media_resource_group_list_successful_and_media_resource_group_list_details(self):
        media_resource_group_list = 'test_get_mrgl'
        ucm.add_media_resource_group_list(media_resource_group_list)
        result = ucm.get_media_resource_group_list(media_resource_group_list)

        # clean up
        ucm.delete_media_resource_group_list(media_resource_group_list)

        self.assertEqual(result['success'], True) and \
        self.assertEqual(result['response']['name'], media_resource_group_list)

    def test_get_media_resource_group_lists_returns_all_media_resource_group_list_details(self):
        media_resource_group_list = 'test_get_mrgls'
        ucm.add_media_resource_group_list(media_resource_group_list)
        result = ucm.get_media_resource_group_lists(mini=False)

        # clean up
        ucm.delete_media_resource_group_list(media_resource_group_list)

        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_media_resource_group_lists_mini_returns_all_media_resource_lists_details_as_list_of_tuples(self):
        media_resource_group_list = 'test_get_mrgls'
        ucm.add_media_resource_group_list(media_resource_group_list)
        result = ucm.get_media_resource_group_lists(mini=True)

        # clean up
        ucm.delete_media_resource_group_list(media_resource_group_list)

        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_media_resource_group_list_fails(self):
        media_resource_group_list = 'mrgl_not_exist'
        result = ucm.delete_media_resource_group_list(media_resource_group_list)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_route_group_fails(self):
        route_group = 'route_group_not_exist'
        result = ucm.delete_route_group(route_group)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Partition
    def test_get_partition_successful_and_partition_details(self):
        partition = 'Global Learned Enterprise Numbers'
        result = ucm.get_partition(partition)

        self.assertEqual(result['success'], True) and \
        self.assertEqual(result['response']['name'], partition)

    def test_get_partitions_returns_all_partition_details(self):
        partition = 'Global Learned Enterprise Numbers'
        result = ucm.get_partitions(mini=False)

        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_partitions_mini_returns_all_media_resource_lists_details_as_list_of_tuples(self):
        result = ucm.get_partitions(mini=True)

        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

    def test_add_partition_and_delete_partition_is_successful(self):
        partition = 'test_pt'
        add_partition = ucm.add_partition(partition)
        del_partition = ucm.delete_partition(partition)

        self.assertEqual(add_partition['success'], True) and \
        self.assertEqual(del_partition['success'], True)

    def test_add_duplicate_partition_fails(self):
            partition = 'test_pt_dup'
            ucm.add_partition(partition)
            duplicate = ucm.add_partition(partition)

            # clean up
            ucm.delete_partition(partition)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_partition_fails(self):
        partition = 'test_pt_none'
        result = ucm.delete_partition(partition)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Calling search space
    def test_get_calling_search_space_successful_and_calling_search_space_details(self):
        calling_search_space = 'test_get_css'
        ucm.add_calling_search_space(calling_search_space)
        result = ucm.get_calling_search_space(calling_search_space)

        # Cleanup
        ucm.delete_calling_search_space(calling_search_space)

        self.assertEqual(result['success'], True) and \
        self.assertEqual(result['response']['name'], calling_search_space)

    def test_get_calling_search_spaces_returns_all_calling_search_space_details(self):
        calling_search_space = 'test_get_all_css'
        ucm.add_calling_search_space(calling_search_space)
        result = ucm.get_calling_search_spaces(mini=False)

        # Cleanup
        ucm.delete_calling_search_space(calling_search_space)

        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_calling_search_spaces_mini_returns_all_media_resource_lists_details_as_list_of_tuples(self):
        calling_search_space = 'test_get_mini_css'
        ucm.add_calling_search_space(calling_search_space)
        result = ucm.get_calling_search_spaces(mini=True)

        # Cleanup
        ucm.delete_calling_search_space(calling_search_space)

        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

    def test_add_calling_search_space_and_delete_calling_search_space_is_successful(self):
        calling_search_space = 'test_css'
        add_calling_search_space = ucm.add_calling_search_space(calling_search_space)
        del_calling_search_space = ucm.delete_calling_search_space(calling_search_space)

        self.assertEqual(add_calling_search_space['success'], True) and \
        self.assertEqual(del_calling_search_space['success'], True)

    def test_add_duplicate_calling_search_space_fails(self):
            calling_search_space = 'test_css_dup'
            ucm.add_calling_search_space(calling_search_space)
            duplicate = ucm.add_calling_search_space(calling_search_space)

            # clean up
            ucm.delete_calling_search_space(calling_search_space)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_calling_search_space_fails(self):
        calling_search_space = 'test_css_none'
        result = ucm.delete_calling_search_space(calling_search_space)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Directory number
    def test_get_directory_number_successful_and_directory_number_details(self):
        directory_number = '999999'
        ucm.add_directory_number(directory_number)
        result = ucm.get_directory_number(directory_number)

        # clean up
        ucm.delete_directory_number(directory_number)

        self.assertEqual(result['success'], True) and \
        self.assertEqual(result['response']['name'], directory_number)

    def test_get_directory_numbers_returns_all_directory_number_details(self):
        directory_number = '888888'
        ucm.add_directory_number(directory_number)
        result = ucm.get_directory_numbers(mini=False)

        # clean up
        ucm.delete_directory_number(directory_number)

        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_directory_numbers_mini_returns_all_media_resource_lists_details_as_list_of_tuples(self):
        directory_number = '777777'
        ucm.add_directory_number(directory_number)
        result = ucm.get_directory_numbers(mini=True)

        # clean up
        ucm.delete_directory_number(directory_number)

        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)
        
    def test_add_directory_number_and_delete_directory_number_is_successful(self):
        directory_number = '12345678'
        add_directory_number = ucm.add_directory_number(directory_number)
        del_directory_number = ucm.delete_directory_number(directory_number)

        self.assertEqual(add_directory_number['success'], True) and \
        self.assertEqual(del_directory_number['success'], True)

    def test_add_duplicate_directory_number_fails(self):
            directory_number = '9876543210'
            ucm.add_directory_number(directory_number)
            duplicate = ucm.add_directory_number(directory_number)

            # clean up
            ucm.delete_directory_number(directory_number)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_directory_number_fails(self):
        directory_number = '987654321'
        result = ucm.delete_directory_number(directory_number)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # CTI route point
    def test_get_cti_route_point_successful_and_cti_route_point_details(self):
        cti_route_point = 'test_get_ctirp'
        ucm.add_cti_route_point(cti_route_point, 'Default')
        result = ucm.get_cti_route_point(cti_route_point)

        # clean up
        ucm.delete_cti_route_point(cti_route_point)

        self.assertEqual(result['success'], True) and \
        self.assertEqual(result['response']['name'], cti_route_point)

    def test_get_cti_route_points_returns_all_cti_route_point_details(self):
        cti_route_point = 'test_get_ctirp'
        ucm.add_cti_route_point(cti_route_point, 'Default')
        result = ucm.get_cti_route_points(mini=False)

        # clean up
        ucm.delete_cti_route_point(cti_route_point)

        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_cti_route_points_mini_returns_all_media_resource_lists_details_as_list_of_tuples(self):
        cti_route_point = 'test_get_ctirp'
        ucm.add_cti_route_point(cti_route_point, 'Default')
        result = ucm.get_cti_route_points(mini=True)

        # clean up
        ucm.delete_cti_route_point(cti_route_point)

        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

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

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_cti_route_point_fails(self):
        cti_route_point = 'cti_non_exist'
        result = ucm.delete_cti_route_point(cti_route_point)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Phones
    def test_get_phone_successful_and_phone_details(self):
        phone = 'sepffffffffffff'
        ucm.add_phone(phone)
        result = ucm.get_phone(phone)

        # clean up
        ucm.delete_phone(phone)

        self.assertEqual(result['success'], True) and \
        self.assertEqual(result['response']['name'], phone)

    def test_get_phones_returns_all_phone_details(self):
        phone = 'sepeeeeeeeeeeee'
        ucm.add_phone(phone)
        result = ucm.get_phones(mini=False)

        # clean up
        ucm.delete_phone(phone)

        self.assertIsInstance(result, list) and len(list) > 0 and self.assertIsInstance(result[0], dict)

    def test_get_phones_mini_returns_all_media_resource_lists_details_as_list_of_tuples(self):
        phone = 'sepdddddddddddd'
        ucm.add_phone(phone)
        result = ucm.get_phones(mini=True)

        # clean up
        ucm.delete_phone(phone)

        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

    def test_add_phone_and_delete_phone_is_successful(self):
        phone = 'sepaaaabbbbcccc'
        add_phone = ucm.add_phone(phone)
        del_phone = ucm.delete_phone(phone)

        self.assertEqual(add_phone['success'], True) and self.assertEqual(del_phone['success'], True)

    def test_add_duplicate_phone_fails(self):
            phone = 'sepaaaabbbbdddd'
            ucm.add_phone(phone)
            duplicate = ucm.add_phone(phone)

            # clean up
            ucm.delete_phone(phone)

            self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_phone_fails(self):
        phone = 'sepaaaabbbbeeee'
        result = ucm.delete_phone(phone)
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    # Device Profiles
    def test_add_device_profile_and_delete_device_profile_is_successful(self):
        profile = 'test_profile'
        add_profile = ucm.add_device_profile(profile)
        del_profile = ucm.delete_device_profile(profile)

        self.assertEqual(add_profile['success'], True) and self.assertEqual(del_profile['success'], True)

    def test_add_duplicate_device_profile_fails(self):
        profile = 'test_dup_profile'
        ucm.add_device_profile(profile)
        duplicate = ucm.add_device_profile(profile)

        # clean up
        ucm.delete_device_profile(profile)

        self.assertEqual(duplicate['success'], False) and self.assertIn(duplicate['response'], 'already exists')

    def test_delete_non_existing_device_profile_fails(self):
        result = ucm.delete_device_profile('profile-not-exist')
        self.assertEqual(result['success'], False) and self.assertIn(result['response'], 'not found')

    def test_get_device_profile_returns_successful_and_device_profile_details(self):
        profile = 'test_get_profile'
        ucm.add_device_profile(profile)
        result = ucm.get_device_profile(profile)

        # clean up
        ucm.delete_device_profile(profile)

        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], profile)

    def test_get_device_profiles_returns_all_device_profiles_details(self):
        result = ucm.get_device_profiles(mini=False)
        self.assertIsInstance(result, list) and len(list) > 1 and self.assertIsInstance(result[0], dict)

    def test_get_device_profiles_mini_returns_all_device_profiles_details_as_list_of_tuples(self):
        result = ucm.get_device_profiles(mini=True)
        self.assertIsInstance(result, list) and self.assertIsInstance(result[0], tuple)

    # Users
    def test_get_users_returns_all_users_details(self):
        result = ucm.get_device_profiles(mini=False)
        self.assertIsInstance(result, list) and len(list) > 1 and self.assertIsInstance(result[0], dict)

    def test_get_user_returns_successful_and_user_details(self):
        user = 'test_get_user'
        ucm.add_user(user, 'last_name')
        result = ucm.get_user(user)

        # clean up
        ucm.delete_user(user)

        self.assertEqual(result['success'], True) and self.assertEqual(result['response']['name'], user)
