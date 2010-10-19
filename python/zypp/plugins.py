
#!/usr/bin/env python
#
# helper class implementing ZYpp script plugin
# text protocol
#
# Author: Duncan Mac-Vicar P. <dmacvicar@suse.de>
#
import sys
import os
import re
import logging

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

    def answer(self, command, headers={}, body=""):
        sys.stdout.write("%s\n" % command)
        for k,v in headers.items():
            sys.stdout.write("%s:%s\n" % (k,v))
        sys.stdout.write("\n")
        sys.stdout.write(body)
        sys.stdout.write("%s" % chr(0))
        sys.stdout.flush()

    def ack(self, headers={}, body=""):
        self.answer( "ACK", headers,  body )

    def error(self, headers={}, body=""):
        self.answer( "ERROR", headers,  body )

    def current_frame(self):
        return self.framestack[len(self.framestack) - 1]

    def __collect_frame(self):
        frame = self.framestack.pop()
        if frame:
            method = getattr(self, frame.command)
            method(frame.headers, frame.body)
            self.state = "START"
            self.framestack = []

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
                    continue

                elif result:
                    key = result.group(1)
                    val = result.group(2)
                    self.current_frame().headers[key] = val
                    continue
                else:
                    raise Exception("Expect header or new line. Got %s" % line)
