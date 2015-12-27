"""
Class to interface with cisco ucm axl api.
Author: Brad Searle
Version: 0.1
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
    Centos 7
    Python 3
    suds-jurko
    Your mileage may vary
    """

    def __init__(self, username, password, cucm):
        self.username = username
        self.password = password
        self.cucm = cucm

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

        # CUCM 10.5
        wsdl = 'file:///tools/envs/networktools/nettools/scripts/axlsqltoolkit/schema/10.5/AXLAPI.wsdl'
        self.client = Client(wsdl, location='https://{0}:8443/axl/'.format(cucm), faults=False,
                             plugins=[ImportDoctor(imp)],
                             transport=t)

    def add_location(self, location,
                     cucm_version=10,
                     kbits=512,
                     video_kbits=-1,
                     within_audio_bw=512,
                     within_video_bw=-1,
                     within_immersive_kbits=-1):

        """
        Add a location to cucm
        :param location:
        :param cucm_version:
        :param kbits:
        :param video_kbits:
        :param within_audio_bw:
        :param within_video_bw:
        :param within_immersive_kbits:
        :return:
        """
        if cucm_version == 10:

            al = self.client.service.addLocation({
                'name': location,
                # CUCM 10.6
                'withinAudioBandwidth': within_audio_bw,
                'withinVideoBandwidth': within_video_bw,
                'withinImmersiveKbits': within_immersive_kbits,
            })

        else:

            al = self.client.service.addLocation({
                'name': location,
                # CUCM 8.6
                'kbits': kbits,
                'videoKbits': video_kbits,
            })

        return al

    def add_region(self, region):

        ar = self.client.service.addRegion({
            'name': region
        })

        return ar

    def update_region(self, region):
        """
        Update region and assign region to all other regions
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

    def add_srst(self, srst, ip_address, port=2000, sip_port=''):

        asrst = self.client.service.addSrst({
            'name': srst,
            'port': port,
            'ipAddress': ip_address,
            'SipPort': sip_port,
        })

        return asrst

    def add_device_pool(self, device_pool,
                        date_time_group,
                        region,
                        location,
                        srst,
                        cm_group, network_locale='Australia'):

        adp = self.client.service.addDevicePool({
            'name': device_pool,
            'dateTimeSettingName': date_time_group,  # update to state timezone
            'regionName': region,
            'locationName': location,
            'srstName': srst,
            'callManagerGroupName': cm_group,
            'networkLocale': network_locale,
        })

        return adp

    def update_device_pool(self, device_pool, route_group, media_resource_group_list):

        udp = self.client.service.updateDevicePool(
                name=device_pool,
                localRouteGroupName=route_group,
                mediaResourceListName=media_resource_group_list
        )

        return udp

    def add_conference_bridge(self, conference_bridge,
                              gateway_name,
                              device_pool,
                              location,
                              product='Cisco IOS Enhanced Conference Bridge',
                              security_profile='Non Secure Conference Bridge'):

        acb = self.client.service.addConferenceBridge({
            'name': conference_bridge,
            'description': '{0} on {1}'.format(conference_bridge, gateway_name),
            'devicePoolName': device_pool,
            'locationName': location,
            'product': product,
            'securityProfileName': security_profile
        })

        return acb

    def add_transcoder(self, transcoder,
                       gateway_name,
                       device_pool,
                       product='Cisco IOS Enhanced Media Termination Point'):

        at = self.client.service.addTranscoder({
            'name': transcoder,
            'description': '{0} on {1}'.format(transcoder, gateway_name),
            'devicePoolName': device_pool,
            'product': product,
        })

        return at

    def add_h323_gateway(self, gateway_loopback,
                         gateway_name,
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

        ahg = self.client.service.addH323Gateway({
            'name': gateway_loopback,
            'description': '{0} H323 Voice Gateway CLI FIXED'.format(gateway_name),
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

        ug = self.client.service.updateH323Gateway(
                name=gateway_loopback,
                mediaResourceListName=media_resource_group_list,
        )

        return ug

    def add_media_resource_group(self, media_resource_group,
                                 mrg_description,
                                 conference_bridge,
                                 transcoder,
                                 multicast='false'):

        amrg = self.client.service.addMediaResourceGroup({
            'name': media_resource_group,
            'description': mrg_description,
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

    def add_media_resource_group_list(self, media_resource_group_list, mrgl_members):

        _member_list = [{'order': mrgl_members.index(i), 'mediaResourceGroupName': i} for i in mrgl_members]

        amrgl = self.client.service.addMediaResourceList({
            'name': media_resource_group_list,
            'members': {
                'member': _member_list,
            }
        })

        return amrgl

    def add_route_group(self, route_group, gateway_loopback, distribution_algorithm='Top Down'):
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

    def add_line(self, pattern,
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


class AddCTIRoutePoint(object):
    """
    Add CTI route point
    lines should be a list of tuples containing the pattern and partition
    EG: [('77777', 'AU_PHONE_PT')]
    """

    def __init__(self,
                 ctiRoutePoint,
                 description,
                 devicePool,
                 location,
                 lines=[],
                 product='CTI Route Point',
                 devClass='CTI Route Point',
                 protocol='SCCP',
                 protocolSide='User',
                 commonDeviceConfigName='AH_Standard_Phone_CDC',
                 callingSearchSpaceName='AU_DEVICE_CSS',
                 useTrustedRelayPoint='Default'):

        def _add_lines(lines):

            _line_list = {'line': []}
            _sentinel = 0
            for i in lines:
                _sentinel += 1
                _line_list['line'].append({'index': _sentinel,
                                           'dirn': {
                                               'pattern': i[0],
                                               'routePartitionName': i[1],
                                           }
                                           })

            return _line_list

        self.cti_route_point = ctiRoutePoint
        self.description = description
        self.device_pool = devicePool
        self.location = location
        self.product = product
        self.dev_class = devClass
        self.protocol = protocol
        self.protocol_slide = protocolSide
        self.common_device_config = commonDeviceConfigName
        self.css = callingSearchSpaceName
        self.use_trusted_relay_point = useTrustedRelayPoint

        if lines:
            self.lines = _add_lines(lines)
        else:
            self.lines = {'line': []}

    def add_cti_route_point(self):

        acrp = axl.client.service.addCtiRoutePoint({
            'name': self.cti_route_point,
            'description': self.description,
            'product': self.product,
            'class': self.dev_class,
            'protocol': self.protocol,
            'protocolSide': self.protocol_slide,
            'commonDeviceConfigName': self.common_device_config,
            'callingSearchSpaceName': self.css,
            'devicePoolName': self.device_pool,
            'locationName': self.location,
            'useTrustedRelayPoint': self.use_trusted_relay_point,
            'lines': self.lines
        })

        return acrp


class AddPhone(object):
    """
    Add phone
    lines takes a list of Tuples EG:
    [('77777', 'Jim Smith', 'Jim Smith', 'Jim Smith - 77777', 'Jim Smith - 77777', '0294123456')]
    """

    def __init__(self,
                 name,
                 description,
                 product,
                 devicePoolName,
                 locationName,
                 phoneTemplateName,
                 lines=[],
                 emServiceURL=True,
                 devClass='Phone',
                 protocol='SCCP',
                 commonDeviceConfigName='AH_Standard_Phone_CDC',
                 softkeyTemplateName='Standard User',
                 enableExtensionMobility='true',
                 callingSearchSpaceName='AU_DEVICE_CSS',
                 automatedAlternateRoutingCssName='AU_DEVICE_CSS',
                 subscribeCallingSearchSpaceName='AU_SUBSCRIBE_CSS',
                 ehookEnable=1):

        def _add_lines(lines):
            _line_list = {'line': []}
            _sentinel = 0
            for i in lines:
                _sentinel += 1

                _line_list['line'].append({
                    'index': _sentinel,
                    'dirn': {
                        'pattern': i[0],
                        'routePartitionName': 'AU_PHONE_PT'
                    },
                    'display': i[1],
                    'displayAscii': i[2],
                    'label': i[3],
                    'e164Mask': i[5]
                })
            return _line_list

        self.name = name
        self.description = description
        self.product = product
        self.device_pool = devicePoolName
        self.location = locationName
        self.phone_template = phoneTemplateName
        self.lines = lines
        self.em_service_url = emServiceURL
        self.dev_class = devClass
        self.protocol = protocol
        self.common_device_config = commonDeviceConfigName
        self.softkey_template = softkeyTemplateName
        self.enable_em = enableExtensionMobility
        self.css = callingSearchSpaceName
        self.aar_css = automatedAlternateRoutingCssName
        self.subscribe_css = subscribeCallingSearchSpaceName
        self.ehook_enable = ehookEnable

        if emServiceURL:
            self.services = {'service': [{
                'telecasterServiceName': 'Extension Mobility',
                'name': 'Extension Mobility',
                'url': 'http://10.1.40.11:8080/emapp/EMAppServlet?device=#DEVICENAME#&EMCC=#EMCC#',
                'urlButtonIndex': '1',
                'urlLabel': 'Press here to log in',
            }]
            }
        else:
            self.services = {'service': []}

        if lines:
            self.lines = _add_lines(lines)
        else:
            self.lines = {'line': []}

    def add_phone(self):

        ap = axl.client.service.addPhone({
            'name': self.name,
            'description': self.description,
            'product': self.product,
            'class': self.dev_class,
            'protocol': self.protocol,
            'commonDeviceConfigName': self.common_device_config,
            'softkeyTemplateName': self.softkey_template,
            'phoneTemplateName': self.phone_template,
            'devicePoolName': self.device_pool,
            'locationName': self.location,
            'enableExtensionMobility': self.enable_em,
            'callingSearchSpaceName': self.css,
            'automatedAlternateRoutingCssName': self.aar_css,
            'subscribeCallingSearchSpaceName': self.subscribe_css,
            'lines': self.lines,
            'services': self.services,
            'vendorConfig': [{
                'ehookEnable': self.ehook_enable
            }]
        })

        return ap
