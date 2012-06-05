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
sys.path.append("/usr/share/rhn/")
import xml.etree.ElementTree as etree

from up2date_client import up2dateLog
from actions.packages import Zypper

log = up2dateLog.initLog()

__rhnexport__ = [
    'upgrade']

# action version we understand
ACTION_VERSION = 2

def _change_product(params):
    """Change the product info in /etc/products.d manually"""
    if not params.has_key('products') or not params['products']:
        return 0

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
            root = etree.parse(fpath).getroot()
            name = root.find('name')
            version = root.find('version')
            if not (name and version):
                continue
            if (name.text.strip() == product['name'] and
                version.text.strip() == product['version']):
                    found = True
                    if product.has_key('delete') and product['delete']:
                        os.remove(fpath)
                        continue
                    name.text = product['new_name']
                    version.text = product['new_version']
                    arch = root.find('arch')
                    arch.text = product['new_arch']
                    release = root.find('register/release')
                    release.text = product['new_release']
                    with open(fpath, 'w') as fwrite:
                        fwrite.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                        fwrite.write(etree.tostring(root, encoding="utf-8", method="xml"))
                        fwrite.write('\n')
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

            'full_update: True|False
            If True, perform a 'zypper patch' after the dist upgrade

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
    if type(params) != type({}):
        return (13, "Invalid arguments passed to function", {})

    if params.has_key('change_product') and params['change_product']:
        _change_product(params)

    dup_channel_names = None
    if params.has_key('dup_channel_names') and type(params['dup_channel_names']) == type([]):
        dup_channel_names = params['dup_channel_names']

    zypper = Zypper()
    log.log_me("Called dist upgrade ", dup_channel_names)
    (status, message, data) = zypper.dup(dup_channel_names)
    if not status or not (params.has_key('full_update') and params['full_update']):
        return (status, message, data)

    log.log_me("Called install all patches")
    (pstat, pmsg, pdata) = zypper.patch()
    if str(pstat) == '103':
        # 103 - ZYPPER_EXIT_INF_RESTART_NEEDED
        # a package manager update was installed and there maybe
        # more updates available. Run zypper.patch again
        (pstat, pmsg, pdata) = zypper.patch()
    # after a successfull dup, this action is successfull completed
    # even if zypper.patch() failed. Failed patch installations
    # can be fixed later using normal errata action. No need to
    # rollback the channels which would mess up the system
    return (status, message, data)

