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
import os.path
import string
import sys


# Non-standard imports
from wpl.wf.WebForm import WebForm
from wpl.wp.Emitter import StringEmitter

from Exceptions import StateInterfaceException


class State:


    def __init__( self ):
        
        # these will be set in ini_state()
        self.project_profile = None
        self.state_name = None
        self.__call_path = None
        self.call_path = None
        self.module_path = None
        self.user_profile = None
        self.webroot = None
        self.Request = None
        self.Response = None
        #self.load_state_module = None
        self.project = None

        pass


    def init_state( self, **options ):
        """ Public method used to initialize the class
            after it has been instantiated. Needed to init.
            WebForm superclass. """

        self.project_profile = options[ 'project_profile' ]
        self.state_name = options[ 'state_name']
        #self.argv = options[ 'argv' ]
        self.__call_path = options[ 'call_path' ]
        self.call_path = options[ 'call_path' ]
        self.module_path = options[ 'path' ]
        self.user_profile = options[ 'user_profile' ]
        #self.page_vars = options[ 'page_vars' ]
        self.webroot = options[ 'webroot' ]
        self.Request = options[ 'Request' ]
        self.Response = options[ 'Response' ]
        self.project = options[ 'project' ]

        #form = options[ 'cgi_form' ]
        #options[ 'emit_strategy' ] = StringEmitter()
        #options[ 'write_content_type' ] = 'no'
        #options[ 'write_cookies' ] = 'no'
        #options[ 'encode_target' ] = None 
        #apply( WebForm.__init__, [self, form], options )

        # bind Project webform cookies to State webform ookies
        #self.cookies = options[ 'cookies' ]

        #self.add_var( 'base_project_url', options[ 'base_project_url' ] )
        #self.add_var( 'state_name', self.state_name )
        #self.Response.add_var( 'base_project_url', options[ 'base_project_url' ] )
        self.Response.add_var( 'state_name', self.state_name )

        #self.load_state_module = options[ "load_state_module" ]

        self.__next_call_path = ''
        self.__main_template_file = ''
        

    def init( self ):
        """ Replacement of __init__. Called after the object has
        been properly instantiated. """

        pass



    def render( self ):
        raise StateInterfaceException( "State render() method must be overriden." )
        pass




    def process( self ):
        raise StateInterfaceException( "State process() method must be overriden." )
        pass


    def encode( self, encode_file_name, prepend_text="" ):
        return self.Response.encode( encode_file_name, prepend_text )


    def scheduleState( self, call_path ):
        """ Schedules another state to load after the exectuon of
            the current state. All schedules are saved in the UserProfile
            object and accessed by the Driver. """

        if type( call_path ) != type( '' ):
            return

        #sys.stderr.write( "cwd = %s"%( os.getcwd() ) )
        #sys.stderr.write( "call path file: %s\n"%( "./" + string.split(call_path,'.')[0] + ".py" ) )
        #sys.stderr.write( "is file = %s\n"%(os.path.isfile( "./" + string.split(call_path,'.')[0] + ".py" ) ) )

        
        #sys.stderr.write( "call_path = %s\n"%( call_path ) )

        if call_path[0] != '/' and \
           os.path.isfile( "./" + string.split(call_path,'.')[0] + ".py" ):

            call_path = string.join( [ self.__call_path , call_path ], '/' )

        self.__next_call_path = call_path


    def getNextCallPath( self ):
        return self.__next_call_path


    def anotherStateScheduled( self ):
        """ Convenience method used to check if another
            state has bee scheduled. Retruns boolean value. """

        if self.__next_call_path != '':
            return 1
        else:
            return 0
        

    def set_main_template( self, template_file_name ):
        """ Used to select a template file to be used when
        diaplying the state content. """

        self.__main_template_file = template_file_name


    def main_template_changed( self ):
        """ Use to check if a different template file
        has ben selected. """

        if self.__main_template_file != '':
            return 1

        return 0

    def get_main_tempalte(self):
        """ Returns the template file set. """
        return self.__main_template_file
