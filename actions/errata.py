#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 1999-2002 Red Hat, Inc.  Distributed under GPL.
#
# Author: Adrian Likins <alikins@redhat.com
#
# Copyright (c) 2010-2011 Novell, Inc.
# All Rights Reserved.
# Author: Ionuț C. Arțăriși <iartarisi@suse.cz>
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

"""Spacewalk client action to install Patches/Erratas"""

import sys
sys.path.append("/usr/share/rhn/")

from up2date_client import rhnserver
from up2date_client import up2dateAuth
from up2date_client import rpmUtils
try:
    from actions import packages
except ImportError:
    from rhn.actions import packages

__rhnexport__ = [
    'update']

# action version we understand
ACTION_VERSION = 2

def __getErrataInfo(errata_id):
    s = rhnserver.RhnServer()
    return s.errata.getErrataInfo(up2dateAuth.getSystemId(), errata_id)

def old_update(errataidlist, cache_only=None):
    # XXX: this method is the one used by yum systems, but it is
    # deprecated and error prone on zypper systems because patches are
    # supposed to be installed by themselves, rather than installing the
    # component packages
    packagelist = []
    for errataid in errataidlist:
        tmpList = __getErrataInfo(errataid)
        packagelist = packagelist + tmpList

    current_packages_with_arch = {}
    current_packages ={}
    for p in rpmUtils.getInstalledPackageList(getArch=1):
        current_packages_with_arch[p['name']+p['arch']] = p
        current_packages[p['name']] = p

    u = {}
    # only update packages that are currently installed
    # since an "applicable errata" may only contain some packages
    # that actually apply. aka kernel. Fun fun fun.

    if len(packagelist[0]) > 4:
        # Newer sats send down arch, filter using name+arch
        for p in packagelist:
            if p[0]+p[4] in current_packages_with_arch:
                u[p[0]+p[4]] = p
            elif p[0]+"noarch" in current_packages_with_arch:
                u[p[0]+p[4]] = p
            elif p[4] == "noarch" and p[0] in current_packages:
                u[p[0]] = p
    else:
        # 5.2 and older sats + hosted dont send arch
        for p in packagelist:
            if p[0] in current_packages:
                u[p[0]] = p


    # XXX: Fix me - once we keep all errata packages around,
    # this is the WRONG thing to do - we want to keep the specific versions
    # that the user has asked for.
    packagelist = [u[a] for a in list(u.keys())]

    if packagelist == []:
        data = {}
        data['version'] = "0"
        data['name'] = "errata.update.no_packages"
        data['erratas'] = errataidlist

        return (39, "No packages from that errata are available", data)

    return packages.update(packagelist, cache_only)

def update(errataidlist, cache_only=None):

    if type(errataidlist) not in [type([]), type(())]:
        errataidlist = [ errataidlist ]

    s = rhnserver.RhnServer()
    if s.capabilities.hasCapability('xmlrpc.errata.patch_names'):
        system_id = up2dateAuth.getSystemId()

        erratas = s.errata.getErrataNamesById(system_id, errataidlist)
        errata_names = [tup[1] for tup in erratas]

        return packages.patch_install(errata_names, cache_only)
    else:
        # see XXX comment in old_update's method definition
        old_update(errataidlist, cache_only)
