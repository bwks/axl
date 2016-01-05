##Python module for configuring Cisco UCM with AXL SOAP API
###Dependencies:
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

###Installation:
Clone repository
```
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

###Example Usage:
Update your path
```python
import sys
sys.path.append('/path/to/repo')
```

Import AXL
```python
from axl.foley import AXL
```

Create connection to CUCM

The user will need the appropriate privileges to access the API
```python
cucm = '10.10.11.14'
wsdl = 'file:///path/to/wsdl/schema/10.5/AXLAPI.wsdl'
ucm = AXL('username', 'password', wsdl, cucm)
```

Configure a location
```python
ucm.add_location('test_location')
{'success': True, 'error': '', 'msg': 'Location successfully added'}
```

Methods return result as a dictionary of values
```python
{
'success': True/False, 
'error': 'AXL Error', 
'msg': 'Error Message'
}
```

Duplicate value error
```python
ucm.add_location('test_location')
{'success': False,
 'error': Could not insert new row - duplicate value in a UNIQUE INDEX column (Unique Index:).,
 'msg': 'Location already exists'}
```
