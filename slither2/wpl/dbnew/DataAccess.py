"""
        wpl.dbnew is a library file used to access databases from Python.
        This file part of the wpl.dbnew.DBFactory library.
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



import UserDict
import string

from DBExceptions import DBUsageError

def escape( text):

    if type( text ) != type( "string" ):
        return text

    text = string.replace(text, "\\", "\\\\")
    text = string.replace(text, "\'", "\\\'")
    text = string.replace(text, "\"", "\\\"")
    return text


class DataAccess:

    def escape(self, text):
        return escape( text )

    def getDb(self):
        raise DBUsageError("Method 'getDB' must be overiden in subclass.")
    
    def execute(self, query):
        raise DBUsageError("Method 'execute' must be overriden in subclass.")


class DataAccessCursor:
    
    def __init__(self, cursor, dictMethod):
        self.__cursor = cursor
        self.__dictMethod = dictMethod
        self.__records = []

    def escape( self, text ):
        return escape( text )    

    def execute(self, query):
        #print "Calling the DataAccess cursor"

        # execute the query right away and cache results
        self.__cursor.execute(query)

        self.__get_records()

        return self
    
    def __get_records(self):
        #print "__get_records called"
        #print "__dictMethod() = ", self.__dictMethod
        results = self.__dictMethod()
        #print results
        records = []
        for result in results:
            #print "appending record..."
            records.append(DataAccessRecord(result))

        self.__records = records

    def getRecords(self):
        #print "in getRecords(): ", self.__records
        return self.__records

    def getLastInsertId( self ):
        return self.__cursor.insert_id()


class DataAccessRecord(UserDict.UserDict):

    def __init__(self, dict, read_only=1):
        self.read_only = read_only
        UserDict.UserDict.__init__(self, dict)

    
    def __repr__(self):
        return str(self.data)


    def __getattr__(self, name):
        if self.data.has_key(name):
            return self.data[name]
        else:
            raise AttributeError(name)

    
    def __setattr__(self, name, value):
        self.__dict__[name] = value

        if self.__dict__.has_key('data'):
            if self.__dict__.has_key('read_only'):
                read_only = self.__dict__['read_only']
                data_ref = self.__dict__['data']
                if read_only:
                    return
                else:
                    data_ref[name] = value

    
    def dumpBindings(self, dict):
        for field in self.data.keys():
            dict[field] = self.data[field]


    def __str__(self):
        rep = ""
        for field in self.data.keys():
            rep = rep + "%s:%s\n" % (field, self.data[field])
        return rep

