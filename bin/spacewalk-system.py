#!/usr/bin/env python
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
