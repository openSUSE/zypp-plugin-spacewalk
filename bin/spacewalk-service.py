#!/usr/bin/env python
#
# Copyright (c) 2010 Novell, Inc.
# All Rights Reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, contact Novell, Inc.
#
# To contact Novell about this file by physical or electronic mail,
# you may find current contact information at www.novell.com
#
# ZYpp service plugin for Spacewalk-like servers
# Author: Duncan Mac-Vicar P. <dmacvicar@suse.de>
#
import sys
import os
sys.path.append("/usr/share/rhn/")
from up2date_client import rhnChannel
from up2date_client import up2dateErrors

try:
    svrChannels = rhnChannel.getChannelDetails()
except up2dateErrors.Error, e:
    sys.stderr.write("%s\n" % e)
    exit(1)
except:
    exit(1)

service_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
print "# Repositories for %s" % service_name
for channel in svrChannels:
    print
    print "[%s]" % channel['label']
    print "name=%s" % channel['name']
    print "baseurl=plugin:spacewalk?channel=%s" % channel['label']
    print "enabled=1"



