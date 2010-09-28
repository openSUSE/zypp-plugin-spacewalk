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

class Plugin:
    """
    The plugin class is offered by ZYpp as a helper
    to handle communication between the plugin and
    libzypp.

    The protocol is similar to stomp, with each frame being:

    COMMAND
    headers

    data
    ^@

    If libzypp calls the plugin with

    INIT
    Param: value
    ^@

    You will need to inherit from plugin:

    class MyPlugin(Plugin)
        def INIT(self, headers, body):
            # ... do something
            answer('COMMAND', {}, body)
    """
    
    def __init__(self):
        self.framestack = []
        self.state = "START"
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    class Frame(object):
        def __init__(self, command):
            self.command = command
            self.headers = {}
            self.body = ""

    def answer(self, command, headers, body=""):
        sys.stdout.write("%s\n" % command)
        for k,v in headers.items():
            sys.stdout.write("%s: %s\n" % (k,v))
        sys.stdout.write("\n")            
        sys.stdout.write(body)
        sys.stdout.write("%s\n" % chr(0))
        
    def current_frame(self):
        return self.framestack[len(self.framestack) - 1]

    def main(self):
        for line in iter(sys.stdin.readline, ''):
            line = line.rstrip()
            if line == "%s" % chr(0):
                frame = self.framestack.pop()
                if frame:
                    method = getattr(self, frame.command)
                    method(frame.headers, frame.body)
                    self.state = "START"
                    self.framestack = []
                    continue
            else:
                if self.state == "START":
                    if re.match("[\w]+", line):
                        frame = self.Frame(line)
                        self.framestack.append(frame)
                        self.state = "HEADERS"
                        continue
                    if line == "":
                      continue
                    else:
                        raise Exception("Expected command")
                if self.state == "HEADERS":
                    result = re.match("(\w+)\: (.+)", line)
                    if line == "":
                        self.state = "BODY"
                        continue
                    elif result:
                        key = result.group(1)
                        val = result.group(2)
                        self.logger.debug("header: %s -> %s\n" % (key,val))
                        self.current_frame().headers[key] = val
                        continue
                    else:
                        raise Exception("Expect header or new line. Got %s" % line)
                if self.state == "BODY":
                    self.current_frame().body = self.current_frame().body + line + "\n"
                    
                
class MediaPlugin(Plugin):

    def INIT(self, headers, body):
        if not os.geteuid() == 0:
            # you can't access auth data if you are not root
            self.answer("ERROR", {}, "Can't access managed repositores without root access")
            return
        if not headers['channel']:
            self.answer("ERROR", {}, "Unknown channel")
            return
        details = rhnChannel.getChannelDetails();
        for channel in details:
            if channel['label'] == headers['channel']:
                self.channel = channel
        if not self.channel:
            self.answer("ERROR", {}, "Can't retrieve information for channel %s" % headers['channel'])
            return
        
        try:
            li = up2dateAuth.getLoginInfo()
            self.auth_headers = li
            #self.answer("META", li)
        except up2dateErrors.RhnServerException, e:
            self.answer("ERROR", {}, str(e))

    def GETFILE(self, headers, body):
        if not headers['path']:
            self.answer("ERROR", {}, "Unknown path")
            return
        url = "%s/GET-REQ/%s%s" % (self.channel['url'], self.channel['label'], headers['path'])
        print "Retrieve %s" % url

plugin = MediaPlugin()
plugin.main()

