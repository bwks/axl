"""
Class to interface with cisco ucm axl api.
Author: Brad Searle
Version: 0.2
Dependencies:
 - suds-jurko: https://bitbucket.org/jurko/suds
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
    This works for me with my environment of;
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Location successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['msg'] = 'Location already exists'.format(location)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Location could not be added'
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Location successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['msg'] = 'Location: {0} not found'.format(location)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Location could not be deleted'
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Region successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['msg'] = 'Region already exists'.format(region)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Region could not be added'
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Region successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['msg'] = 'Region: {0} not found'.format(region)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Region could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def update_region(self, region):
        """
        Update region and assign region to all other regions
        :param region:
        :return:
        """
        # Get all Regions
        _all_regions = self.client.service.listRegion({'name': '%'}, returnedTags={'name': ''})

        # Make list of region names
        _region_names = [str(i['name']) for i in _all_regions[1]['return']['region']]

        # Build list of dictionaries to add to region api call
        _region_list = []

        for i in _region_names:
            if i == region:
                _region_list.append({
                    'regionName': i,
                    'bandwidth': '256 kbps (L16, AAC-LD)',
                    'videoBandwidth': '-1',
                    'lossyNetwork': 'Use System Default',
                })

            # Music on hold region name
            elif i == 'MOH_R':
                _region_list.append({
                    'regionName': i,
                    'bandwidth': '64 kbps (G.722, G.711)',
                    'videoBandwidth': '-1',
                    'lossyNetwork': 'Use System Default',
                })

            else:
                _region_list.append({
                    'regionName': i,
                    'bandwidth': '8 kbps (G.729)',
                    'videoBandwidth': '-1',
                    'lossyNetwork': 'Use System Default',
                })

        ur = self.client.service.updateRegion(name=region,
                                              relatedRegions={'relatedRegion': _region_list})

        return ur

    def add_srst(self, srst, ip_address, port=2000, sip_port=5060):
        """

        :param srst:
        :param ip_address:
        :param port:
        :param sip_port:
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'SRST successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['msg'] = 'SRST already exists'.format(srst)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'SRST could not be added'
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'SRST successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['msg'] = 'SRST: {0} not found'.format(srst)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'SRST could not be deleted'
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Device pool successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['msg'] = 'Device pool already exists'.format(srst)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Device pool could not be added'
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Device pool successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['msg'] = 'Device pool: {0} not found'.format(device_pool)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Device pool could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def update_device_pool(self, device_pool, route_group, media_resource_group_list):
        """

        :param device_pool:
        :param route_group:
        :param media_resource_group_list:
        :return:
        """
        udp = self.client.service.updateDevicePool(
                name=device_pool,
                localRouteGroupName=route_group,
                mediaResourceListName=media_resource_group_list
        )

        return udp

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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Conference bridge successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['msg'] = 'Conference bridge already exists'.format(conference_bridge)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Conference bridge could not be added'
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Conference bridge successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['msg'] = 'Conference bridge: {0} not found'.format(conference_bridge)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Conference bridge could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def add_transcoder(self,
                       transcoder,
                       description='',
                       device_pool='Default',
                       product='Cisco IOS Enhanced Media Termination Point'):
        """

        :param transcoder:
        :param description:
        :param device_pool:
        :param product:
        :return:
        """
        resp = self.client.service.addTranscoder({
            'name': transcoder,
            'description': description,
            'devicePoolName': device_pool,
            'product': product,
        })

        result = {
            'success': False,
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Conference bridge successfully added'
            return result
        elif resp[0] == 500 and 'duplicate value' in resp[1].faultstring:
            result['msg'] = 'Conference bridge already exists'.format(transcoder)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Conference bridge could not be added'
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
            'msg': '',
            'error': '',
        }

        if resp[0] == 200:
            result['success'] = True
            result['msg'] = 'Transcoder successfully deleted'
            return result
        elif resp[0] == 500 and 'was not found' in resp[1].faultstring:
            result['msg'] = 'Transcoder: {0} not found'.format(transcoder)
            result['error'] = resp[1].faultstring
            return result
        else:
            result['msg'] = 'Transcoder could not be deleted'
            result['error'] = resp[1].faultstring
            return result

    def add_h323_gateway(self,
                         gateway_loopback,
                         description,
                         device_pool,
                         location,
                         prefix_dn,
                         sig_digits,
                         css,
                         aar_css,
                         aar_neighborhood,
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

        :param gateway_loopback:
        :param description:
        :param device_pool:
        :param location:
        :param prefix_dn:
        :param sig_digits:
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
        ahg = self.client.service.addH323Gateway({
            'name': gateway_loopback,
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

        return ahg

    def update_h323_gateway(self, gateway_loopback, media_resource_group_list):
        """

        :param gateway_loopback:
        :param media_resource_group_list:
        :return:
        """
        ug = self.client.service.updateH323Gateway(
                name=gateway_loopback,
                mediaResourceListName=media_resource_group_list,
        )

        return ug

    def add_media_resource_group(self,
                                 media_resource_group,
                                 description,
                                 conference_bridge,
                                 transcoder,
                                 multicast='false'):
        """

        :param media_resource_group:
        :param description:
        :param conference_bridge:
        :param transcoder:
        :param multicast:
        :return:
        """
        amrg = self.client.service.addMediaResourceGroup({
            'name': media_resource_group,
            'description': description,
            'multicast': multicast,
            'members': {
                'member': [{
                    'deviceName': conference_bridge
                }, {
                    'deviceName': transcoder
                }]
            }
        })

        return amrg

    def add_media_resource_group_list(self, media_resource_group_list, mrgl_members=[]):
        """

        :param media_resource_group_list:
        :param mrgl_members: A list of mrgl member names
        :return:
        """
        _member_list = [{'order': mrgl_members.index(i), 'mediaResourceGroupName': i} for i in mrgl_members]

        amrgl = self.client.service.addMediaResourceList({
            'name': media_resource_group_list,
            'members': {
                'member': _member_list,
            }
        })

        return amrgl

    def add_route_group(self, route_group, gateway_loopback, distribution_algorithm='Top Down'):
        """

        :param route_group:
        :param gateway_loopback:
        :param distribution_algorithm:
        :return:
        """

        arg = self.client.service.addRouteGroup({
            'name': route_group,
            'distributionAlgorithm': distribution_algorithm,
            'members': {
                'member': {
                    'deviceName': gateway_loopback,
                    'deviceSelectionOrder': 1,
                    'port': 0,
                }
            }
        })

        return arg

    def add_line(self,
                 pattern,
                 route_partition_name,
                 description,
                 alerting_name,
                 ascii_alerting_name,
                 shared_line_css,
                 aar_neighbourhood,
                 call_forward_css,
                 vm_profile_name='NoVoiceMail',
                 aar_destination_mask='',
                 call_forward_destination='',
                 forward_all_to_vm='false',
                 forward_to_vm='false'):
        """

        :param pattern:
        :param route_partition_name:
        :param description:
        :param alerting_name:
        :param ascii_alerting_name:
        :param shared_line_css:
        :param aar_neighbourhood:
        :param call_forward_css:
        :param vm_profile_name:
        :param aar_destination_mask:
        :param call_forward_destination:
        :param forward_all_to_vm:
        :param forward_to_vm:
        :return:
        """

        al = self.client.service.addLine({
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
                'destination': '',
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

        return al

    def add_cti_route_point(self,
                            cti_route_point,
                            description,
                            device_pool,
                            location,
                            common_device_config,
                            css,
                            lines=[],
                            product='CTI Route Point',
                            dev_class='CTI Route Point',
                            protocol='SCCP',
                            protocol_slide='User',
                            use_trusted_relay_point='Default'):
        """
        Add CTI route point
        lines should be a list of tuples containing the pattern and partition
        EG: [('77777', 'AU_PHONE_PT')]
        :param cti_route_point:
        :param description:
        :param device_pool:
        :param location:
        :param common_device_config:
        :param css:
        :param lines:
        :param product:
        :param dev_class:
        :param protocol:
        :param protocol_slide:
        :param use_trusted_relay_point:
        :return:
        """

        def _add_lines(lines):
            # adds a dict of lines to the line list
            _line_list = {'line': []}
            for i in lines:
                _line_list['line'].append({
                    'index': lines.index(i) + 1,
                    'dirn': {
                        'pattern': i[0],
                        'routePartitionName': i[1],
                    }
                })
            return _line_list

        if lines:
            line_dict = _add_lines(lines)
        else:
            line_dict = {'line': []}

        acrp = self.client.service.addCtiRoutePoint({
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
            'lines': line_dict
        })

        return acrp

    def add_phone(self,
                  name,
                  description,
                  product,
                  device_pool,
                  location,
                  phone_template,
                  common_device_config,
                  css,
                  aar_css,
                  subscribe_css,
                  lines=[],
                  em_service_url=True,
                  dev_class='Phone',
                  protocol='SCCP',
                  softkey_template='Standard User',
                  enable_em='true',
                  ehook_enable=1):

        """
        lines takes a list of Tuples with properties for each line EG:

                                               display                           external
            DN     partition    display        ascii          label               mask
        [('77777', 'LINE_PT', 'Jim Smith', 'Jim Smith', 'Jim Smith - 77777', '0294127777')]

        :param name:
        :param description:
        :param product:
        :param device_pool:
        :param location:
        :param phone_template:
        :param lines:
        :param em_service_url:
        :param dev_class:
        :param protocol:
        :param common_device_config:
        :param softkey_template:
        :param enable_em:
        :param css:
        :param aar_css:
        :param subscribe_css:
        :param ehook_enable:
        :return:
        """

        def _add_lines(lines):
            _line_list = {'line': []}
            for i in lines:
                _line_list['line'].append({
                    'index': lines.index(i) + 1,
                    'dirn': {
                        'pattern': i[0],
                        'routePartitionName': i[1]
                    },
                    'display': i[2],
                    'displayAscii': i[3],
                    'label': i[4],
                    'e164Mask': i[5]
                })
            return _line_list

        if em_service_url:
            services = {
                'service': [{
                    'telecasterServiceName': 'Extension Mobility',
                    'name': 'Extension Mobility',
                    'url': 'http://{0}:8080/emapp/EMAppServlet?device=#DEVICENAME#&EMCC=#EMCC#'.format(self.cucm),
                    'urlButtonIndex': '1',
                    'urlLabel': 'Press here to log in',
                }]
            }
        else:
            services = {'service': []}

        if lines:
            line_dict = _add_lines(lines)
        else:
            line_dict = {'line': []}

        ap = self.client.service.addPhone({
            'name': name,
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
            'lines': line_dict,
            'services': services,
            'vendorConfig': [{
                'ehookEnable': ehook_enable
            }]
        })

        return ap
