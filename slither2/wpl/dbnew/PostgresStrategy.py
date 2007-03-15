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


import string
import _pg

import DataAccess
from wpl.trace.Trace import traceBack
from DBException import *




class PostgresDataAccess(DataAccess.DataAccess):


    def __init__(self, config_dict ):

        dbargs = {}
        dbargs[ 'dbname' ] = config_dict.get( 'db', None )
        dbargs[ 'user' ] = config_dict.get( 'user', None )
        dbargs[ 'passwd' ] = config_dict.get( 'password', None )
        dbargs[ 'host' ] = config_dict.get( 'host', None )

        if config_dict.has_key( "port" ):
            dbargs[ 'port' ] = string.atoi( config_dict.get( 'port', None ) )

            
        self.__db = apply(_pg.connect,(),dbargs)


        
    def getDb(self):
        return self.__db

    
    def execute(self, query):
        try:
            cursor = self.__db.query(query)
        except:
            raise DBCommError("stacktrace:\n%s" % traceBack())

        cursor = DataAccess.DataAccessCursor(cursor, cursor.dictresult)

        return cursor
