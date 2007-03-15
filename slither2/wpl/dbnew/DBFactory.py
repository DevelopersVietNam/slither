"""
        wpl.dbnew is a library file used to access databases from Python.
        This file part of the wpl.dbnew.DBFactory library.
        The following is the BSD license.
        Copyright (c) 2001, John Shafaee <pshafaee@hostway.com>,
        George K. Thiruvathukal <gkt@toolsofcomputing.com>, Jason K. Duffy <jas@friendmail.net>
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

# standard imports
import ConfigParser
import string

from wpl.trace.Trace import traceBack
from DBExceptions import DBInitError



MYSQL = "MySQL"
POSTGRES = "Postgres"

STRATEGY_DICT = {

    MYSQL : "MySQLStrategy",
    POSTGRES : "PostgresStrategy",

    }



class DBFactory:


    def __init__(self):
        pass


    def getDataAccessFromConfig(self, configFile, sectionName="Database"):
        config = ConfigParser.ConfigParser()
        config.read(configFile)
        if not config.has_section(sectionName):
            raise DBInitError, "config has no section %s" % sectionName
        options = config.options(sectionName)
        args = {}
        for opt in options:
            args[opt] = config.get(sectionName, opt)
        
        return self.getDataAccess(args)


    def getDataAccess(self, config_dict ):

        strategy = config_dict.get( 'strategy', None )
        if strategy == None:
            raise DBInitError( "No database 'strategy' specified." )
        elif strategy not in STRATEGY_DICT.keys():
            raise DBInitError( "Database strategy '%s' not supported."%( strategy ) )


        module_name = "wpl.dbnew.%s"%( STRATEGY_DICT[ strategy ] )
        

        try:
            module = __import__( module_name )

            components = string.split( module_name, '.')
            for comp in components[1:]:
                module = getattr(module, comp)
            
            exec( "db_strategy = module.%s( config_dict )"%( STRATEGY_DICT[strategy] ) )

            return db_strategy
            
        except:
            raise DBInitError( "Could not instantiate strategy '%s' from module '%s'.\nDetails: %s" %( strategy,
                                                                                                       module_name,
                                                                                                       traceBack() ) )


if __name__=="__main__":

    test_config = {
        'strategy' : MYSQL,
        'user' : 'pshafae',
        'password' : 'java2000',
        'db' : 'mysql',
        'host': 'localhost'
        }
    
    dba = DBFactory().getDataAccess( test_config )
    c = dba.execute("select * from user")
    res = c.getRecords()
    for row in res:
        print row
    

