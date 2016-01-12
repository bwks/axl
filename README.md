##Python module for configuring Cisco UCM with AXL SOAP API
###Dependencies
 suds-jurko
 - https://bitbucket.org/jurko/suds

###Links
 - http://www.imdb.com/character/ch0005280/ 
 - https://developer.cisco.com/site/axl/

###Testing Environment
AXL configuration testing has been completed against CUCM v10.5

Installed environment:
 - Centos 7
 - Python 3
 - suds-jurko

###Installation
Clone repository
```bash
BradsMBP# mkdir test
BradsMBP# cd test
BradsMBP# git clone https://github.com/bobthebutcher/axl.git
Cloning into 'axl'...
remote: Counting objects: 174, done.
remote: Compressing objects: 100% (24/24), done.
remote: Total 174 (delta 11), reused 0 (delta 0), pack-reused 150
Receiving objects: 100% (174/174), 44.67 KiB | 0 bytes/s, done.
Resolving deltas: 100% (94/94), done.
Checking connectivity... done.
BradsMBP#
```

###Example Usage
Update your path
```python
import sys
sys.path.append('/path/to/repo')
```

Import AXL
```python
from axl.foley import AXL
```

####Creating connection to CUCM

The user will need the appropriate privileges to access the API
```python
cucm = '10.10.11.14'
wsdl = 'file:///path/to/wsdl/schema/10.5/AXLAPI.wsdl'
ucm = AXL('username', 'password', wsdl, cucm)
```

####Adding a location
```python
ucm.add_location(location='test_location')
{'success': True, 'error': '', 'response': 'Location successfully added'}
```

####Adding a region
```python
ucm.add_region(region='test_region')
{'success': True, 'error': '', 'response': 'Region successfully added'}
```

####Adding a device pool
```python
ucm.add_device_pool(device_pool='test_dev_pool', region='test_region', location='test_location')
{'success': True, 'error': '', 'response': 'Device pool successfully added'}
```

####Deleting a region

Like in the UCM web interface all dependencies must be removed before an object can be deleted
```python
ucm.delete_region(region='test_region')
{'success': False,
 'error': Key value for constraint (informix.pk_region_pkid) is still being referenced.,
 'response': 'Region could not be deleted'}
```

####Add a route list
```python
ucm.add_route_list(route_list='test_rl1', route_group='test_rg')
{'success': True, 'response': 'Route list successfully added', 'error': ''}
```