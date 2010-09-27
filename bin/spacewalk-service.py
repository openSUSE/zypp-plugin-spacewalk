#!/usr/bin/env python
#
# ZYpp service plugin for Spacewalk-like servers
#
# Author: Duncan Mac-Vicar P. <dmacvicar@suse.de>
#
import sys
import os
sys.path.append("/usr/share/rhn/")
from up2date_client import rhnChannel
#from up2date_client import up2dateErrors

svrChannels = rhnChannel.getChannelDetails()
service_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
print "# Repositories for %s" % service_name
for channel in svrChannels:
    print
    print "[%s]" % channel['label']
    print "name=%s" % channel['name']
    print "baseurl=plugin:spacewalk?channel=%s" % channel['label']
    print "enabled=1"



