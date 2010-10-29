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
print "# Channels for service %s" % service_name
for channel in svrChannels:
    print
    if channel['name']:
        print "# Name:        %s" % channel['name']
    if channel['summary']:
        print "# Summary:     %s" % channel['summary']
    if channel['description']:
        print "# Description:"
        for line in [line for line in channel['description'].split(os.linesep)]:
            print "#   %s" % line
        print "#"
    if channel['type']:
        print "# Type:         %s" % channel['type']
    if channel['version']:
        print "# Version:      %s" % channel['version']
    if channel['arch']:
        print "# Architecture: %s" % channel['arch']
    if channel['gpg_key_url']:
        print "# Gpg Key:      %s" % channel['gpg_key_url']
    print "[%s]" % channel['label']
    print "name=%s" % channel['name']
    print "baseurl=plugin:spacewalk?channel=%s" % channel['label']
    print "enabled=1"
    print "autorefresh=1"
    if channel['type']:
        print "type=%s" % channel['type']
    if channel['gpg_key_url']:
	print "gpgkey=%s" % channel['gpg_key_url']
    else:
	print "gpgcheck=0"

