#!/usr/bin/env python

print "Content-type: text/plain\n\n"

import os

try:
  f = os.popen("hostname")
  print "hostname: %s " % f.read()
  f.close()
except:
  print "Could not run 'hostname' command on your system."

try:
  f = os.popen("whoami")
  print "whoami: %s " % f.read()
  f.close()
except:
  print "Could not run 'whoami' command on your system."

