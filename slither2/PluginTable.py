"""

    Slither is a CGI based Web portal and software development framework
    authored in Python. This file is part of Slither.
    Copyright (C) 2001 John Shafaee <pshafaee@hostway.com> and 
    George K. Thiruvathukal <gkt@toolsofcomputing.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Slither is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""


# Standard imports
import string




class PluginTable:


    def __init__( self ):

        self.__table = {}
        pass



    def addPlugin( self, name, reference ):
        """ Adds a plugin to the table. In this version we 
            do not standardize on plugins. """

        name = self.__clean_name( name )

        if name == '':
            return 0 

        # later we may want to make other validations
        self.__table[ name ] = reference
        return 1
        pass


    def removePlugin( self, name ):
        """ Removes a plugin binding. """

        name = self.__clean_name( name )

        if self.__table.has_key( name ):
            del( self.__table[ name ] )
            return 1
        else:
            return 0 
        pass



    def getPlugin( self, name ):
        """ Returns reference to requested plugin. """

        name = self.__clean_name( name )

        return self.__table.get( name , None )



    def getPluginNames( self ):
        """ Gets a list of all bound handler names;
            used by the project class to bind handlers 
            to States. """  
        return self.__table.keys()


    def reset( self ):
        """ Clears the plugin table of all bindings. """

        self.__table.clear()
        pass


    def __clean_name( self, name ):
        """ Internal method used to clean the name of 
            a plugin before adding it to the table. """

        name = string.strip( name )
        return name


    def __str__( self ):
        """ Returns a prinatable representation of the table. """

        s = "PluginTable\n"

        if len( self.__table ) == 0:
            s = string.join( [ s, "(no plugins bound)" ] )
        else:
            for key in self.__table.keys():
                s = string.join( [ s, "\t%s  -->  %s\n"%( key, self.__table[ key ] ) ] )

        return s




if __name__ == '__main__':

    print "\n********* Testing PluginTable **********\n"

    print "Instantiating table..."
    pt = PluginTable()


    print "Printing empty table..."
    print pt


    print "Adding several plugins..."
    pt.addPlugin( "logger" , "PluginA" )
    pt.addPlugin( "mailer" , "PluginB" )
    pt.addPlugin( "translator" , "PluginC" ) 

    print "Printing table..."
    print pt

    print "Removing logger..."
    print pt.removePlugin( "logger" )

    print "Printing table..."
    print pt


    print "Getting a list of plugins...."
    print pt.getPluginNames()

    print "Getting mailer plugin..."
    print pt.getPlugin( "mailer" )

    print "\n******** End of Test ********\n"
