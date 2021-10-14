#!/usr/bin/env python
#
# Copyright (c) 2010-2013 Novell, Inc.
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
# ZYpp URL resolver plugin for Spacewalk-like servers
# Author: Duncan Mac-Vicar P. <dmacvicar@suse.de>
#
import sys
import os
import re
import logging
import traceback
sys.path.append("/usr/share/rhn/")
from up2date_client import rhnChannel
from up2date_client import up2dateAuth
from up2date_client import up2dateErrors

from inspect import getargspec

# for testing add the relative path to the load path
if "spacewalk-resolver.py" in sys.argv[0]:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../python'))

from zypp_plugin import Plugin

CONF = "/etc/zypp/zypp.conf"

class SpacewalkResolverPlugin(Plugin):

    """ Pure exception handling """
    def RESOLVEURL(self, headers, body):
        try:
            self.doRESOLVEURL(headers, body)
        except up2dateErrors.Error as e:
            self.answer("ERROR", {}, str(e))
        except:
            self.answer("ERROR", {}, traceback.format_exc())

    """ RESOLVEURL action """
    def doRESOLVEURL(self, headers, body):

        spacewalk_auth_headers = ['X-RHN-Server-Id',
                                  'X-RHN-Auth-User-Id',
                                  'X-RHN-Auth',
                                  'X-RHN-Auth-Server-Time',
                                  'X-RHN-Auth-Expire-Offset']

        if not os.geteuid() == 0:
            # you can't access auth data if you are not root
            self.answer("ERROR", {}, "Can't access managed repositores without root access")
            return


        if 'channel' not in headers:
            self.answer("ERROR", {}, "Missing argument channel")
            return

        if 'server' in headers:
            server = int(headers['server'])
        else:
            server = 0

        # do we have spacewalk-client-tools with timeout option?
        args = getargspec(rhnChannel.getChannelDetails)[0]
        timeout = self._getTimeout()
        if 'timeout' in args:
            details = rhnChannel.getChannelDetails(timeout=timeout)
        else:
            details = rhnChannel.getChannelDetails();

        self.channel = None
        for channel in details:
            if channel['label'] == headers['channel']:
                self.channel = channel
        if not self.channel:
            self.answer("ERROR", {}, "Can't retrieve information for channel %s" % headers['channel'])
            return

        self.auth_headers = {}
        if 'timeout' in args:
            login_info = up2dateAuth.getLoginInfo(timeout=timeout)
        else:
            login_info = up2dateAuth.getLoginInfo()
        for k,v in list(login_info.items()):
            if k in spacewalk_auth_headers:
                self.auth_headers[k] = v
        #self.answer("META", li)

        proxystr = ""
        if rhnChannel.config.cfg['enableProxy'] == 1:
            proxy_config = rhnChannel.config.getProxySetting()
            if proxy_config:
                (proxy_host, proxy_port) = proxy_config.split(':')
                proxystr = "&proxy=%s&proxyport=%s" % (proxy_host, proxy_port)

        # url is a list, use the one provided by the given server
        if type(self.channel['url']) == type([]):
            self.channel['url'] = self.channel['url'][server]
        timeoutstr = ""
        if timeout:
            timeoutstr = "&timeout=%d" % timeout
        url = "%s/GET-REQ/%s?head_requests=no%s%s" % (self.channel['url'],
                                                      self.channel['label'],
                                                      proxystr,
                                                      timeoutstr)

        self.answer("RESOLVEDURL", self.auth_headers, url)

    def _getTimeout(self):
        """ read timeout from config"""
        timeout = None
        if os.path.exists(CONF):
            c = open(CONF, "r")
            for line in c:
                if line[0] == '#':
                    continue
                match = re.match('\s*download.transfer_timeout\s*=\s*(\d+)', line)
                if match:
                    timeout = int(match.group(1))
                    break
            c.close()
        return timeout

plugin = SpacewalkResolverPlugin()
plugin.main()

