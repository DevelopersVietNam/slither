"""
        wpl.ca is a library file used to wrap the cgi module with
        a large set of additional features. 
        This file part of the wpl.wf.WebForm library.
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
import os
import sys
import cgi
import UserDict

from wpl.trace.Trace import traceBack
from wpl.ca.SimpleCookie import SimpleCookie



class CGIRequest( UserDict.UserDict ):
    

    def __init__( self ):


        self.form = {}
        self.env = os.environ
        self.cookies = {}
        self.user = {}

                
        self.field_storage = cgi.FieldStorage()

        # make sure that the field storage obkect has not
        # been previosly instantiated
        #if len( self.field_storage ) == 0:
        #    raise Exception( "cgi.FieldStorage() method already invoked; no form data can be parsed." )


        self.__parse_form( self.field_storage )

        self.__parse_cookies()


    def __parse_form( self, form ):
	""" Parses the cgi.field storag object into a
        directory name space."""


        # create the form and file directory
        #self.data_dir.create( "/form" )
        #self.data_dir.cd( "/form" )
        
        # go through each field storage data item and
        # add the values to the form dir

        for var in form.keys():
            try:
                if type( form[ var ] ) == type( [] ):
                    # this is a list, first parse it
                    new_list = []
                    for item in form[ var ]:
                        # each is a field storage object
                        if item.filename == None:
                            new_list.append( item.value )
                        else:
                            new_list.append( ( item.filename, item.file ) )

                    # add the new list to /form
                    #self.data_dir[ var ] = new_list
                    self.form[ var ] = new_list

                elif form[ var ].filename == None:
                    # this is not a file, just add it
                    #self.data_dir[ var ] = form[ var ].value
                    self.form[ var ] = form[ var ].value

                else:
                    # this is a file
                    #self.data_dir[ var ] = ( form[ var ].filename, form[ var ].file )
                    self.form[ var ] = ( form[ var ].filename, form[ var ].file )
            except:
               raise Exception( "ERROR: While parsing cgi FieldStorage object. Details: %s"%( traceBack() ) )



    def __parse_cookies( self ):
        """ Parses the HTTP request for any cookies
        information. """

        # create the cookie directory
        #self.data_dir.create( "/cookies" )
        #self.data_dir.cd( "/cookies" )
        
        if os.environ.has_key("HTTP_COOKIE"):
            
            cookie = SimpleCookie()
            cookie.load( os.environ["HTTP_COOKIE"] )
            
            for c in cookie.keys():
                #self.data_dir[ c ] = cookie[ c ]
                self.cookies[ c ] = cookie[ c ]

        pass



    def get( self, var, alternate=None ):
        """ Overrides the UserDict get method for
        safely retrieving value pairs. """

        try:
            data = self.__getitem__( var )
        except:
            data = None
            
        if not data:
            return alternate
        else:
            return data


    def has_key( self, var ):
        """ Overrides the UserDict method for
        checking if a key exists. """

        data = self.get( var )
        if not data:
            return 0
        else:
            return 1


    def __getitem__( self, var ):
        """ Overloads the use of [] operators for
        retreiveing data. """

        if self.user.has_key( var ):
            # first look in user space
            return self.user[ var ]

        elif self.form.has_key( var ):
            # then in the form space
            return self.form[ var ]

        elif self.env.has_key( var ):
            # finally look in the envirnment
            return self.env[ var ]
        
        else:
            # all else failed, raise exception
            raise KeyError( "No such key '%s' in user, form, or environment."%( var ) )



    def __setitem__( self, var, value ):
        """ Overloads the use of [] operatords for
        setting data values. """

        # always set values in the user name space
        self.user[ var ] = value
        pass


    def __delitem__( self, var ):
        """ Overloads the use of [] operatord for
        removing data values. """

        # only remove values from the user namespace
        if self.user.has_key( var ):
            del self.user[ var ]
        pass


    def __getattr__( self, var ):
        """ Ovverides the objects attribute dictionary
        access to allow searching of the user, form,
        and environemnt dictionaries. """

        # first look for any bound variables
        if self.__dict__.has_key( var ):
            return self.__dict__[ var ]

        # now look in the user/form/env name spaces
        try:
            return self.__getitem__( var )
        except:
            raise AttributeError( "No attribute '%s' bound to object or in user, form, env name space."%( var ) )


    def __setattr__( self, attr, value ):
        """ Overrides the objects attrubute dictionary
        manipulator so that new values can be bound. If the
        atribute dictionary has the particular attribute, then
        we update its value. Otherwise, we set the value in
        the user name space. """

        

        if self.has_key( attr ):
            self.__setitem__( attr, value )
        else:
            self.__dict__[ attr ] = value


    def get_field_storage(self):
        return self.field_storage


    def has_cookie( self, cookie_name ):
        """ Boolean check for the availability
        of a particular cookie. """
        return self.cookies.has_key( cookie_name )


    def has_cookies(self):
        """ Method tells you whether any cookies
        are present int the form. """
        return len( self.cookies.keys() ) > 0


    def get_cookie( self, cookie_name ):
        """ Retruns a cookie with matching name.
        Otherwise none. """

        return self.cookies.get( cookie_name, None )


    def get_cookies(self):
        """ Returns the list of cookies to a client. """
        l = []
        for key in self.cookies.keys():
            l.append( self.cookies[ key ] )
            
        return l






