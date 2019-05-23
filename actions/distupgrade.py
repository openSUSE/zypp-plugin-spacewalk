#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Novell, Inc.
# All Rights Reserved.
# Author: Michael Calmer <mc@suse.de>
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

"""Spacewalk client action to perform a dist upgrade"""

import os
import sys
import subprocess
sys.path.append("/usr/share/rhn/")
import xml.dom.minidom;
from xml.dom import Node;

from up2date_client import up2dateLog
try:
    from actions.packages import Zypper
except ImportError:
    from rhn.actions.packages import Zypper

log = up2dateLog.initLog()

__rhnexport__ = [
    'upgrade']

# action version we understand
ACTION_VERSION = 2

def __strip_message(code, message, response):
        """reduce text to maximal 1008 characters"""
        if len(message) > 1008:
            textstart = message[:200]
            textend = message[-800:]
            message = "%s\n[...]\n%s" % (textstart, textend)
        return (code, message, response)

def _change_product(params):
    """Change the product info in /etc/products.d manually"""
    if 'products' not in params or not params['products']:
        return 0

    log.log_me("Manually product change requested: %s" % params['products'])
    ret = 0
    for product in params['products']:
        found = False
        for f in os.listdir('/etc/products.d/'):
            fpath = os.path.join('/etc/products.d/', f)
            if found:
                continue
            if os.path.islink(fpath):
                # skip baseproduct link
                continue
            if not os.path.isfile(fpath):
                # skip everything what is not a file
                continue

            dom = xml.dom.minidom.parse(fpath)
            foundName = False
            foundVersion = False
            names = dom.getElementsByTagName('name')
            for name in names:
                if (name.hasChildNodes() and
                    name.firstChild.nodeValue.lower() == product['name']):
                    foundName = True
                    break
            if not foundName:
                continue
            versions = dom.getElementsByTagName('version')
            for ver in versions:
                if (ver.hasChildNodes() and
                    ver.firstChild.nodeValue.lower() == product['version']):
                    foundVersion = True
                    break
            if not foundVersion:
                continue
            found = True

            childs = dom.documentElement.childNodes
            for child in childs:
                if child.nodeType != Node.ELEMENT_NODE:
                    continue
                if (child.tagName == "name" and child.hasChildNodes() and
                    child.firstChild.nodeValue.lower() == product['name']):
                    child.removeChild(child.firstChild)
                    child.appendChild(dom.createTextNode(product['new_name']))
                if (child.tagName == "version" and child.hasChildNodes() and
                    child.firstChild.nodeValue.lower() == product['version']):
                    child.removeChild(child.firstChild)
                    child.appendChild(dom.createTextNode(product['new_version']))
                if product['new_arch'] and child.tagName == "arch":
                    if child.hasChildNodes():
                        child.removeChild(child.firstChild)
                    child.appendChild(dom.createTextNode(product['new_arch']))
                if child.tagName == "register":
                    regchilds = child.childNodes
                    for rc in regchilds:
                        if rc.nodeType != Node.ELEMENT_NODE:
                            continue
                        if rc.tagName == "release":
                            if rc.hasChildNodes():
                                rc.removeChild(rc.firstChild)
                            if product['new_release']:
                                rc.appendChild(dom.createTextNode(product['new_release']))

            fwrite = open(fpath, 'w')
            fwrite.write(dom.toxml('UTF-8'))
            fwrite.close()
            break
        if not found:
            ret = 1
    return ret

def upgrade(params, cache_only=None):
    """Perform a dist upgrade

    params: has to be a dict support the following keys

            'dup_channel_names': ['channelName', ...]
            if channel names are given (as list of strings) a
            'zypper dup --from <channelName> ...'
            is executed. If no channel names given or this
            parameter does not exist, a simple 'zypper dup'
            is executed.

            'full_update': True|False
            If True, perform a 'zypper patch' after the dist upgrade

            'dry_run': True|False
            run without changing the system

            'change_product': True|False
            Some migrations require a manual change of the products.
            Typpical SLE10 installations. If a manual change should be
            made, set this variable to True


            products: [ { name => '...'
                          version => '...'
                          new_name => '...'
                          new_version => '...'
                          new_release => '...'
                          new_arch => '...'
                          delete => True|False
                        },
                        { ... } ]
            The installed product is identified by 'name' and 'version'
            and will be modified with the new_* values.
            If the option 'delete' is True, the product will be removed
            instead of changed.
    """
    log.log_me("distupgrade.upgrade: %s" % params)
    dry_run = False
    full_update = False
    if type(params) != type({}):
        return (13, "Invalid arguments passed to function", {})

    if cache_only:
        return (0, "no-ops for caching", {})

    if 'dry_run' in params and params['dry_run']:
        dry_run = True

    if 'full_update' in params and params['full_update']:
        full_update = True

    if not dry_run and 'change_product' in params and params['change_product']:
        _change_product(params)

    dup_channel_names = None
    if 'dup_channel_names' in params and type(params['dup_channel_names']) == type([]):
        dup_channel_names = params['dup_channel_names']

    zypper = Zypper()
    log.log_me("Called dist upgrade ", dup_channel_names)
    (status, message, data) = zypper.distupgrade(channel_names=dup_channel_names, dry_run=dry_run, run_patch=full_update)

    return __strip_message(status, message, data)

