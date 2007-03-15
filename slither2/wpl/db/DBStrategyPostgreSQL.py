"""
        wpl.db is a library file used to access databases from Python.
        This file part of the wpl.db.DBFactory library.
        The following is the BSD license.
        Copyright (c) 2001, John Shafaee <pshafaee@hostway.com>,
        George K. Thiruvathukal <gkt@toolsofcomputing.com>
        All rights reserved.

        Redistribution and use in source and binary forms, with or without modification,
        are permitted provided that the following conditions are met:

        *  Redistributions of source code must retain the above copyright
           notice, this list of conditions and the following disclaimer.
        *  Redistributions in binary form must reproduce the above copyright
           notice, this list of conditions and the following disclaimer
           in the documentation and/or other materials provided with the distribution.
           Neither the name of the authors/associated organization nor the names of its
           contributors may be used to endorse or promote products
           derived from this software without specific prior written permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
        IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
        FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE
        LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
        BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
        BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
        LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
        SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import cgi
import os
import string
import sys
import ConfigParser
#import Path

import _pg

from DBExceptions import *
#from hwStackTrace import hwStackTrace
from wpl.trace.Trace import traceBack

class DBStrategy:
    def __init__(self, confFile="sql.conf", confSectionName="Database", **props):
        try:
           config=ConfigParser.ConfigParser()
           config.read(confFile)
           self.dbProp = config.get(confSectionName,'db')
           self.hostProp = config.get(confSectionName,'host')
           self.userProp = config.get(confSectionName,'user')
           self.passwordProp = config.get(confSectionName,'password')
           self.db = _pg.connect(dbname=self.dbProp,\
                             host=self.hostProp,\
                             user=self.userProp,\
                             passwd=self.passwordProp)
        except:
           raise DBInitError("StackTrace -> " + traceBack())

    def getDb(self):
        return self.db

    def execute(self,query):
        try:
           self.result = self.db.query(query)
        except:
           raise DBCommError("StackTrace -> " + traceBack())

    def getDictResult(self):
        return self.result.dictresult()
    
    def __str__(self):
        passwordEcho = '*' * len(self.passwordProp)
        return "PostgreSQL Strategy -> db=%s host=%s user=%s password=%s" \
           % (self.dbProp,self.hostProp,self.userProp,passwordEcho)

    __repr__ = __str__

