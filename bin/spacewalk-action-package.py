#!/usr/bin/env python
#
# Copyright (c) 2010 Novell, Inc.
# All Rights Reserved.
#
# Based on yum-rhn-plugin
# Copyright (c) 1999-2010 Red Hat, Inc.
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
import os
import sys
import time

sys.path.append("/usr/share/rhn/")

from up2date_client import up2dateLog
from up2date_client import config
from up2date_client import rpmUtils
from up2date_client import rhnPackageInfo
from rpm import RPMPROB_FILTER_OLDPACKAGE

import subprocess
import xml.dom.minidom

log = up2dateLog.initLog()

# file used to keep track of the next time rhn_check 
# is allowed to update the package list on the server
LAST_UPDATE_FILE="/var/lib/up2date/dbtimestamp"

# mark this module as acceptable
__rhnexport__ = [
    'update',
    'remove',
    'refresh_list',
    'fullUpdate',
    'checkNeedUpdate',
    'runTransaction',
    'verify',
    'verifyAll'
]

class Zypper:
    def __init__(self):
        pass

    def __parse_output(self, output):
        log.log_me(output)
        dom = xml.dom.minidom.parseString(output)
        messages = dom.getElementsByTagName("message")
        for message in messages:
            yield message.firstChild.nodeValue

    def __execute(self, args):
        cmd = ["zypper"]
        cmd.extend(args)
        log.log_me("Executing: %s" % cmd)
        task = subprocess.Popen(' '.join(cmd), shell=True, stdout=subprocess.PIPE)
        stdout_text, stderr_text = task.communicate()
        errors = []
        for error in self.__parse_output(stdout_text):
            errors.append(error)            
        return (task.returncode, "\n".join(errors), {})
        
    def install(self, package_list):
        args = ["-n", "-x", "install"]
        args.extend(package_list)
        return self.__execute(args)

    def remove(self, package_list):
        args = ["-n", "-x", "remove"]
        args.extend(package_list)
        return self.__execute(args)


def __package_name_from_tup(tup):
    """ Create a zypper package tuple from an rhn package tuple.
    Choose from the above styles to be compatible with yum.parsePackage
                                                    """
    n, v, r, e, a = tup[:]
    if not e:
        # set epoch to 0 as yum/zypper expects
        e = '0'
    pkginfo = '%s-%s-%s' % (n, v, r)
    return pkginfo

def remove(package_list, cache_only=None):
    """We have been told that we should remove packages"""
    if cache_only:
        return (0, "no-ops for caching", {})

    if type(package_list) != type([]):
        return (13, "Invalid arguments passed to function", {})

    log.log_debug("Called remove_packages", package_list)

    log.log_debug("Called remove", package_list)
    zypper = Zypper()
    return zypper.remove([__package_name_from_tup(x) for x in package_list])

def update(package_list, cache_only=None):
    """We have been told that we should retrieve/install packages"""
    if type(package_list) != type([]):
        return (13, "Invalid arguments passed to function", {})

    log.log_me("Called update", package_list)
    zypper = Zypper()
    return zypper.install([__package_name_from_tup(x) for x in package_list])

def runTransaction(transaction_data, cache_only=None):
    """ Run a transaction on a group of packages. 
        This was historicaly meant as generic call, but
        is only called for rollback. 
        Therefore we change all actions "i" (install) to 
        "r" (rollback) where we will not check dependencies and obsoletes.
    """
    if cache_only:
        return (0, "no-ops for caching", {})
    
    for index, data in enumerate(transaction_data['packages']):
        if data[1] == 'i':
            transaction_data['packages'][index][1] = 'r'
    # TODO
    return (1, "runTransaction not implemented on SUSE systems yet", {})

def fullUpdate(force=0, cache_only=None):
    """ Update all packages on the system. """
    # TODO
    return (1, "fullUpdate not implemented on SUSE systems yet", {})

def checkNeedUpdate(rhnsd=None, cache_only=None):
    """ Check if the locally installed package list changed, if
        needed the list is updated on the server
        In case of error avoid pushing data to stay safe
    """
    if cache_only:
        return (0, "no-ops for caching", {})

    data = {}
    dbpath = "/var/lib/rpm"
    cfg = config.initUp2dateConfig()
    if cfg['dbpath']:
        dbpath = cfg['dbpath']
    RPM_PACKAGE_FILE="%s/Packages" % dbpath

    try:
        dbtime = os.stat(RPM_PACKAGE_FILE)[8] # 8 is st_mtime
    except:
        return (0, "unable to stat the rpm database", data)
    try:
        last = os.stat(LAST_UPDATE_FILE)[8]
    except:
        last = 0;

    # Never update the package list more than once every 1/2 hour
    if last >= (dbtime - 10):
        return (0, "rpm database not modified since last update (or package "
            "list recently updated)", data)
    
    if last == 0:
        try:
            file = open(LAST_UPDATE_FILE, "w+")
            file.close()
        except:
            return (0, "unable to open the timestamp file", data)

    # call the refresh_list action with a argument so we know it's
    # from rhnsd
    return refresh_list(rhnsd=1)
   
def refresh_list(rhnsd=None, cache_only=None):
    """ push again the list of rpm packages to the server """
    if cache_only:
        return (0, "no-ops for caching", {})
    log.log_debug("Called refresh_rpmlist")

    ret = None

    try:
        rhnPackageInfo.updatePackageProfile()
    except:
        print "ERROR: refreshing remote package list for System Profile"
        return (20, "Error refreshing package list", {})

    touch_time_stamp()
    return (0, "rpmlist refreshed", {})

 
def touch_time_stamp():
    try:
        file_d = open(LAST_UPDATE_FILE, "w+")
        file_d.close()
    except:
        return (0, "unable to open the timestamp file", {})
    # Never update the package list more than once every hour.
    t = time.time()
    try:
        os.utime(LAST_UPDATE_FILE, (t, t))

    except:
        return (0, "unable to set the time stamp on the time stamp file %s"
                % LAST_UPDATE_FILE, {})

def verify(packages, cache_only=None):
    log.log_debug("Called packages.verify")
    if cache_only:
        return (0, "no-ops for caching", {})

    data = {}
    data['name'] = "packages.verify"
    data['version'] = 0
    ret, missing_packages = rpmUtils.verifyPackages(packages)
                                                                                
    data['verify_info'] = ret
    
    if len(missing_packages):
        data['name'] = "packages.verify.missing_packages"
        data['version'] = 0
        data['missing_packages'] = missing_packages
        return(43, "packages requested to be verified are missing", data)

    return (0, "packages verified", data)

def verifyAll(cache_only=None):
    log.log_debug("Called packages.verifyAll")
    if cache_only:
        return (0, "no-ops for caching", {})

    data = {}
    data['name'] = "packages.verifyAll"
    data['version'] = 0

    ret = rpmUtils.verifyAllPackages()
    data['verify_info'] = ret
    return (0, "packages verified", data)

# just for testing
if __name__ == "__main__":
    #print update([['rubygem-thoughtbot-shoulda', '2.9.2', '1.1', '', 'x86_64']])
    print remove([['ant', '1.7.1', '12.1', '', 'x86_64']])

    
