"""
Class to interface with cisco ucm axl api.
Author: Brad Searle
Version: 0.2.5
Dependencies:
 - suds-jurko: https://bitbucket.org/jurko/suds

Links:
 - http://www.imdb.com/character/ch0005280/
 - https://developer.cisco.com/site/axl/
"""

import ssl
import urllib

from suds.transport.https import HttpAuthenticated
from suds.client import Client

from suds.xsd.doctor import Import
from suds.xsd.doctor import ImportDoctor


class AXL(object):
    """
    The AXL Class sets up the connection to the call manager.
    Tested with environment of;
    Centos 7, Python 3, suds-jurko.
    Your mileage may vary.
    """

    def __init__(self, username, password, wsdl, cucm, cucm_version=10):
        """
        :param username: axl username
        :param password: axl password
        :param wsdl: wsdl file location
        :param cucm: UCM IP address
        :param cucm_version: UCM version
        :return:

        example usage:
        >>> from axl.foley import AXL
        >>> wsdl = 'file:///path/to/wsdl/axlsqltoolkit/schema/10.5/AXLAPI.wsdl'
        >>> ucm = AXL('axl_user', 'axl_pass' wsdl, '192.168.200.10')
        """
        self.username = username
        self.password = password
        self.wsdl = wsdl
        self.cucm = cucm
        self.cucm_version = cucm_version

        tns = 'http://schemas.cisco.com/ast/soap/'
        imp = Import('http://schemas.xmlsoap.org/soap/encoding/', 'http://schemas.xmlsoap.org/soap/encoding/')
        imp.filter.add(tns)

        t = HttpAuthenticated(username=self.username, password=self.password)
        t.handler = urllib.request.HTTPBasicAuthHandler(t.pm)

        ssl_def_context = ssl.create_default_context()
        ssl_def_context.check_hostname = False
        ssl_def_context.verify_mode = ssl.CERT_NONE

        t1 = urllib.request.HTTPSHandler(context=ssl_def_context)
        t.urlopener = urllib.request.build_opener(t.handler, t1)

        self.client = Client(self.wsdl, location='https://{0}:8443/axl/'.format(cucm), faults=False,
                             plugins=[ImportDoctor(imp)],
                             transport=t)

    def get_locations(self, mini=True):
        """
        Get location details
        :param mini: return a list of tuples of location details
        :return: A list of dictionary's
        """
        resp = self.client.service.listLocation(
                {'name': '%'}, returnedTags={
                    'name': '',
                    'withinAudioBandwidth': '',
                    'withinVideoBandwidth': '',
                    'withinImmersiveKbits': '',
                })[1]['return']['location']
        if mini:
            return [(i['name'],
                     i['withinAudioBandwidth'],
                     i['withinVideoBandwidth'],
                     i['withinImmersiveKbits'],
                     ) for i in resp]
        else:
            return resp

    def get_location(self, location):
        """
        Get device pool parameters
        :param location: location name
        :return: result dictionary
        """
        resp = self.client.service.getLocation(name=location)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['location']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Location: {0} not found'.format(location)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_location(self,
                     location,
                     kbits=512,
                     video_kbits=-1,
                     within_audio_bw=512,
                     within_video_bw=-1,
                     within_immersive_kbits=-1):

        """
        Add a location
        :param location: Name of the location to add
        :param cucm_version: ucm version
        :param kbits: ucm 8.5
        :param video_kbits: ucm 8.5
        :param within_audio_bw: ucm 10
        :param within_video_bw: ucm 10
        :param within_immersive_kbits: ucm 10
        :return: result dictionary
        """
        if self.cucm_version == 10:

            resp = self.client.service.addLocation({
                'name': location,
                # CUCM 10.6
                'withinAudioBandwidth': within_audio_bw,
                'withinVideoBandwidth': within_video_bw,
                'withinImmersiveKbits': within_immersive_kbits,
            })

        else:

            resp = self.client.service.addLocation({
                'name': location,
                # CUCM 8.6
                'kbits': kbits,
                'videoKbits': video_kbits,
            })

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Location successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Location already exists'.format(location)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Location could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_location(self, location):
        """
        Delete a location
        :param location: The name of the location to delete
        :return: result dictionary
        """
        resp = self.client.service.removeLocation(name=location)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Location successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Location: {0} not found'.format(location)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Location could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_regions(self, mini=True):
        """
        Get region details
        :param mini: return a list of tuples of region details
        :return: A list of dictionary's
        """
        resp = self.client.service.listRegion(
                {'name': '%'}, returnedTags={'_uuid'})[1]['return']['region']
        if mini:
            return [(i['_uuid'][1:-1]) for i in resp]
        else:
            return resp

    def get_region(self, region):
        """
        Get region information
        :param region: Region name
        :return: result dictionary
        """
        resp = self.client.service.getRegion(name=region)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['region']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Region: {0} not found'.format(region)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_region(self, region):
        """
        Add a region
        :param region: Name of the region to add
        :return: result dictionary
        """
        resp = self.client.service.addRegion({
            'name': region
        })

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Region successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Region already exists'.format(region)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Region could not be added'
            result['error'] = resp[1].faultstring
            return result

    def update_region(self, region, moh_region=''):
        """
        Update region and assign region to all other regions
        :param region:
        :param moh_region:
        :return:
        """
        # Get all Regions
        all_regions = self.client.service.listRegion({'name': '%'}, returnedTags={'name': ''})

        # Make list of region names
        region_names = [str(i['name']) for i in all_regions[1]['return']['region']]

        # Build list of dictionaries to add to region api call
        region_list = []

        for i in region_names:
            # Highest codec within a region
            if i == region:
                region_list.append({
                    'regionName': i,
                    'bandwidth': '256 kbps',
                    'videoBandwidth': '-1',
                    'immersiveVideoBandwidth': '-1',
                    'lossyNetwork': 'Use System Default',
                })

            # Music on hold region name
            elif i == moh_region:
                region_list.append({
                    'regionName': i,
                    'bandwidth': '64 kbps',
                    'videoBandwidth': '-1',
                    'immersiveVideoBandwidth': '-1',
                    'lossyNetwork': 'Use System Default',
                })

            # All else G.711
            else:
                region_list.append({
                    'regionName': i,
                    'bandwidth': '64 kbps',
                    'videoBandwidth': '-1',
                    'immersiveVideoBandwidth': '-1',
                    'lossyNetwork': 'Use System Default',
                })

        resp = self.client.service.updateRegion(name=region,
                                                relatedRegions={'relatedRegion': region_list})

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Region successfully updated'
            return result
        elif resp[0] == 500 and '{0} was not found'.format(region) in resp[1].faultstring:
            result['response'] = 'Region: {0} not found'.format(region)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Region could not be updated'
            result['error'] = resp[1].faultstring
            return result

    def delete_region(self, region):
        """
        Delete a location
        :param region: The name of the region to delete
        :return: result dictionary
        """
        resp = self.client.service.removeRegion(name=region)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Region successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Region: {0} not found'.format(region)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Region could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_srsts(self, mini=True):
        """
        Get all SRST details
        :param mini: return a list of tuples of SRST details
        :return: A list of dictionary's
        """
        resp = self.client.service.listSrst(
                {'name': '%'}, returnedTags={'_uuid': ''})[1]['return']['srst']
        if mini:
            return [(i['_uuid'][1:-1]) for i in resp]
        else:
            return resp

    def get_srst(self, srst):
        """
        Get SRST information
        :param srst: SRST name
        :return: result dictionary
        """
        resp = self.client.service.getSrst(name=srst)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['srst']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'SRST: {0} not found'.format(srst)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_srst(self, srst, ip_address, port=2000, sip_port=5060):
        """
        Add SRST
        :param srst: SRST name
        :param ip_address: SRST ip address
        :param port: SRST port
        :param sip_port: SIP port
        :return: result dictionary
        """
        resp = self.client.service.addSrst({
            'name': srst,
            'port': port,
            'ipAddress': ip_address,
            'SipPort': sip_port,
        })

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'SRST successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'SRST already exists'.format(srst)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'SRST could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_srst(self, srst):
        """
        Delete a SRST
        :param srst: The name of the SRST to delete
        :return: result dictionary
        """
        resp = self.client.service.removeSrst(name=srst)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'SRST successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'SRST: {0} not found'.format(srst)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'SRST could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_device_pools(self, mini=True):
        """
        Get a dictionary of device pools
        :param mini: return a list of tuples of device pool info
        :return: a list of dictionary's of device pools information
        """
        resp = self.client.service.listDevicePool(
                {'name': '%'}, returnedTags={
                    'name': '',
                    'dateTimeSettingName': '',
                    'callManagerGroupName': '',
                    'mediaResourceListName': '',
                    'regionName': '',
                    'srstName': '',
                    # 'localRouteGroup': [0],
                })[1]['return']['devicePool']
        if mini:
            return [(i['name'],
                     i['dateTimeSettingName']['value'],
                     i['callManagerGroupName']['value'],
                     i['regionName']['value'],
                     i['srstName']['value'],
                     # i['localRouteGroup'][0]['value'],
                     ) for i in resp]
        else:
            return resp

    def get_device_pool(self, device_pool):
        """
        Get device pool parameters
        :param device_pool: device pool name
        :return: result dictionary
        """
        resp = self.client.service.getDevicePool(name=device_pool)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['devicePool']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Device pool: {0} not found'.format(device_pool)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_device_pool(self,
                        device_pool,
                        date_time_group='CMLocal',
                        region='Default',
                        location='',
                        srst='Disable',
                        cm_group='Default',
                        network_locale='Australia'):

        """
        Add a device pool
        :param device_pool: Device pool name
        :param date_time_group: Date time group name
        :param region: Region name
        :param location: Location name
        :param srst: SRST name
        :param cm_group: CM Group name
        :param network_locale: Network locale name
        :return: result dictionary
        """
        resp = self.client.service.addDevicePool({
            'name': device_pool,
            'dateTimeSettingName': date_time_group,  # update to state timezone
            'regionName': region,
            'locationName': location,
            'srstName': srst,
            'callManagerGroupName': cm_group,
            'networkLocale': network_locale,
        })

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Device pool successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Device pool already exists'.format(srst)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Device pool could not be added'
            result['error'] = resp[1].faultstring
            return result

    def update_device_pool_rg_mrgl(self, device_pool, route_group, media_resource_group_list):
        """
        Update a device pools route group and media resource group list
        :param device_pool:
        :param route_group:
        :param media_resource_group_list:
        :return:
        """
        resp = self.client.service.updateDevicePool(
                name=device_pool,
                localRouteGroup={'name': 'Standard Local Route Group', 'value': route_group},
                mediaResourceListName=media_resource_group_list
        )

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Device pool successfully updated'
            return result
        elif resp[0] == 500 and '{0} was not found'.format(device_pool) in resp[1].faultstring:
            result['response'] = 'Device pool: {0} not found'.format(device_pool)
            result['error'] = resp[1].faultstring
            return result
        elif resp[0] == 500 and '{0} was not found'.format(route_group) in resp[1].faultstring:
            result['response'] = 'Route group: {0} not found'.format(route_group)
            result['error'] = resp[1].faultstring
            return result
        elif resp[0] == 500 and '{0} was not found'.format(media_resource_group_list) in resp[1].faultstring:
            result['response'] = 'Media resource group list: {0} not found'.format(media_resource_group_list)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Device pool could not be updated'
            result['error'] = resp[1].faultstring
            return result

    def delete_device_pool(self, device_pool):
        """
        Delete a Device pool
        :param device_pool: The name of the Device pool to delete
        :return: result dictionary
        """
        resp = self.client.service.removeDevicePool(name=device_pool)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Device pool successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Device pool: {0} not found'.format(device_pool)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Device pool could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_conference_bridges(self, mini=True):
        """
        Get conference bridges
        :param mini: List of tuples of conference bridge details
        :return: results dictionary
        """
        resp = self.client.service.listConferenceBridge(
                {'name': '%'},
                returnedTags={'name': '',
                              'description': '',
                              'devicePoolName': '',
                              'locationName': ''})[1]['return']['conferenceBridge']

        if mini:
            return [(i['name'], i['description'], i['devicePoolName']['value'], i['locationName']['value'])
                    for i in resp]
        else:
            return resp

    def get_conference_bridge(self, conference_bridge):
        """
        Get conference bridge parameters
        :param conference_bridge: conference bridge name
        :return: result dictionary
        """
        resp = self.client.service.getConferenceBridge(name=conference_bridge)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['conferenceBridge']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Conference bridge: {0} not found'.format(conference_bridge)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_conference_bridge(self,
                              conference_bridge,
                              description='',
                              device_pool='Default',
                              location='Hub_None',
                              product='Cisco IOS Enhanced Conference Bridge',
                              security_profile='Non Secure Conference Bridge'):
        """
        Add a conference bridge
        :param conference_bridge: Conference bridge name
        :param description: Conference bridge description
        :param device_pool: Device pool name
        :param location: Location name
        :param product: Conference bridge type
        :param security_profile: Conference bridge security type
        :return: result dictionary
        """
        resp = self.client.service.addConferenceBridge({
            'name': conference_bridge,
            'description': description,
            'devicePoolName': device_pool,
            'locationName': location,
            'product': product,
            'securityProfileName': security_profile
        })

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Conference bridge successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Conference bridge already exists'.format(conference_bridge)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Conference bridge could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_conference_bridge(self, conference_bridge):
        """
        Delete a Conference bridge
        :param conference_bridge: The name of the Conference bridge to delete
        :return: result dictionary
        """
        resp = self.client.service.removeConferenceBridge(name=conference_bridge)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Conference bridge successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Conference bridge: {0} not found'.format(conference_bridge)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Conference bridge could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_transcoders(self, mini=True):
        """
        Get transcoders
        :param mini: List of tuples of transcoder details
        :return: results dictionary
        """
        resp = self.client.service.listTranscoder(
                {'name': '%'},
                returnedTags={'name': '',
                              'description': '',
                              'devicePoolName': ''})[1]['return']['transcoder']

        if mini:
            return [(i['name'], i['description'], i['devicePoolName']['value']) for i in resp]
        else:
            return resp

    def get_transcoder(self, transcoder):
        """
        Get conference bridge parameters
        :param transcoder: conference bridge name
        :return: result dictionary
        """
        resp = self.client.service.getTranscoder(name=transcoder)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['transcoder']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Transcoder: {0} not found'.format(transcoder)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_transcoder(self,
                       transcoder,
                       description='',
                       device_pool='Default',
                       product='Cisco IOS Enhanced Media Termination Point'):
        """
        Add a transcoder
        :param transcoder: Transcoder name
        :param description: Transcoder description
        :param device_pool: Transcoder device pool
        :param product: Trancoder product
        :return: result dictionary
        """
        resp = self.client.service.addTranscoder({
            'name': transcoder,
            'description': description,
            'devicePoolName': device_pool,
            'product': product,
        })

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Conference bridge successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Conference bridge already exists'.format(transcoder)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Conference bridge could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_transcoder(self, transcoder):
        """
        Delete a Transcoder
        :param transcoder: The name of the Transcoder to delete
        :return: result dictionary
        """
        resp = self.client.service.removeTranscoder(name=transcoder)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Transcoder successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Transcoder: {0} not found'.format(transcoder)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Transcoder could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_h323_gateways(self, mini=True):
        """
        Get H323 Gateways
        :param mini: List of tuples of H323 Gateway details
        :return: results dictionary
        """
        resp = self.client.service.listH323Gateway(
                {'name': '%'},
                returnedTags={'name': '',
                              'description': '',
                              'devicePoolName': '',
                              'locationName': '',
                              'sigDigits': ''})[1]['return']['h323Gateway']

        if mini:
            return [(i['name'],
                     i['description'],
                     i['devicePoolName']['value'],
                     i['locationName']['value'],
                     i['sigDigits']['value']) for i in resp]
        else:
            return resp

    def get_h323_gateway(self, h323_gateway):
        """
        Get H323 Gateway parameters
        :param h323_gateway: H323 Gateway name
        :return: result dictionary
        """
        resp = self.client.service.getH323Gateway(name=h323_gateway)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['h323Gateway']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'H323 Gateway: {0} not found'.format(h323_gateway)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_h323_gateway(self,
                         h323_gateway,
                         description='',
                         device_pool='Default',
                         location='Hub_None',
                         prefix_dn='',
                         sig_digits='99',
                         css='',
                         aar_css='',
                         aar_neighborhood='',
                         product='H.323 Gateway',
                         protocol='H.225',
                         protocol_side='Network',
                         pstn_access='true',
                         redirect_in_num_ie='false',
                         redirect_out_num_ie='false',
                         cld_party_ie_num_type='Unknown',
                         clng_party_ie_num_type='Unknown',
                         clng_party_nat_pre='',
                         clng_party_inat_prefix='',
                         clng_party_unknown_prefix='',
                         clng_party_sub_prefix='',
                         clng_party_nat_strip_digits='',
                         clng_party_inat_strip_digits='',
                         clng_party_unknown_strip_digits='',
                         clng_party_sub_strip_digits='',
                         clng_party_nat_trans_css='',
                         clng_party_inat_trans_css='',
                         clng_party_unknown_trans_css='',
                         clng_party_sub_trans_css=''):
        """
        Add H323 gateway
        :param h323_gateway:
        :param description:
        :param device_pool:
        :param location:
        :param prefix_dn:
        :param sig_digits: Significant digits, 99 = ALL
        :param css:
        :param aar_css:
        :param aar_neighborhood:
        :param product:
        :param protocol:
        :param protocol_side:
        :param pstn_access:
        :param redirect_in_num_ie:
        :param redirect_out_num_ie:
        :param cld_party_ie_num_type:
        :param clng_party_ie_num_type:
        :param clng_party_nat_pre:
        :param clng_party_inat_prefix:
        :param clng_party_unknown_prefix:
        :param clng_party_sub_prefix:
        :param clng_party_nat_strip_digits:
        :param clng_party_inat_strip_digits:
        :param clng_party_unknown_strip_digits:
        :param clng_party_sub_strip_digits:
        :param clng_party_nat_trans_css:
        :param clng_party_inat_trans_css:
        :param clng_party_unknown_trans_css:
        :param clng_party_sub_trans_css:
        :return:
        """
        resp = self.client.service.addH323Gateway({
            'name': h323_gateway,
            'description': description,
            'product': product,
            'protocol': protocol,
            'protocolSide': protocol_side,
            'callingSearchSpaceName': css,
            'automatedAlternateRoutingCssName': aar_css,
            'devicePoolName': device_pool,
            'locationName': location,
            'aarNeighborhoodName': aar_neighborhood,
            'pstnAccess': pstn_access,
            'sigDigits': sig_digits,
            'prefixDn': prefix_dn,
            'redirectInboundNumberIe': redirect_in_num_ie,
            'redirectOutboundNumberIe': redirect_out_num_ie,
            'calledPartyIeNumberType': cld_party_ie_num_type,
            'callingPartyIeNumberType': clng_party_ie_num_type,
            'callingPartyNationalPrefix': clng_party_nat_pre,
            'callingPartyInternationalPrefix': clng_party_inat_prefix,
            'callingPartyUnknownPrefix': clng_party_unknown_prefix,
            'callingPartySubscriberPrefix': clng_party_sub_prefix,
            'callingPartyNationalStripDigits': clng_party_nat_strip_digits,
            'callingPartyInternationalStripDigits': clng_party_inat_strip_digits,
            'callingPartyUnknownStripDigits': clng_party_unknown_strip_digits,
            'callingPartySubscriberStripDigits': clng_party_sub_strip_digits,
            'callingPartyNationalTransformationCssName': clng_party_nat_trans_css,
            'callingPartyInternationalTransformationCssName': clng_party_inat_trans_css,
            'callingPartyUnknownTransformationCssName': clng_party_unknown_trans_css,
            'callingPartySubscriberTransformationCssName': clng_party_sub_trans_css
        })

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'H323 gateway successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'H323 gateway already exists'.format(h323_gateway)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'H323 gateway could not be added'
            result['error'] = resp[1].faultstring
            return result

    def update_h323_gateway_mrgl(self, h323_gateway, media_resource_group_list):
        """

        :param h323_gateway:
        :param media_resource_group_list:
        :return:
        """
        resp = self.client.service.updateH323Gateway(
                name=h323_gateway,
                mediaResourceListName=media_resource_group_list,
        )

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'H323 gateway successfully updated'
            return result
        elif resp[0] == 500 and '{0} was not found'.format(h323_gateway) in resp[1].faultstring:
            result['response'] = 'H323 gateway: {0} not found'.format(h323_gateway)
            result['error'] = resp[1].faultstring
            return result
        elif resp[0] == 500 and '{0} was not found'.format(media_resource_group_list) in resp[1].faultstring:
            result['response'] = 'Media resource group list: {0} not found'.format(media_resource_group_list)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'H323 gateway could not be updated'
            result['error'] = resp[1].faultstring
            return result

    def delete_h323_gateway(self, h323_gateway):
        """
        Delete a H323 gateway
        :param h323_gateway: The name of the H323 gateway to delete
        :return: result dictionary
        """
        resp = self.client.service.removeH323Gateway(name=h323_gateway)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'H323 gateway successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'H323 gateway: {0} not found'.format(h323_gateway)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'H323 gateway could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_route_groups(self, mini=True):
        """
        Get route groups
        :param mini: return a list of tuples of route group details
        :return: A list of dictionary's
        """
        resp = self.client.service.listRouteGroup(
                {'name': '%'}, returnedTags={'name': '', 'distributionAlgorithm': ''})[1]['return']['routeGroup']
        if mini:
            return [(i['name'], i['distributionAlgorithm']) for i in resp]
        else:
            return resp

    def get_route_group(self, route_group):
        """
        Get route group
        :param route_group: route group name
        :return: result dictionary
        """
        resp = self.client.service.getRouteGroup(name=route_group)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['routeGroup']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Route group: {0} not found'.format(route_group)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_route_group(self,
                        route_group,
                        distribution_algorithm='Top Down',
                        members=[]):
        """
        Add a route group
        :param route_group: Route group name
        :param distribution_algorithm: Top Down/Circular
        :param members: A list of devices to add (must already exist DUH!)
        """
        req = {
            'name': route_group,
            'distributionAlgorithm': distribution_algorithm,
            'members': {'member': []},
        }

        if members:
            [req['members']['member'].append({
                'deviceName': i,
                'deviceSelectionOrder': members.index(i) + 1,
                'port': 0
            }) for i in members]

        resp = self.client.service.addRouteGroup(req)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Route group successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Route group already exists'.format(route_group)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Route group could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_route_group(self, route_group):
        """
        Delete a Route group
        :param route_group: The name of the Route group to delete
        :return: result dictionary
        """
        resp = self.client.service.removeRouteGroup(name=route_group)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Route group successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Route group: {0} not found'.format(route_group)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Route group could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_route_lists(self, mini=True):
        """
        Get route lists
        :param mini: return a list of tuples of route list details
        :return: A list of dictionary's
        """
        resp = self.client.service.listRoutelist(
                {'name': '%'}, returnedTags={'name': '', 'description': ''})[1]['return']['routeList']
        if mini:
            return [(i['name'], i['description']) for i in resp]
        else:
            return resp

    def get_route_list(self, route_list):
        """
        Get route list
        :param route_list: route list name
        :return: result dictionary
        """
        resp = self.client.service.getRouteList(name=route_list)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['routeList']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Route list: {0} not found'.format(route_list)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_route_list(self,
                       route_list,
                       description='',
                       cm_group_name='Default',
                       route_list_enabled='true',
                       run_on_all_nodes='false',
                       members=[]):

        """
        Add a route list
        :param route_list: Route list name
        :param description: Route list description
        :param cm_group_name: Route list call mangaer group name
        :param route_list_enabled: Enable route list
        :param run_on_all_nodes: Run route list on all nodes
        :param members: A list of route groups
        :return: Result dictionary
        """
        req = {
            'name': route_list,
            'description': description,
            'callManagerGroupName': cm_group_name,
            'routeListEnabled': route_list_enabled,
            'runOnEveryNode': run_on_all_nodes,
            'members': {'member': []},
        }

        if members:
            [req['members']['member'].append({
                'routeGroupName': i,
                'selectionOrder': members.index(i) + 1,
                'calledPartyTransformationMask': '',
                'callingPartyTransformationMask': '',
                'digitDiscardInstructionName': '',
                'callingPartyPrefixDigits': '',
                'prefixDigitsOut': '',
                'useFullyQualifiedCallingPartyNumber': 'Default',
                'callingPartyNumberingPlan': 'Cisco CallManager',
                'callingPartyNumberType': 'Cisco CallManager',
                'calledPartyNumberingPlan': 'Cisco CallManager',
                'calledPartyNumberType': 'Cisco CallManager',
            }) for i in members]

        resp = self.client.service.addRouteList(req)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Route list successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Route list already exists'.format(route_list)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Route list could not be added'
            result['error'] = resp[1].faultstring
            return result

    def get_route_patterns(self, mini=True):
        """
        Get route patterns
        :param mini: return a list of tuples of route pattern details
        :return: A list of dictionary's
        """
        resp = self.client.service.listRoutePattern(
                {'pattern': '%'}, returnedTags={
                    'pattern': '', 'description': '', '_uuid': ''})[1]['return']['routePattern']
        if mini:
            return [(i['pattern'], i['description'], i['_uuid'][1:-1]) for i in resp]
        else:
            return resp

    def get_route_pattern(self, pattern):
        """
        Get route pattern
        :param pattern: route pattern
        :return: result dictionary
        """
        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        # Cant get pattern directly so get UUID first
        uuid = self.client.service.listRoutePattern({'pattern': pattern}, returnedTags={'_uuid': ''})

        if uuid[0] == 200 and uuid[1]['return'] == '':
            result['response'] = 'Route pattern: {0} not found'.format(pattern)
            result['error'] = 'Route pattern: {0} not found'.format(pattern)
            return result

        else:
            resp = self.client.service.getRoutePattern(uuid=uuid[1]['return']['routePattern'][0]['_uuid'][1:-1])

            if resp[0] == 200:
                result['success'] = True
                result['response'] = resp[1]['return']['routePattern']
                return result
            elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
                result['response'] = 'Route pattern: {0} not found'.format(pattern)
                result['error'] = resp[1].faultstring
                return result
            else:
                result['response'] = 'Unknown error'
                result['error'] = resp[1].faultstring
                return result

    def add_route_pattern(self,
                          pattern,
                          gateway='',
                          route_list='',
                          description='',
                          partition=''):
        """
        Add a route pattern
        :param pattern: Route pattern
        :param gateway: Destination gateway
        :param route_list: Destination route list
               Either a gateway or route list can be used at the same time
        :param description: Route pattern description
        :param partition: Route pattern partition
        :return: result dictionary
        """
        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        req = {
            'pattern': pattern,
            'description': description,
            'destination': {},
            'routePartitionName': partition,
        }

        if gateway == '' and route_list == '':
            result['response'] = 'Either a gateway OR route list, is a required parameter'
            result['error'] = 'Enter either a gateway OR route list, not both'
            return result
        elif gateway != '' and route_list != '':
            result['response'] = 'Enter a gateway OR route list, not both'
            result['error'] = 'Destination can be a gateway OR route list, not both'
            return result
        elif gateway != '':
            req['destination'].update({'gatewayName': gateway})
            destination = gateway
        elif route_list != '':
            req['destination'].update({'routeListName': route_list})
            destination = route_list

        resp = self.client.service.addRoutePattern(req)

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Pattern successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Pattern already exists'.format(pattern)
            result['error'] = resp[1].faultstring
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Gateway or route list: {0} not found'.format(destination)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Pattern could not be added'
            result['error'] = resp[1].faultstring
            return result

    def get_media_resource_groups(self, mini=True):
        """
        Get media resource groups
        :param mini: return a list of tuples of route pattern details
        :return: A list of dictionary's
        """
        resp = self.client.service.listMediaResourceGroup(
                {'name': '%'}, returnedTags={
                    'name': '', 'description': ''})[1]['return']['mediaResourceGroup']
        if mini:
            return [(i['name'], i['description']) for i in resp]
        else:
            return resp

    def get_media_resource_group(self, media_resource_group):
        """
        Get a media resource group details
        :param media_resource_group: Media resource group name
        :return: result dictionary
        """
        resp = self.client.service.getMediaResourceGroup(name=media_resource_group)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['mediaResourceGroup']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Media resouce group: {0} not found'.format(media_resource_group)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_media_resource_group(self,
                                 media_resource_group,
                                 description='',
                                 multicast='false',
                                 members=[]):
        """
        Add a media resource group
        :param media_resource_group: Media resource group name
        :param description: Media resource description
        :param multicast: Mulicast enabled
        :param members: Media resource group members
        :return: result dictionary
        """
        resp = self.client.service.addMediaResourceGroup({
            'name': media_resource_group,
            'description': description,
            'multicast': multicast,
            'members': {'member': []}
        })

        if members:
            [resp['members']['member'].append({'deviceName': i}) for i in members]

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Media resource group successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Media resource group already exists'.format(media_resource_group)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Media resource group could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_media_resource_group(self, media_resource_group):
        """
        Delete a Media resource group
        :param media_resource_group: The name of the media resource group to delete
        :return: result dictionary
        """
        resp = self.client.service.removeMediaResourceGroup(name=media_resource_group)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Media resource group successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Media resource group: {0} not found'.format(media_resource_group)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Media resource group could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_media_resource_group_list(self, media_resource_group_list):
        return self.client.service.getMediaResourceList(name=media_resource_group_list)

    def add_media_resource_group_list(self, media_resource_group_list, members=[]):
        """
        Add a media resource group list
        :param media_resource_group_list: Media resource group list name
        :param members: A list of members
        :return:
        """
        resp = self.client.service.addMediaResourceList({
            'name': media_resource_group_list,
            'members': {'member': []}
        })

        if members:
            [resp['members']['member'].append({'order': members.index(i),
                                               'mediaResourceGroupName': i}) for i in members]

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Media resource group list successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Media resource group list already exists'.format(media_resource_group_list)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Media resource group list could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_media_resource_group_list(self, media_resource_group_list):
        """
        Delete a Media resource group list
        :param media_resource_group_list: The name of the media resource group list to delete
        :return: result dictionary
        """
        resp = self.client.service.removeMediaResourceList(name=media_resource_group_list)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Media resource group list successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Media resource group list: {0} not found'.format(media_resource_group_list)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Media resource group list could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def add_directory_number(self,
                             pattern,
                             route_partition_name='',
                             description='',
                             alerting_name='',
                             ascii_alerting_name='',
                             shared_line_css='',
                             aar_neighbourhood='',
                             call_forward_css='',
                             vm_profile_name='NoVoiceMail',
                             aar_destination_mask='',
                             call_forward_destination='',
                             forward_all_to_vm='false',
                             forward_all_destination='',
                             forward_to_vm='false'):
        """
        Add a directory number
        :param pattern: Directory number
        :param route_partition_name: Route partition name
        :param description: Directory number description
        :param alerting_name: Alerting name
        :param ascii_alerting_name: ASCII alerting name
        :param shared_line_css: Calling search space
        :param aar_neighbourhood: AAR group
        :param call_forward_css: Call forward calling search space
        :param vm_profile_name: Voice mail profile
        :param aar_destination_mask: AAR destination mask
        :param call_forward_destination: Call forward destination
        :param forward_all_to_vm: Forward all to voice mail checkbox
        :param forward_all_destination: Forward all destination
        :param forward_to_vm: Forward to voice mail checkbox
        :return: result dictionary
        """

        resp = self.client.service.addLine({
            'pattern': pattern,
            'routePartitionName': route_partition_name,
            'description': description,
            'alertingName': alerting_name,
            'asciiAlertingName': ascii_alerting_name,
            'voiceMailProfileName': vm_profile_name,
            'shareLineAppearanceCssName': shared_line_css,
            'aarNeighborhoodName': aar_neighbourhood,
            'aarDestinationMask': aar_destination_mask,
            'callForwardAll': {
                'forwardToVoiceMail': forward_all_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': forward_all_destination,
            },
            'callForwardBusy': {
                'forwardToVoiceMail': forward_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': call_forward_destination,
            },
            'callForwardBusyInt': {
                'forwardToVoiceMail': forward_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': call_forward_destination,
            },
            'callForwardNoAnswer': {
                'forwardToVoiceMail': forward_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': call_forward_destination,
            },
            'callForwardNoAnswerInt': {
                'forwardToVoiceMail': forward_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': call_forward_destination,
            },
            'callForwardNoCoverage': {
                'forwardToVoiceMail': forward_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': call_forward_destination,
            },
            'callForwardNoCoverageInt': {
                'forwardToVoiceMail': forward_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': call_forward_destination,
            },
            'callForwardOnFailure': {
                'forwardToVoiceMail': forward_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': call_forward_destination,
            },
            'callForwardNotRegistered': {
                'forwardToVoiceMail': forward_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': call_forward_destination,
            },
            'callForwardNotRegisteredInt': {
                'forwardToVoiceMail': forward_to_vm,
                'callingSearchSpaceName': call_forward_css,
                'destination': call_forward_destination,
            },
        })

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Directory number successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Directory number already exists'.format(pattern)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Directory number could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_directory_number(self, directory_number):
        """
        Delete a directory number
        :param directory_number: The name of the directory number to delete
        :return: result dictionary
        """
        resp = self.client.service.removeLine(pattern=directory_number)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Directory number successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Directory number: {0} not found'.format(directory_number)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Directory number could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def add_cti_route_point(self,
                            cti_route_point,
                            description='',
                            device_pool='Default',
                            location='Hub_None',
                            common_device_config='',
                            css='',
                            product='CTI Route Point',
                            dev_class='CTI Route Point',
                            protocol='SCCP',
                            protocol_slide='User',
                            use_trusted_relay_point='Default',
                            lines=[]):
        """
        Add CTI route point
        lines should be a list of tuples containing the pattern and partition
        EG: [('77777', 'AU_PHONE_PT')]
        :param cti_route_point: CTI route point name
        :param description: CTI route point description
        :param device_pool: Device pool name
        :param location: Location name
        :param common_device_config: Common device config name
        :param css: Calling search space name
        :param product: CTI device type
        :param dev_class: CTI device type
        :param protocol: CTI protocol
        :param protocol_slide: CTI protocol slide
        :param use_trusted_relay_point: Use trusted relay point: (Default, On, Off)
        :param lines: A list of tuples of [(directory_number, partition)]
        :return:
        """

        resp = self.client.service.addCtiRoutePoint({
            'name': cti_route_point,
            'description': description,
            'product': product,
            'class': dev_class,
            'protocol': protocol,
            'protocolSide': protocol_slide,
            'commonDeviceConfigName': common_device_config,
            'callingSearchSpaceName': css,
            'devicePoolName': device_pool,
            'locationName': location,
            'useTrustedRelayPoint': use_trusted_relay_point,
            'lines': {'line': []}
        })

        if lines:
            [resp['lines']['line'].append({'index': lines.index(i) + 1,
                                           'dirn': {'pattern': i[0], 'routePartitionName': i[1]}
                                           }) for i in lines]

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'CTI route point successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'CTI route point already exists'.format(cti_route_point)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'CTI route point could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_cti_route_point(self, cti_route_point):
        """
        Delete a CTI route point
        :param cti_route_point: The name of the CTI route point to delete
        :return: result dictionary
        """
        resp = self.client.service.removeCtiRoutePoint(name=cti_route_point)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'CTI route point successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'CTI route point: {0} not found'.format(cti_route_point)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'CTI route point could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def add_phone(self,
                  phone,
                  description='',
                  product='Cisco 7941',
                  device_pool='Default',
                  location='Hub_None',
                  phone_template='Standard 7941 SCCP',
                  common_device_config='',
                  css='',
                  aar_css='',
                  subscribe_css='',
                  lines=[],
                  dev_class='Phone',
                  protocol='SCCP',
                  softkey_template='Standard User',
                  enable_em='true',
                  em_service_name='Extension Mobility',
                  em_service_url=False,
                  em_url_button_enable=False,
                  em_url_button_index='1',
                  em_url_label='Press here to logon',
                  ehook_enable=1):
        """
        lines takes a list of Tuples with properties for each line EG:

                                               display                           external
            DN     partition    display        ascii          label               mask
        [('77777', 'LINE_PT', 'Jim Smith', 'Jim Smith', 'Jim Smith - 77777', '0294127777')]
        Add A phone
        :param phone:
        :param description:
        :param product:
        :param device_pool:
        :param location:
        :param phone_template:
        :param common_device_config:
        :param css:
        :param aar_css:
        :param subscribe_css:
        :param lines:
        :param dev_class:
        :param protocol:
        :param softkey_template:
        :param enable_em:
        :param em_service_name:
        :param em_service_url:
        :param em_url_button_enable:
        :param em_url_button_index:
        :param em_url_label:
        :param ehook_enable:
        :return:
        """

        req = {
            'name': phone,
            'description': description,
            'product': product,
            'class': dev_class,
            'protocol': protocol,
            'commonDeviceConfigName': common_device_config,
            'softkeyTemplateName': softkey_template,
            'phoneTemplateName': phone_template,
            'devicePoolName': device_pool,
            'locationName': location,
            'enableExtensionMobility': enable_em,
            'callingSearchSpaceName': css,
            'automatedAlternateRoutingCssName': aar_css,
            'subscribeCallingSearchSpaceName': subscribe_css,
            'lines': {'line': []},
            'services': {'service': []},
            'vendorConfig': [{
                'ehookEnable': ehook_enable
            }]
        }

        if lines:
            [req['lines']['line'].append({
                'index': lines.index(i) + 1,
                'dirn': {
                    'pattern': i[0],
                    'routePartitionName': i[1]
                },
                'display': i[2],
                'displayAscii': i[3],
                'label': i[4],
                'e164Mask': i[5]
            }) for i in lines]

        if em_service_url:
            req['services']['service'].append([{
                'telecasterServiceName': em_service_name,
                'name': em_service_name,
                'url': 'http://{0}:8080/emapp/EMAppServlet?device=#DEVICENAME#&EMCC=#EMCC#'.format(self.cucm),
            }])

        if em_url_button_enable:
            req['services']['service'][0].update({'urlButtonIndex': em_url_button_index, 'urlLabel': em_url_label})

        resp = self.client.service.addPhone(req)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Phone successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Phone already exists'.format(phone)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Phone could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_phone(self, phone):
        """
        Delete a phone
        :param phone: The name of the phone to delete
        :return: result dictionary
        """
        resp = self.client.service.removePhone(name=phone)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Phone successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Phone: {0} not found'.format(phone)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Phone could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_device_profiles(self, mini=True):
        """
        Get device profile details
        :param mini: return a list of tuples of device profile details
        :return: A list of dictionary's
        """
        resp = self.client.service.listDeviceProfile(
                {'name': '%'}, returnedTags={
                    'name': '',
                    'product': '',
                    'protocol': '',
                    'phoneTemplateName': '',
                })[1]['return']['deviceProfile']
        if mini:
            return [(i['name'],
                     i['product'],
                     i['protocol'],
                     i['phoneTemplateName']['value'],
                     ) for i in resp]
        else:
            return resp

    def get_device_profile(self, profile):
        """
        Get device profile parameters
        :param profile: profile name
        :return: result dictionary
        """
        resp = self.client.service.getDeviceProfile(name=profile)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['deviceProfile']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Profile: {0} not found'.format(profile)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_device_profile(self,
                           profile,
                           description='',
                           product='Cisco 7962',
                           phone_template='Standard 7962G SCCP',
                           dev_class='Device Profile',
                           protocol='SCCP',
                           softkey_template='Standard User',
                           em_service_name='Extension Mobility',
                           lines=[]):
        """
        Add A Device profile for use with extension mobility
        lines takes a list of Tuples with properties for each line EG:

                                               display                           external
            DN     partition    display        ascii          label               mask
        [('77777', 'LINE_PT', 'Jim Smith', 'Jim Smith', 'Jim Smith - 77777', '0294127777')]
        :param profile:
        :param description:
        :param product:
        :param phone_template:
        :param lines:
        :param dev_class:
        :param protocol:
        :param softkey_template:
        :param em_service_name:
        :return:
        """

        req = {
            'name': profile,
            'description': description,
            'product': product,
            'class': dev_class,
            'protocol': protocol,
            'softkeyTemplateName': softkey_template,
            'phoneTemplateName': phone_template,
            'lines': {'line': []},
            'services': {'service': [{
                'telecasterServiceName': em_service_name,
                'name': em_service_name,
                'url': 'http://{0}:8080/emapp/EMAppServlet?device=#DEVICENAME#&EMCC=#EMCC#'.format(self.cucm),
            }]},
        }

        if lines:
            [req['lines']['line'].append({
                'index': lines.index(i) + 1,
                'dirn': {
                    'pattern': i[0],
                    'routePartitionName': i[1]
                },
                'display': i[2],
                'displayAscii': i[3],
                'label': i[4],
                'e164Mask': i[5]
            }) for i in lines]

        resp = self.client.service.addDeviceProfile(req)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Device profile successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'Device profile already exists'.format(profile)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Device profile could not be added'
            result['error'] = resp[1].faultstring
            return result

    def delete_device_profile(self, profile):
        """
        Delete a device profile
        :param profile: The name of the device profile to delete
        :return: result dictionary
        """
        resp = self.client.service.removeDeviceProfile(name=profile)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'Device profile successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'Device profile: {0} not found'.format(profile)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Device profile could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def get_users(self, mini=True):
        """
        Get users details
        :param mini: return a list of tuples of user details
        :return: A list of dictionary's
        """
        resp = self.client.service.listUser(
                {'userid': '%'}, returnedTags={
                    'userid': '',
                    'firstName': '',
                    'lastName': '',
                })[1]['return']['user']
        if mini:
            return [(i['userid'],
                     i['firstName'],
                     i['lastName'],
                     ) for i in resp]
        else:
            return resp

    def get_user(self, user_id):
        """
        Get user parameters
        :param user_id: profile name
        :return: result dictionary
        """
        resp = self.client.service.getUser(userid=user_id)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = resp[1]['return']['user']
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'User: {0} not found'.format(user_id)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'Unknown error'
            result['error'] = resp[1].faultstring
            return result

    def add_user(self,
                 user_id,
                 last_name,
                 first_name='',
                 user_profile='Standard (Factory Default) User Profile'):
        """
        Add a user
        :param user_id: User ID of the user to add
        :param first_name: First name of the user to add
        :param last_name: Last name of the user to add
        :param user_profile: User profile template
        :return: result dictionary
        """
        resp = self.client.service.addUser({
            'userid': user_id,
            'firstName': first_name,
            'lastName': last_name,
            'userProfile': user_profile,
        })

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'User successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['response'] = 'User already exists'.format(user_id)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'User could not be added'
            result['error'] = resp[1].faultstring
            return result

    def update_user_em(self,
                       user_id,
                       device_profile,
                       default_profile,
                       subscribe_css,
                       primary_extension):
        """
        Update end user for extension mobility
        :param user_id: User ID
        :param device_profile: Device profile name
        :param default_profile: Default profile name
        :param subscribe_css: Subscribe CSS
        :param primary_extension: Primary extension, must be a number from the device profile
        :return: result dictionary
        """
        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        resp = self.client.service.getDeviceProfile(name=device_profile)

        if resp[0] == 500 and '{0} was not found'.format(device_profile) in resp[1].faultstring:
            result['response'] = 'Device profile: {0} not found'.format(device_profile)
            result['error'] = resp[1].faultstring
            return result

        else:
            uuid = resp[1]['return']['deviceProfile']['_uuid'][1:-1]

        resp = self.client.service.updateUser(
                userid=user_id,
                phoneProfiles={'profileName': {'_uuid': uuid}},
                defaultProfile=default_profile,
                subscribeCallingSearchSpaceName=subscribe_css,
                primaryExtension={'pattern': primary_extension},
                associatedGroups={'userGroup': {'name': 'Standard CCM End Users'}}
        )

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'User successfully updated'
            return result
        elif resp[0] == 500 and '{0} was not found'.format(user_id) in resp[1].faultstring:
            result['response'] = 'User ID: {0} not found'.format(user_id)
            result['error'] = resp[1].faultstring
            return result
        elif resp[0] == 500 and '{0} was not found'.format(default_profile) in resp[1].faultstring:
            result['response'] = 'Default profile: {0} not found'.format(default_profile)
            result['error'] = resp[1].faultstring
            return result
        elif resp[0] == 500 and '{0} was not found'.format(subscribe_css) in resp[1].faultstring:
            result['response'] = 'Subscribe CSS: {0} not found'.format(subscribe_css)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'User could not be updated'
            result['error'] = resp[1].faultstring
            return result

    def update_user_credentials(self,
                                user_id,
                                password='',
                                pin=''):
        """
        Update end user for credentials
        :param user_id: User ID
        :param password: Web interface password
        :param pin: Extension mobility PIN
        :return: result dictionary
        """
        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if password == '' and pin == '':
            result['response'] = 'User could not be updated'
            result['error'] = 'Password and/or Pin are required'
            return result

        elif password != '' and pin != '':
            resp = self.client.service.updateUser(
                    userid=user_id,
                    password=password,
                    pin=pin,
            )

        elif password != '':
            resp = self.client.service.updateUser(
                    userid=user_id,
                    password=password,
            )

        elif pin != '':
            resp = self.client.service.updateUser(
                    userid=user_id,
                    pin=pin,
            )

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'User successfully updated'
            return result
        elif resp[0] == 500 and '{0} was not found'.format(user_id) in resp[1].faultstring:
            result['response'] = 'User ID: {0} not found'.format(user_id)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'User could not be updated'
            result['error'] = resp[1].faultstring
            return result

    def delete_user(self, user_id):
        """
        Delete a user
        :param user_id: The name of the user to delete
        :return: result dictionary
        """
        resp = self.client.service.removeUser(userid=user_id)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['response'] = 'User successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['response'] = 'User: {0} not found'.format(user_id)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['response'] = 'User could not be deleted'
            result['error'] = resp[1].faultstring
            return result
