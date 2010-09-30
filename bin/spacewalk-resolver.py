#!/usr/bin/env python
#
# ZYpp media plugin for Spacewalk-like servers
#
# Author: Duncan Mac-Vicar P. <dmacvicar@suse.de>
#
import sys
import os
import re
import logging
sys.path.append("/usr/share/rhn/")
from up2date_client import rhnChannel
from up2date_client import up2dateAuth
from up2date_client import up2dateErrors

# for testing add the relative path to the load path
if "spacewalk-resolver.py" in sys.argv[0]:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../python/zypp'))
else:
    sys.path.insert(0, "/usr/share/zypp-plugin-spacewalk/python")
    
from plugins import Plugin

class SpacewalkResolverPlugin(Plugin):

    def RESOLVEURL(self, headers, body):

        spacewalk_auth_headers = ['X-RHN-Server-Id', 
                                  'X-RHN-Auth-User-Id',
                                  'X-RHN-Auth',
                                  'X-RHN-Auth-Server-Time',
                                  'X-RHN-Auth-Expire-Offset']
        
        if not os.geteuid() == 0:
            # you can't access auth data if you are not root
            self.answer("ERROR", {}, "Can't access managed repositores without root access")
            return

        
        if not headers['channel']:
            self.answer("ERROR", {}, "Missing argument channel")
            return

        details = rhnChannel.getChannelDetails();
        for channel in details:
            if channel['label'] == headers['channel']:
                self.channel = channel
        if not self.channel:
            self.answer("ERROR", {}, "Can't retrieve information for channel %s" % headers['channel'])
            return

        self.auth_headers = {}
        try:
            login_info = up2dateAuth.getLoginInfo()
            for k,v in login_info.items():
                if k in spacewalk_auth_headers:
                    self.auth_headers[k] = v
            #self.answer("META", li)
        except up2dateErrors.RhnServerException, e:
            self.answer("ERROR", {}, str(e))
        
        url = "%s/GET-REQ/%s" % (self.channel['url'], self.channel['label'])
        self.answer("RESOLVEDURL", self.auth_headers, url)


plugin = SpacewalkResolverPlugin()
plugin.main()

