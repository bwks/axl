##Python module for configuring cisco cucm with axl soap api.
###Dependencies:
 suds-jurko
 - https://bitbucket.org/jurko/suds
 - http://www.imdb.com/character/ch0005280/ 

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
```
import sys
sys.path.append('/path/to/repo')
```

Import AXL
```
from axl.foley import AXL
```
