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
# helper class implementing ZYpp script plugin
# text protocol
#
# Author: Duncan Mac-Vicar P. <dmacvicar@suse.de>
# Author: Michael Andres <ma@suse.de>
#
import sys
import os
import re
import logging

# Some modules seem to write debug output to stdout, so we redirect
# it to stderr and use the original stdout for sending back the result.
pluginSendback = sys.stdout
sys.stdout = sys.stderr

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

    You will need to inherit from plugin and implement a handler:

    class MyPlugin(Plugin)
        def INIT(self, headers, body):
            # ... do something
            answer('COMMAND', {"headertag":"header value"}, "multiline\nbody\n" )

    If a handler is not implemented, Plugin will send back a "_ENOMETHOD" message.

    Receiving a _DISCONNECT message the script will close stdin and leave main()
    unless you reimplement it. Upon an ACK response to _DISCONNECT libzypp will not
    attempt to kill the script. An exit value different than 0 may be set via an
    'exit' header in ACK.
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

    def answer(self, command, headers={}, body=""):
        pluginSendback.write("%s\n" % command)
        for k,v in list(headers.items()):
            pluginSendback.write("%s:%s\n" % (k,v))
        pluginSendback.write("\n")
        pluginSendback.write(body)
        pluginSendback.write("%s" % chr(0))
        pluginSendback.flush()

    def ack(self, headers={}, body=""):
        self.answer( "ACK", headers,  body )

    def error(self, headers={}, body=""):
        self.answer( "ERROR", headers,  body )

    def _DISCONNECT(self, headers, body):
	sys.stdin.close()
	self.ack( {'exit':'0'}, 'Disconnect' )

    def current_frame(self):
        return self.framestack[len(self.framestack) - 1]

    def __collect_frame(self):
        frame = self.framestack.pop()
        if frame:
            self.state = "START"
            self.framestack = []
	    try:
		method = getattr(self, frame.command)
	    except:
		self.answer( "_ENOMETHOD", { "Command":frame.command } )
	    else:
		method(frame.headers, frame.body)

    def main(self):
        for line in iter(sys.stdin.readline, ''):
            line = line.rstrip()
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
                result = re.match("(\w+)\:\s*(.+)", line)
                if line == "":
                    self.state = "BODY"
                    #print "wating for body"
                    while 1:
                        c = sys.stdin.read(1)
                        if c == chr(0):
                            #print "got it"
                            break
                        else:
                            #print "no"
                            self.current_frame().body = self.current_frame().body + c
                    self.__collect_frame()
                    if ( sys.stdin.closed ):
			break
                    continue

                elif result:
                    key = result.group(1)
                    val = result.group(2)
                    self.current_frame().headers[key] = val
                    continue
                else:
                    raise Exception("Expect header or new line. Got %s" % line)
