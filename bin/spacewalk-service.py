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
import traceback

if not os.path.exists("/etc/sysconfig/rhn/systemid"):
    sys.stderr.write("This system is not registered to any spacewalk server. If the system is not intended to be managed with spacewalk, please uninstall the zypp-plugin-spacewalk package.\n")
    sys.exit(1)

# ma@suse.de: some modules seem to write debug output to stdout,
# so we redirect it to stderr and use the original stdout for
# sending back the result.
sendback = sys.stdout
sys.stdout = sys.stderr

try:
    sys.path.append("/usr/share/rhn/")
    from up2date_client import rhnChannel
    from up2date_client import up2dateErrors
    try:
        from up2date_client.rhncli import utf8_encode
    except ImportError:
        from rhn.i18n import sstr as utf8_encode
except:
    sys.stderr.write("%sPlease install package spacewalk-backend-libs.\n" % traceback.format_exc())
    sys.exit(1)

def _sendback(text):
    sendback.write(utf8_encode("{0}\n".format(text)))

try:
    svrChannels = rhnChannel.getChannelDetails()
except up2dateErrors.NoSystemIdError as e:
    sys.stderr.write("%s\n" % e)
    sys.exit(42)
except up2dateErrors.Error as e:
    sys.stderr.write("%s\n" % e)
    sys.exit(1)
except:
    sys.exit(1)

enable_proxy = rhnChannel.config.cfg['enableProxy']
proxy_config = rhnChannel.config.getProxySetting()

service_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
print("# Channels for service %s" % service_name)
for channel in svrChannels:
    _sendback("")
    if channel['name']:
        _sendback("# Name:        %s" % utf8_encode(channel['name']))
    if channel['summary']:
        _sendback("# Summary:     %s" % utf8_encode(channel['summary']))
    if channel['description']:
        _sendback("# Description:")
        for line in [line for line in channel['description'].split(os.linesep)]:
            _sendback("#   %s" % utf8_encode(line))
        _sendback("#")
    if channel['type']:
        _sendback("# Type:         %s" % utf8_encode(channel['type']))
    if channel['version']:
        _sendback("# Version:      %s" % utf8_encode(channel['version']))
    if channel['arch']:
        _sendback("# Architecture: %s" % utf8_encode(channel['arch']))
    if channel['gpg_key_url']:
        _sendback("# Gpg Key:      %s" % utf8_encode(channel['gpg_key_url']))
    _sendback("[%s]" % utf8_encode(channel['label']))
    _sendback("name=%s" % utf8_encode(channel['name']))
    for i in range(0, len(channel['url'])):
        _sendback("baseurl=plugin:spacewalk?channel=%s&server=%d" % (utf8_encode(channel['label']),i))
    _sendback("enabled=1")
    _sendback("autorefresh=1")
    if channel['type']:
        _sendback("type=%s" % utf8_encode(channel['type']))
    if channel['gpg_key_url']:
        _sendback("gpgkey=%s" % utf8_encode(channel['gpg_key_url']))
    if channel.dict.get('metadata_signed', "0") == "1":
        _sendback("gpgcheck=%s" % utf8_encode(channel.dict.get('gpgcheck', "1")))
    else:
        # bnc#823917: Always disable gpgcheck as SMgr does not sign metadata,
        # even if the original gpg_key_url is known.
        _sendback("gpgcheck=0")
        # fate#314603 check package signature if metadata not signed
        # allow disabling of package gpg check for custom channels
        # This conditional should restore the old behaviour with upstream Spacewalk
        if not channel.dict.get('gpgcheck', None) and not channel['gpg_key_url']:
            _sendback("pkg_gpgcheck=0")
        else:
            _sendback("pkg_gpgcheck=%s" % utf8_encode(channel.dict.get('gpgcheck', "1")))
        _sendback("repo_gpgcheck=0")
    if enable_proxy == 1 and proxy_config:
        _sendback("proxy=%s" % proxy_config)
