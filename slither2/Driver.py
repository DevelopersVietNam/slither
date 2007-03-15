#!/usr/local/python2.1/bin/python
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
import os
import os.path
import sys
import urlparse



# Non-standard import
import Path
Path.path.addDir( os.getcwd() )


from wpl.trace.Trace import traceBack
from wpl.logger.Logger import LogWriter
from wpl.wp.WriteProcessor import WriteProcessor
from wpl.wp.Emitter import Emitter
from wpl.wp.Emitter import StringEmitter


from Project import Project

from SharedResources import change_cwd

from Exceptions import LoadException



# Constants
PANIC_HTML = 'Panic.html'




class Driver:


    def __init__( self, argv ):


        # attempt to import DriverConf
        self.driver_conf = None
        try:
            self.driver_conf = __import__( "DriverConf" )
        except:
            self.driver_conf = None

        # initialize systm variables
        self.log_file_name = self.get_system_variable( "LOG_FILE", "./logs/Driver" )


        # create logger
        # (NOTE: Later we will want to allow other strategies to be
        #        specified as well. )
        self.logger = LogWriter( self.log_file_name, log_details = 0 )


        self.__argv = argv
        ( self.__driver_path , self.__driver_file_name ) = os.path.split( os.path.abspath( self.__argv[ 0 ] ) )

        self.logger.writeDebug( "__driver_path -> %s"%( self.__driver_path ) )
        self.logger.writeDebug( "__driver_file_name -> %s"%( self.__driver_file_name ) )


        pass


    def get_system_variable( self, var_name, alternate ):
        """ Initialize a system variable. """

        if self.driver_conf == None:
            return alternate

        if hasattr( self.driver_conf, var_name ):
            return getattr( self.driver_conf, var_name )
        else:
            return alternate

        pass



    def process( self ):
        """ Main method called by WebForm auto dispatcher to 
            begin processing. Handles locating and loading a project
            based on the URL call. """

        if self.driver_conf == None:
            self.__panic( "Missing DriverConf.py" , """Could not find module DriverConf.py in the slither directory.
            Please make sure that this file exists and has the appropriate permissions. """ )

        # attempt to get the project binding dict
        if not hasattr( self.driver_conf, "projects" ):
            self.__panic( "Missing 'projects' dictionary.", """Could not find the 'projects' directory in DriverConf.py.
            Please make sure that the dictionary exists and properly defined. """ )

        self.__project_dict = getattr( self.driver_conf, "projects" )
            
        self.logger.writeDebug( "Loaded base projects dictionary.\nproject_dict = %s"%( self.__project_dict ) )


        # parse the URL
        url_profile = self.__parse_url( os.environ.get( 'REQUEST_URI', '' ) )

        # attempt to load the project
        ( project_profile, load_msg, tb ) = self.__load_project( url_profile )
 
        if project_profile:
            try:
                self.logger.writeDebug( "Running project..." )

                # dispatch the project
                output = project_profile['project'].run()

                change_cwd( self.__driver_path )

                self.logger.writeDebug( "Printing result" )


                #self.logger.writeEntry( "OUTPUT: %s"%(output[:500]) )

                # output the results to the browser
                #sys.stdout.write( output )
                sys.stdout.write( output )

            except:
                # an error occured during dispatching
                sys.stdout = project_profile['project'].stdout_save
                error_msg = "Project '%s' experienced errors during execution.\n"%( project_profile['project_name'] )
                self.logger.writeError( error_msg ) 
                change_cwd( self.__driver_path )
                self.__panic( "Fatal project execution error.", error_msg, traceBack() )
            else:
                sys.exit( 0 )

        else:
            #error_msg = "One more problems encountered when loading the requested project.\n%s"%( load_msg )
            self.logger.writeError( load_msg )
            self.__panic( "Could not load project.", load_msg, tb )




    def __load_project( self, url_profile ):
        """ Internal method used to load the properties of 
            a project so that the project can be dispatched. """
        
        try:
            tb = ""
            
            project_name = url_profile[ 'project_name' ]

            if project_name == "":
                raise LoadException( "No project name specified." )

            # read proeprty from conf file
            project_profile = self.__project_dict.get( project_name, None )
            

            if project_profile == None:
                raise LoadException( "No registration found for project name '%s'."%( project_name ) )
            else:
                # at this point we have a prety good chance of loading the project
                project_profile[ 'project_name' ] = project_name
                project_profile[ 'project_state_path' ] = url_profile[ 'state_path' ]
                project_profile[ 'base_url' ] = url_profile[ 'base_url' ]
                

            # check project properties
            if project_profile.get( 'webroot', '' ) == '' or \
               project_profile.get( 'project_module' , '' ) == '':

                raise LoadException( "Project '%s' missing valid entries for 'webroot' \
                                      or 'project_module'  properties."%( project_name ) )

            # we assume that the project_class has the same name as the
            # project_module if the project_class property is not supplied. 
            project_profile[ 'project_class' ] = project_profile.get( 'project_class', project_profile[ 'project_module' ] )

            ( chdir_result, chdir_msg ) = change_cwd( project_profile.get( 'webroot', '' ) )
            if not chdir_result:
                raise LoadException( "The registered path '%s' for project '%s' does \
                not appear to be a valid or accessible. %s"%( project_profile[ 'webroot' ], 
                                                              project_name, chdir_msg ) )

            self.logger.writeDebug( "cwd = %s"%(os.getcwd() ) )
            #for p in sys.path:
            #  self.logger.writeDebug( "%s"%(p) )
            sys.path = [ "." ] + sys.path

            # add to the project profile some useful information
            project_profile[ "slither_driver_path" ] = self.__driver_path

            # import the Project file
            project_module = __import__( project_profile[ 'project_module' ] )

            self.logger.writeDebug( "Imported project module!" )

            # create new instance of the project
            instance_code = "project = project_module.%s()"%( project_profile['project_class'] ) 

            self.logger.writeDebug( "Executing instance_code : %s"%( instance_code ) ) 

            exec instance_code 

            self.logger.writeDebug( "Project '%s' successfully instantiated."%( project_name ) )

            # make sure that this class is an instance of Project
            if not isinstance( project, Project ):
                raise LoadException( "Class %s.%s is not an instance of the Project class."%( project_profile['project_module'],
                                                                                              project_profile['project_class'] ) ) 

            project.init_project( project_profile = project_profile, argv = self.__argv[1:] )

            # call the project's init method
            project.init()

            project_profile[ 'project' ] = project

            return ( project_profile , "Successfully loaded project '%s'."%( project_name ), "" )

        except LoadException, details:
            error_msg = "Invalid project properties. %s"%( details )

            tb = ""

        except ImportError, details :
            error_msg = "Could not import project module '%s' for project name '%s'.\n \
                         Check that the module exists at the specified file path.\n \
                         %s"%( project_profile[ 'project_module' ], project_name, details )
            tb = ""

        except AttributeError, details :
            error_msg = "Could not instantiate class '%s' for project \n \
            name '%s'. Make sure the class name is correct in module '%s'."%( project_profile['project_class'],
                                                                              project_profile['project_name'], 
                                                                              project_profile['project_module'],
                                                                              )
            tb = traceBack()

        except:
            error_msg = "Unexpected error while loading project '%s'."%( project_name )
            tb =  traceBack()

        # post exception processing
        self.logger.writeError( error_msg + "Traceback: " + tb )

        change_cwd( self.__driver_path )

        return ( None, error_msg, tb )




    def __parse_url( self, url ):
        """ Internal method used to parse the calling URL into
            sub pieces used to load the project and later the
            requested state. """

        self.logger.writeDebug( "Parsing URL: %s"%( url ) )

        url_property = {}
        url_property[ 'project_name' ] = ''
        url_property[ 'state_path' ] = ''


        # split url based '/' 
        url      = string.split( url , '?' )[0]
        url_list = string.split( url , '/' )

        
        request_path = ''
        driver_found = 0
        for entry in url_list:
            if entry == self.__driver_file_name:
                driver_found = 1
                
            elif driver_found == 1:
                if url_property[ 'project_name' ] == '':
                    url_property[ 'project_name' ] = entry
                else:
                    if entry != '':
                        url_property[ 'state_path' ] = string.join( [ url_property[ 'state_path' ] , entry ], '/' ) 
                    else:
                        pass
            else:
                request_path = string.join( [ request_path, entry ], '/' )
                pass


        # build call URL
        port = ''
        if os.environ.get( 'SERVER_PORT', '80' ) != '80':
            port = ":%s"%( os.environ.get( 'SERVER_PORT', '80' ) )

        #server = "%s%s"%( os.environ.get( 'SERVER_NAME' ,"ERROR_NO_SERVER_DETECTED" ), port )

        #request_path = string.join( [request_path, self.__driver_file_name, url_property[ 'project_name' ] ], '/' )[1:]

        # find out what protocol we are using
        protocol = os.environ.get( 'SERVER_PROTOCOL' ,"file" )
        if not protocol:
            protocol = "file"
        protocol = string.lower( protocol )
        protocol = string.split( protocol , "/" )[0]

        # account for https
        if port == "443" or os.environ.has_key( "HTTPS" ):
            protocol = "https"
            port = ""

        server = "%s%s"%( os.environ.get( 'SERVER_NAME' ,"ERROR_NO_SERVER_DETECTED" ), port )

        request_path = string.join( [request_path, self.__driver_file_name, url_property[ 'project_name' ] ], '/' )[1:]
        
        # build the base URL
        url_property[ 'base_url' ] = urlparse.urlunparse( (protocol, server, request_path, '', '', '' ) )

        self.logger.writeDebug( "Parsed URL profile generated.\nurl_property = %s"%( url_property ) ) 

        return url_property



    def __panic( self, subject="", error_msg="", tb="" ):
        """ Print an error page wit the specified message
            and exit the application. """

        if subject == "":
            subject = "(unexpected error)"

        if error_msg == "":
            error_msg = "Non-specified fatal error has occured in Driver execution!"


        # log the message as an error
        # NOTE: Need to make this better and smoother in the future
        self.logger.writeError( error_msg + "\n" + tb )

        # emit MIME type for HTTP response
        sys.stdout.write( "Content-type: text/html\n\n" )

        def_dict = {}
        def_dict[ "subject" ]   = subject
        def_dict[ "error_msg" ] = error_msg
        def_dict[ "log_file" ]  = self.log_file_name

        if tb != "":
            def_dict[ "tb" ]    = "<pre>" + tb + "</pre>"

        #if self.__project_dict != None:
        #    # build a printable representation of registered
        #    # prjects
        #    s = ""
        #    for p in self.__project_dict.keys():
        #        pd = self.__project_dict[ p ]
        #        s = s + """<tr><td valign="top" ><b>%s</b></td><td><table>"""%( p )
        #        for prop in pd.keys():
        #            s = s + """<tr><td>%s</td><td>%s</td></tr>"""%( prop, pd[ prop ] )
        #
        #        s = s + "</table></td></tr>"
        #
        #    def_dict[ "projects" ] = s
            

        # load writeprocessor to display the error page
        emitter = Emitter()    
        writer = WriteProcessor( PANIC_HTML, '.', def_dict, emitter=emitter )

        writer.process()

        self.logger.writeDebug( "Printing out PANIC message." )

        # print the page
        sys.stdout.write( emitter.getResult() )

        # exit
        sys.exit( 1 )


if __name__ == '__main__':


   d = Driver( sys.argv )
   d.process()
 
