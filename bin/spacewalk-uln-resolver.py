#!/usr/bin/env python
#
# Copyright (c) 2019, SUSE Linux GmbH.
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
import configparser
import urllib.parse

sys.path.append("/usr/share/rhn/")

from up2date_client import rhnChannel, up2dateAuth, up2dateErrors
from up2date_client.rpcServer import RetryServer, ServerList
from spacewalk.common.suseLib import get_proxy
from inspect import getargspec

# for testing add the relative path to the load path
if "spacewalk-uln-resolver.py" in sys.argv[0]:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../python'))

from zypp_plugin import Plugin

CONF = "/etc/zypp/zypp.conf"


class SpacewalkULNPlugin(Plugin):
    """
    Pure exception handling.
    """
    ULN_CONF_PATH = '/etc/rhn/spacewalk-repo-sync/uln.conf'
    DEFAULT_ULN_HOST = "linux-update.oracle.com"

    def __init__(self):
        Plugin.__init__(self)
        self._uln_token = None
        self._uln_url = None

    def _get_hostname(self, url) -> tuple:
        """
        Get label from the URL (a hostname).

        :raises RhnSyncException: if URL is wrongly formatted.
        :returns: tuple (hostname, label)
        """
        if not url.startswith("uln://"):
            raise RhnSyncException("URL must start with 'uln://'.")
        p_url = urllib.parse.urlparse(url)
        return p_url.netloc or self.DEFAULT_ULN_HOST, p_url.path

    def _get_credentials(self) -> tuple:
        """
        Get credentials from the uln.conf

        :raises AssertionError: if configuration does not contain required sections.
        :returns: tuple of username and password
        """
        config = configparser.ConfigParser()
        config.read(self.DEFAULT_ULN_HOST)
        if "main" in config:
            sct = config["main"]
            username, password = sct.get("username"), sct.get("password")
        else:
            username = password = None
        assert username is not None and password is not None, "Credentials were not found in the configuration"

        return username, password

    def _authenticate_uln(self, url):
        """
        Get ULN token.

        :raises RhnSyncException: if configuration does not contain required sections.
        :returns: ULN token
        """
        usr, pwd = self._get_credentials()
        px_url, px_usr, px_pwd = get_proxy(url)
        hostname, label = self._get_hostname(url)
        self._uln_url = "https://{}/XMLRPC/GET-REQ{}".format(hostname, label)
        server_list = ServerList(["https://{}/rpc/api".format(hostname)])
        retry_server = RetryServer(server_list.server(), refreshCallback=None, proxy=None,
                                   username=px_usr, password=px_pwd, timeout=5)
        retry_server.addServerList(server_list)
        self._uln_token = retry_server.auth.login(usr, pwd)

    def RESOLVEURL(self, headers, body):
        """
        Resolve URL.

        :returns: None
        """
        url = 'uln:///no-idea-yet'  # get it from uln.conf
        try:
            self._authenticate_uln(url)
            auth_headers = {
                "X-ULN-Api-User-Key": self._uln_token
            }
            self.answer("RESOLVEDURL", auth_headers, self._uln_url)
        except Exception as exc:
            self.answer("ERROR", {}, str(exc))

plugin = SpacewalkULNPlugin()
plugin.main()

