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
# ZYpp system plugin for Spacewalk-like servers
#
# Author: Michael Andres <ma@suse.de>
#

import sys
import os
import traceback

sys.path.append("/usr/share/rhn/")
## for testing add the relative path to the load path
if "spacewalk-system.py" in sys.argv[0]:
  sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../python/zypp'))
else:
  sys.path.insert(0, "/usr/share/zypp-plugin-spacewalk/python")

from plugins import Plugin
from up2date_client import rhnPackageInfo

class SpacewalkSystemPlugin(Plugin):

  def PACKAGESETCHANGED(self, headers, body):
    try:
      rhnPackageInfo.updatePackageProfile()
    except:
      self.error( { "message":"Error refreshing package list" }, traceback.format_exc() )
      return
    self.ack()

plugin = SpacewalkSystemPlugin()
plugin.main()
