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

import sys
#import ConfigParser
#import SQLUtils
import string

# Non Standard imports

#from hwStackTrace import hwStackTrace
from wpl.trace.Trace import traceBack 
from UserDict import UserDict
from DBExceptions import *


#
# The RecordDescriptor class might be obsolete with the new WebForm support
# for additional looping methods. I am probably going to deprecate this in
# the future but it does little harm to keep it here for now.
#

class RecordDescriptor:
    def __init__(self, dict):
        self.dict = dict

    def getDescriptor(self):
        sep=''
        descriptor='('
        for field in self.dict.keys():
            descriptor = descriptor + sep + field
            sep=','
        descriptor = descriptor + ')'
        return descriptor

    def getValues(self):
        return self.dict.values()[:]

    def __str__(self):
        return 'RecordDescriptor:' \
               + self.getDescriptor() \
               + ":" + str(self.getValues())

class Record(UserDict):
    def __init__(self,dict, read_only=1):
        self.read_only = read_only
        UserDict.__init__(self, dict)

    def __repr__(self):
        return 'Record: ' + str(self.data)

    # Please note that any changes to __getattr__ and __setattr__ must be
    # done gingerly as you can seriously break things. Be careful! This
    # is the code that allows you to make "record.fieldName" references
    # in *addition to* the regular record['fieldName'] dictionary reference.
    
    def __getattr__(self,name):
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

    def descriptor(self):
        return RecordDescriptor(self.data)

    def __str__(self):
        rep = '<Record>'
        for field in self.data.keys():
           rep = rep \
                 + '\n' \
                 + ' <Field name="%s" value="%s"/>' % (field,self.data[field])
        rep = rep + '\n' + '</Record>'
        return rep


#
# Factory DataAccess methods. These are all for convenience.
#

def getNewMySQLDataAccess(confFile='sql.conf', confSectionName='Database'):
    return DataAccess(confFile, confSectionName, 'MySQL', MySQLdb='wpl.db.MySQLdb_new')

def getMySQLDataAccess(confFile='sql.conf', confSectionName='Database'):
    return DataAccess(confFile, confSectionName, 'MySQL', MySQLdb='MySQLdb')

def getPostgreSQLDataAccess(confFile='sql.conf', confSectionName='Database'):
    return DataAccess(confFile, confSectionName, 'PostgreSQL')


class DBFactory:


    def __init__(self, db_config_dict ):
        
        #print '%s %s %s' % (confFile, confSectionName, strategy)
        
        self.db_config_dict = db_config_dict
        
        strategy = string.lower( db_config_dict.get( 'strategy', None ) )
        
        if strategy == None:
            raise DBInitError("No valid connection strategy specified. Make sure to specify a 'strategy' key.")
       
        try:
            strategy_name = "%sStrategy"%( strategy )

            strategy_module_name = "wpl.db.%s"%( strategy_name )
            
            DBModule = __import__( strategy_module_name )

            components = string.split( strategy_module_name, '.')
            for comp in components[1:]:
                DBModule = getattr(DBModule, comp)

            #sys.stderr.write( "imported DBModule %s"%( dir(DBModule) ) )

            # create a new instance
            exec_args = " self.db_config_dict "

            exec_string = "self.Strategy = DBModule.%s( %s )"%( strategy_name, exec_args )

            exec( exec_string )

        except:
            raise DBInitError( "FATAL ERROR: Could not import and instantiate appropriate DB strategy.\
            \nDetails: %s"%( traceBack() ) )

    def getDb(self):
        return self.Strategy.getDb()

    def execute(self,query):
        self.Strategy.execute(query)

    def clean(self, text):
        return SQLUtils.escape(str(text))

    def getRecords(self):
        results = self.Strategy.getDictResult()
        records = []
        for result in results:
           records.append(Record(result))
           return records
       
    def __str__(self):
        return str(self.Strategy)

    __repr__ = __str__
