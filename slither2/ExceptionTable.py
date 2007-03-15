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




class ExceptionHandler:

    def __init__( self ):
        pass

    def handleException( self, exception, value, tb ):
        """ Must be overloaded to handle the exception. By 
            default nothing is done. """
        pass

    def toString( self, exception, value, tb ):

        return """
        <table border="1">
        <tr>
           <td><i>Exception:</i></td><td><pre>%s</pre></td>
        </tr>
        <tr>
           <td><i>Value:</i></td><td><pre>%s</pre></td>
        </tr>
        <tr>
           <td><i>Traceback:</i></td><td> <pre>%s</pre></td>
        </tr>
        </table> """%( exception, value, tb )


class ExceptionTable:


    def __init__( self ):

        self.__table = {}
        pass



    def addHandler( self, name, handler ):
        """ Add a new exception type/name and handler. """

        name = self.__clean_name( name )

        # make sure that handler is of type ExceptionHandler
        if not isinstance( handler, ExceptionHandler ) or name == '':
            return 0

        # add handler to table using name as key
        self.__table[ name ] = handler

        return 1
        pass


    def removeHandler( self, name ):
        """ Removes a handler from the table. """
       
        name = self.__clean_name( name )
 
        if self.__table.has_key( name ):
            del( self.__table[ name ] )
            return 1

        else:
            return 0
        pass


    def reset( self ):
        """ Clears the exception table. """

        self.__table.clear()
        pass


    def getHandler( self, name, default=None ):
        """ Returns a reference to a handler for a particular
            exception name or type. Otherwise None is returned. """

        # clean the exception name
        name = self.__clean_name( name )

        # locate and return the appropriate handler
        return self.__table.get( name, default )

        pass


    def __clean_name( self, name ):
        """ Internal method used to make sure that the exception
            name is cleaned. Extracts class name from the string
            if a fully qualified class name is given. """

        # clean the exception name
        if type( name ) != type( 'string' ):
            name = str( name )

        name = string.strip( name )

        # save a copy of the original name
        original_name = name

        # attempt to extract the class name of excepton
        name = string.split( name, '.' )[-1]

        if name == '':
            name = original_name

        return name



    def __str__( self ):
        """ Returns a string representation fo the table."""

        s = "ExceptionTable\n"

        if len( self.__table.keys() ) == 0:
            s = string.join( [ s, "(no assigned handlers)" ] )

        else:
            for key in self.__table.keys():
                s = string.join( [ s, "\t%s  -->  %s\n"%( key, self.__table[ key ] ) ] )

        return s
        pass








class test_handler1:

    def __init__( self, name ):
        self.name = name
        pass

    def handleException( self, exception, value, tb ):
        print "%s is handling problem..."%( self.name ) 


class test_handler2( ExceptionHandler ):

    def __init__( self, name ):
        self.name = name
        pass

    def my_handle( self, exception, value, tb ):
        print "%s is handling problem..."%( self.name )


class test_handler3( ExceptionHandler ):

    def __init__( self, name ):
        self.name = name
        pass

    def handleException( self, exception, value, tb ):
        print "%s is handling problem..."%( self.name )


if __name__ == '__main__':

    print "\n******** Testing ExcetionTable **********\n"

    print "Creating instance of ExceptionTable..."
    et = ExceptionTable()


    print "Printing empty ExcetpionTable..."
    print et


    print "Instantiating handlers..."
    h1 = test_handler1( "Test Handler 1" )
    h2 = test_handler2( "Test Handler 2" )
    h3 = test_handler3( "Test Handler 3" )
    

    print "Attempting to add bogus handler..."
    print et.addHandler( "Exception" , h1 ) 

    print "Adding handler for Exception exception..."
    print et.addHandler( "exception.Exception", h3 )

    print "Adding handler for MyException..."
    print et.addHandler( "MyException", h3 )

    print "Adding approved handler with improperly overloaded handle method..."
    print et.addHandler( "BadHandler" , h2 ) 

    print "Printing ExceptionTable..."
    print et

    print "Getting and invoking handler for Exception..."
    h = et.getHandler( "exception.Exception" )
    if  h != None:
        h.handleException( "a vlaue" )
    else:
        print "(bad or un assigned handler)"


    print "Getting and invoking handler for MyException..."
    h = et.getHandler( "exception.someotherclass.MyException" )
    if  h != None:
        h.handleException( "a vlaue" )
    else:
        print "(bad or un assigned handler)"

    print "Getting and invoking handler for BadHandler exception..."
    h = et.getHandler( "BadHandler" )
    if  h != None:
        h.handleException( "a vlaue" )
    else:
        print "(bad or un assigned handler)"


    print "Getting and invoking handler for bogus exception..."
    h = et.getHandler( "bad_exception" )
    if  h != None:
        h.handleException( "a vlaue" )
    else:
        print "(bad or un assigned handler)"

    print "\n******** End of Test **********\n"
