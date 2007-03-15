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
import sys
import os
import os.path
import string
import cPickle
import StringIO



#stdout_capture = StringIO.StringIO()
#stdout_save = sys.stdout
#sys.stdout = stdout_capture


# Non-standard import
import PluginTable
import ExceptionTable


from UserProfile import UserProfile

from Exceptions import LoadException
from Exceptions import StageProcessException



from SharedResources import change_cwd
from SharedResources import format_dict
from State import State 

#from wpl.wf.WebForm import WebForm
from wpl.logger.Logger import LogWriter
from wpl.trace.Trace import traceBack
from wpl.path import Path

from wpl.ca import CGIRequest
from wpl.ca import CGIResponse 


class stdout_to_log:

    def __init__( self, logger_instance ):
        self.logger_instance = logger_instance

    def write( self, s ):
        self.logger_instance.writeEntry( string.strip(s), "PRINT" )



###
# constants
SYSTEM_LOG_ENTRY   = "SYSTEM"
SYSTEM_LOG_ERROR   = "SYSTEM ERROR"
SYSTEM_LOG_WARNING = "SYSTEM WARNING"
SYSTEM_LOG_DEBUG   = "SYSTEM DEBUG"


class Project:


    def init_project( self, ** options ):
        """ Public method for initializing the object after
            instantiation. """


        # set the project in the python path
        Path.path.addDir( os.getcwd() )

        # instantiate the CGI request and response objects
        self.Request  = CGIRequest.CGIRequest()
        self.Response = CGIResponse.CGIResponse()

        # make sure we are not being called from anywhere
        # else except the Driver
        
        from ProjectConf import LOCAL_PROPS 
        self.__props = LOCAL_PROPS

        self.project_profile = options.get( 'project_profile', '' )

        # copy local props to project_profile
        for key in self.__props.keys():
            if not self.project_profile.has_key( key ):
                self.project_profile[ key ] = self.__props[ key ]


        # by default, attempt to set the encode target and template
        # search path as defined in the ProjectConf.py file
        if self.project_profile.get( "encode_target" , "" ) != "":
            self.Response.set_encode_file_name( self.project_profile["encode_target"] )

        self.Response.set_search_path( self.project_profile.get( "search_path" , [] ) )

        
        # command line arguments passed down from Driver
        #self.argv = options[ 'argv' ]
        self.Request[ 'argv' ] = options['argv' ]


        # set the base project URL
        self.Response[ 'base_project_url' ] = self.project_profile[ 'base_url' ]


        # create the logger
        self.logger = LogWriter( self.__props.get( 'log_file_name' , 'Project' ), \
                                 log_details=self.__props.get( 'log_details', 0 ),\
                                 log_context=self.__props.get( 'log_context', 1 ),\
                                 date_delim =self.__props.get( 'log_date_delim',"-"),\
                                 print_log_lablels = self.__props.get( 'log_print_log_lablels', 1 ) )


        if self.__props.get( 'log_quiet', 0 ):
            self.logger.setCategoryExcludeList( [ SYSTEM_LOG_DEBUG ] )

        # create tables
        self.exception_table = ExceptionTable.ExceptionTable()
        self.plugin_table    = PluginTable.PluginTable() 


        # NOTE:no more dependency on WebForm
        #apply( WebForm.__init__, [ self, cgi.FieldStorage() ], LOCAL_PROPS )

        # NOTE: No more page_vars; we now use CGIResponse for everything
        # add alias for form_vars; users don't have to use two
        # different call mechs. for rendering the main page
        #self.page_vars = self.form_vars
        

        # ad base url for auto replacement of URL paths
        #self.add_var( "base_project_url", self.project_profile[ 'base_url' ] )


        # set values of over used paramters
        self.__name = self.project_profile[ 'project_name' ]
        
        self.__user_profile_dir = self.project_profile.get('user_profile_dir', '.') 
        self.__user_profile_cookie_name = self.project_profile.get( 'user_profile_cookie_name' , self.__name + '_tracker' )
        self.__session_access_path = self.project_profile.get( 'session_access_path' , '/')
        self.__session_access_domain = self.project_profile.get( 'session_access_domain', os.environ.get('SERVER_NAME','') )
        self.__session_expiration = self.project_profile.get( 'session_expiration', '' )

        self.__max_transitions = self.project_profile.get( 'max_transitions', 20 )

        # need to provide finctionality to turn off certain categories
        # from the profile block
        self.logger.writeEntry( "Project '%s' successfully initialized."%( self.__name), SYSTEM_LOG_DEBUG )
        self.logger.writeEntry( "\tproject profile:\n%s"%( format_dict(self.project_profile ) ), SYSTEM_LOG_DEBUG )


    #--------------------- Interface methods -----------------



    def init( self ):
        """ Constructor. Called by the Driver method after the
            project has been instantiated. This should be orverloaded
            and used in place of the __init__() method. """
        pass


    def render( self ):
        """ Must be overloaded. By default it returns a generaic
            page indicating that the default project page has been
            called. """
        
        return "DEFAULT RENDER PAGE: Please overload and customize."



    def preprocess( self ):
        """ Called just before dispatching a state (render/process).
            We don't do anything by default. """
        pass



    def postprocess( self ):
        """ Called after dispatching a state (render/process). 
            We don't do anything by default. """
        pass



    def load_plugins( self ):
        """ Can be overloaded to add aditional plugins to the system.
            Refer to documentation to see how this is done. We don't load 
            any plugins by default."""
        pass


    def load_exceptions( self ):
        """ All exception table initializations should
            go here. """
        pass
    


    def session( self, operation, user_profile=None ):
        """ Manages a session using the UserProfile object and cookies. You can 
            overload this to use any other user mgmt. strategy including URL based
            session ID's etc. """

        return self.__cookie_strategy( operation, user_profile )
        pass


    #------------------------------------------------------------
 

    #def add_var( self, var, value ):
    #    """ Overloaded WebForm method to log action
    #    for easy debugging. """
    #
    #    #self.logger.writeDebug( "Form var '%s' set to '%s'."%( var, value) )
    #    WebForm.add_var( self, var, value )


    #def add_vars( self, env ):
    #    """ Overloaded WebForm method to log actions
    #    for easy debugging. """
    #
    #    #self.logger.writeDebug( "Dictionary copied into form vars:\n%"%(format_dict(env) ) )
    #    WebForm.add_vars(sel, env )


    def setTemplate( self, template_file_name ):
        """ Sets the HTML file to use as the project.
            template. """

        self.set_encode_file_name( template_file_name )


    def run( self ):
        """ Main method called to dispatch stages and handle 
            stage exceptions. """

        # capture all data written to the standard output stream
        # so that it can be safely emitted
        #stdout_capture = StringIO.StringIO()
        stdout_capture = stdout_to_log( self.logger )
        self.stdout_save    = sys.stdout
        sys.stdout     = stdout_capture


        # load the session
        self.logger.writeEntry( "Loading session...", SYSTEM_LOG_DEBUG )
        self.user_profile = self.session( 'load' )

        # bind the user profile to Request
        self.Request.session = self.user_profile

        self.state_exception = ( None, None )
        self.trace_back = ""

        # load exception and plugin tables
        try:
            self.logger.writeEntry( "Loading exception and plugin tables...", SYSTEM_LOG_DEBUG  )
            self.load_exceptions()
            self.load_plugins()
        except:
            self.logger.writeEntry( "Error while loading plugins and/or exceptions.", SYSTEM_LOG_ERROR )
            self.logger.writeEntry( "Attempting to continue executing the request.\nDetails: %s"%( traceBack() ), SYSTEM_LOG_ERROR )
            self.trace_back = traceBack()
            


        #########################
        # begin execution of call

        #error_flag = 0

        if self.trace_back == "":
            try:
                self.logger.writeEntry( "Calling preprocess...", SYSTEM_LOG_DEBUG )
                self.preprocess()
            except:
                self.logger.writeEntry( "Error occured executing project's preprocess method.", SYSTEM_LOG_ERROR )
                self.logger.writeEntry( "No states will be loaded.\nDetails: %s"%( traceBack() ), SYSTEM_LOG_ERROR )
                self.trace_back = traceBack()
            

        # run loop paramters
        loop_control = 'run' 
        out = ''
        first_state_profile = self.parse_state_path( self.project_profile[ 'project_state_path' ] )
        call_path = first_state_profile[ 'call_path' ]
        load_path = self.project_profile[ 'project_state_path' ]
        last_call_path = ''
        state_profile = None
        load_msg = ''
        loop_count = -1 # must start at -1 because it is called at teh top of the loop


        while( loop_control=='run' and self.trace_back == "" ):

            loop_count = loop_count + 1

            # check loop count to make sure we are not in a cycle
            if loop_count > self.__max_transitions:
                self.logger.writeEntry( "Loop count exceeded maximum count.", SYSTEM_LOG_ERROR )
                self.logger.writeEntry( "You might thave a cycle in your code. Calling project's render().", SYSTEM_LOG_ERROR )
                out = self.render()
                break;


            # set params. for loading the state
            if last_call_path != call_path:
                self.logger.writeEntry( "Loading state: call_path '%s', last_call_path '%s'"%( call_path, last_call_path ),
                                        SYSTEM_LOG_DEBUG )

                state_profile = self.load_state_module( load_path )

            if state_profile == None:
                self.logger.writeEntry( "Could not load state; calling default project render().",
                                        SYSTEM_LOG_DEBUG )
                out = self.render()
                break;
            
            elif state_profile[ 'method' ][0] == "_":
                # attempted to load a protectedor private method
                # reject and call default render
                self.logger.writeEntry( "Attempted to call protected/private method %s; \
                default project render() called."%(state_profile[ 'method' ]),
                                        SYSTEM_LOG_WARNING )
                out = self.render()
                break;

            try:
                
                # change cwd to the state object directory
                change_cwd( state_profile['full_path'] ) 

                # capture the state profile prior to run
                # used later to detect state changes
                last_call_path = state_profile[ 'call_path' ]

                self.logger.writeEntry( "Setting last_call_path to %s."%( last_call_path ),
                                        SYSTEM_LOG_DEBUG )

                self.logger.writeEntry( "Calling method %s()..."%(state_profile[ 'method' ]),
                                        SYSTEM_LOG_DEBUG )

                # get a handle to the funtion (exceptions are raised if the function does not exist)
                func = getattr( state_profile[ 'state' ], state_profile[ 'method' ] )

                # call the function
                out = apply( func, [], {} )

                # cahnge cwd to back to project
                change_cwd( self.project_profile['webroot'] ) 

                # no exeptions raised; clear last exception
                self.state_exception = ( None, None )
                
            except StageProcessException, details:

                self.logger.writeEntry( "State %s raised StageProcessException."%( state_profile['state_name'] ),
                                        SYSTEM_LOG_DEBUG )
                out = details
                break;

            except:
                self.logger.writeEntry( "Exception caught while executing state method.\nDetails: %s"%( traceBack() ),SYSTEM_LOG_ERROR  )


                self.logger.writeEntry( "Attempting to look up exception handler...", SYSTEM_LOG_DEBUG )
                
                # attempt to locate a handler for the exception
                handler = self.exception_table.getHandler( sys.exc_info()[0] )

                # capture exception
                if self.state_exception[0] == sys.exc_info()[0]:
                    self.logger.writeEntry( "Exception '%s' called more than once consecutively."%( self.state_exception[0] ),
                                            SYSTEM_LOG_DEBUG )
                    out = self.render()
                    break;
                else:
                    self.state_exception = ( sys.exc_info()[0], sys.exc_info()[1] )
                    
                if handler != None:                    
                    # handle exception and rerun the state
                    self.logger.writeEntry( "Valid handler discovered.", SYSTEM_LOG_DEBUG )
                    out = handler.handleException( sys.exc_info()[0], sys.exc_info()[0], traceBack()  )

                    if out != '' and out != None:
                        # if the exception handler returned a value
                        # we simply print it
                        self.logger.writeEntry( "Value returned by exception handler.", SYSTEM_LOG_DEBUG )
                        break;
                    else:
                        self.logger.writeEntry( "Handler returned None/empty string.", SYSTEM_LOG_DEBUG)

                else:
                    self.logger.writeEntry( "No handler found; loading the default render method.", SYSTEM_LOG_DEBUG )
                    out = self.render()
                    if self.trace_back == "":
                        self.trace_back = traceBack()
                    break;
            else:

                self.logger.writeEntry( "Successfully finished calling %s()."%(state_profile['method']),
                                        SYSTEM_LOG_DEBUG )
                
                if out != '' and out != None:
                    # the method invoked returned something to be rendered
                    self.logger.writeEntry( "Method returned output; stopping process loop and rendering results.",
                                            SYSTEM_LOG_DEBUG )
                    break
                else:
                    # nothing to be rendered
                    if state_profile[ 'method' ] == 'render' and\
                       not state_profile['state'].anotherStateScheduled():
                        self.logger.writeEntry( "No output detected from render(); calling process().", SYSTEM_LOG_DEBUG )
                        state_profile[ 'method' ] = 'process'
                    else:
                        # process or custom method was called with no output return
                        
                        # check if a state transition has been scheduled 
                        if state_profile['state'].anotherStateScheduled():
                            call_path = self.parse_state_path( state_profile['state'].getNextCallPath() ).get( 'call_path', '')
                            load_path = state_profile['state'].getNextCallPath()
                            
                            self.logger.writeEntry( "State %s scheduled; restarting call loop."%(state_profile['state'].getNextCallPath() ),
                                                    SYSTEM_LOG_DEBUG ) 
                            
                            # restart the loop to process new state
                            continue;
                        else:
                            self.logger.writeEntry( "Nothing else to do; retruning default render page.",
                                                    SYSTEM_LOG_DEBUG )
                            
                            out = self.render()
                            break;


        # change cwd back to project
        change_cwd( self.project_profile['webroot'] ) 

        #if error_flag == 0:
        if self.trace_back == "":
            # call postprocess
            try:
                # reset the context
                self.logger.resetContext()
                
                self.logger.writeEntry( "Calling postprocess...", SYSTEM_LOG_DEBUG )
                self.postprocess()
            except:
                self.logger.writeEntry( "Error occured while executing project's postprocess method. Renderig default page.\
                \nDetails: %s"%( traceBack() ),
                                        SYSTEM_LOG_ERROR )
                self.trace_back = traceBack()
                out = self.render()
        else:
            # override the output if an error occured
            self.logger.writeEntry( "One or more errors occured earlier; skipping postprocess() and calling defult render().",
                                    SYSTEM_LOG_DEBUG )
            out = self.render()


        # cleanup after the session
        self.logger.writeEntry( "Saving session...", SYSTEM_LOG_DEBUG )
        self.session( 'save', self.user_profile )
        self.user_profile = None

        # process the output
        self.Response.add_var( 'state_output', out )

        #self.logger.writeEntry( "Rendering page:\n %s"%( out ), SYSTEM_LOG_DEBUG )

        sys.stdout = self.stdout_save
        #self.logger.writeDebug( "stdout = '%s'"%(stdout_capture.getvalue() ) )

        self.logger.writeEntry( "Project finished running.", SYSTEM_LOG_DEBUG )

        # capture the log cache for rendering
        self.Response[ 'log_cache' ] = self.logger.getMessageCache()

        if self.project_profile.get( "mode", "production" ) == "debug" and\
           self.trace_back != "":

            self.logger.writeEntry( "In DEBUG mode and an error has occured.", SYSTEM_LOG_DEBUG )
            
            final_doc = self.__debug( "Project exception caught.",
                                      "An exception was caught during project processing.",
                                      self.trace_back,
                                      self.Response[ "log_cache" ]
                                      )
        
        else:

            final_doc = self.Response.encode_final_document()

        #self.logger.writeENtry( "final_doc = %s"%( final_doc[:200] ), SYSTEM_LOG_DEBUG )
        return final_doc




    def load_state_module( self, load_path ):

        state_profile = self.parse_state_path( load_path )
        
        # bind UserProfile to state
        state_profile[ 'user_profile' ] = self.user_profile

        
        # NOTE: We may want to put this in a func. at some point
        # load basic properties for state
        state_profile[ 'webroot' ] = self.project_profile['webroot']
        state_profile[ 'project_profile' ] = self.project_profile
        state_profile[ 'Request' ] = self.Request
        state_profile[ 'Response' ] = self.Response
        state_profile[ "project" ] = self

        
        
        # attempt to instantiate the specified state
        ( state_profile, load_msg ) = self.__load_state( state_profile )


        if state_profile == None:
            self.logger.writeEntry( "Could not load state module.\nDetails: %s"%(load_msg),
                                    SYSTEM_LOG_ERROR )

            # set the trace back
            self.trace_back = load_msg
            return None
        else:
            self.logger.writeEntry( "Successfully loaded %s."%(state_profile["state_name"]),
                                    SYSTEM_LOG_DEBUG  )
            
            # set the UserProfile dir to the state directory
            if state_profile[ 'user_profile' ] != None:                
                # UserProfile's create method will not do anything
                # if the directory structure exists.
                state_profile[ 'user_profile' ].create( state_profile[ 'call_path' ] )
                state_profile[ 'user_profile' ].cd( state_profile[ 'call_path' ] )
                
                self.logger.writeEntry( "Changed UserProfile namespace scope to '%s'."%(state_profile[ 'call_path' ]),
                                        SYSTEM_LOG_DEBUG )
                
            else:
                self.logger.writeEntry( "UserProfile not valid.", SYSTEM_LOG_WARNING )

                 
        # bind plugins to instance
        plugin_name_list = self.plugin_table.getPluginNames()
        for name in plugin_name_list:
            if self.plugin_table.getPlugin(name) == None:
                self.logger.writeEntry( "Plugin %s is set to None."%(name), SYSTEM_LOG_WARNING )

            setattr( state_profile['state'], name, self.plugin_table.getPlugin(name) )



        # invoke the methods init method
        self.logger.writeEntry( "Calling state's init() method...", SYSTEM_LOG_DEBUG )
        state_profile['state'].init()

        return state_profile


   #---------------------- Internal methods ---------------------

    def __cookie_strategy( self, operation, user_profile=None ):
        """ Internal method that implements session management with cookies.
            It will use an ID stored in as a cookie to locate a UserProfile
            object. Oherwise, it will create a new UserProfile object and 
            store the assigned unique ID as a cookie. """

        # check directory
        (chdir_result, chdir_msg) = change_cwd( self.__user_profile_dir, check_only=1 )
        if not chdir_result:
            self.logger.writeEntry( "User profile directory '%s' is not \
            valid or accessible.\n%s"%( self.__user_profile_dir, chdir_msg ), SYSTEM_LOG_ERROR )

            return UserProfile()

        self.logger.writeEntry("__cookie_strategy: cwd = %s"%( os.getcwd() ), SYSTEM_LOG_DEBUG )

        cookie = self.Request.get_cookie( self.__user_profile_cookie_name )

        if operation == 'load' and cookie != None:

            self.logger.writeEntry( "__cookie_strategy: cookie : %s"%( cookie ), SYSTEM_LOG_DEBUG )
            self.logger.writeEntry( "__cookie_strategy: cookie value : %s"%( cookie.value ), SYSTEM_LOG_DEBUG )

            up_file_name = os.path.join( self.__user_profile_dir, cookie.value )

            try:                
                user_profile_file  = open( up_file_name, 'r' )

                user_profile = cPickle.load( user_profile_file )
                
                user_profile_file.close()

                self.logger.writeEntry( "__cookie_strategy: Successfully loaded user profile for session %s."%(cookie.value), SYSTEM_LOG_DEBUG )

                return user_profile
            
            except:
                self.logger.writeEntry( "__cookie_strategy: Exceptions raised while loading user profile file '%s'. Details: %s"%(up_file_name,
                                                                                                               traceBack() ),
                                        SYSTEM_LOG_WARNING )
                self.logger.writeEntry( "__cookie_strategy: Creating and returning a fresh UserProfile." )
                return UserProfile()

        elif operation == 'load' and cookie == None:

            self.logger.writeEntry( "__cookie_strategy: First time that user has accessd project. Creating new UserProfile.",
                                    SYSTEM_LOG_DEBUG )
            return UserProfile()
        

        elif operation == 'save' and isinstance( user_profile, UserProfile ) == 1:

            up_file_name =  os.path.join( self.__user_profile_dir, 'UserProfile.'+ user_profile.getId() )

            try:
                
                #save the file
                user_profile_file = open( up_file_name, 'w' )

                cPickle.dump( user_profile , user_profile_file )
                
                user_profile_file.close()

                #cookie = self.get_new_cookie()
                #cookie[ self.__user_profile_cookie_name ] = 'UserProfile.'+ user_profile.getId()
                #cookie[ self.__user_profile_cookie_name ]['path']    = self.__session_access_path
                #cookie[ self.__user_profile_cookie_name ]['domain']  = self.__session_access_domain
                #cookie[ self.__user_profile_cookie_name ]['expires'] = self.__session_expiration

                self.Response.set_cookie( self.__user_profile_cookie_name,
                                          'UserProfile.'+ user_profile.getId(),
                                          self.__session_access_domain,
                                          self.__session_access_path,
                                          self.__session_expiration )


                self.logger.writeEntry( "__cookie_strategy: User profile cookie set with name: UserProfile.%s"%( user_profile.getId() ),
                                        SYSTEM_LOG_DEBUG )
            except:
                self.logger.writeEntry( "__vookie_strategy: Error occured while saving user profile file '%s'.\nDetails: %s"%( up_file_name,
                                                                                                                               traceBack() ),
                                        SYSTEM_LOG_DEBUG )

        else:
            self.logger.writeEntry( "__cookie_strategy: Did not know how to handle operation '%s'. Nothing done."%( operation ),
                                    SYSTEM_LOG_WARNING )
            self.logger.writeEntry( "__cookie_strategy: user_profile = %s"%( user_profile ), SYSTEM_LOG_DEBUG )
            pass
        



    def __load_state( self, state_profile ):
        """ Loads a state and returns a reference to the
            state object. """

        # initialize the state to None
        state_profile[ 'state' ] = None
        error_msg = ''

        try:

            # check state properties
            if state_profile[ 'path' ] == '' or \
               state_profile[ 'state_name' ] == '':
                raise LoadException( "Invalid state path %s or state module/class name '%s'."%( state_profile['path'],
                                                                                                state_profile['state_name'] )
                                     )

            # change to state directory
            ( chdir_result, chdir_msg) = change_cwd( state_profile[ 'full_path' ] )
            if not chdir_result:
                raise LoadException( "Full state path %s does not appear to be a valid or accessible directory. %s"%( state_profile['full_path'], chdir_msg ) )


            # add the state path to the execution path
            Path.path.addDir( state_profile['full_path'] )
            
            # import the state
            state_module = __import__( state_profile[ 'state_name' ] )

            # load the state
            instance_code = "state = state_module.%s()"%( state_profile['state_name'] )

            self.logger.writeEntry( "__load_state: Executing state instance code: %s"%( instance_code ), SYSTEM_LOG_DEBUG )

            exec instance_code 

            self.logger.writeEntry( "__load_state: State %s.%s successfully instantiated."%( state_profile['state_name'],
                                                                                             state_profile['state_name'] ),
                                    SYSTEM_LOG_DEBUG )

            # make sure that the class is a State instance
            if not isinstance( state, State ):
                raise LoadException( "Class %s.%s is not an instance of the State class."%( state_profile['state_name'] ,
                                                                                            state_profile['state_name'] ) )
            # change back to project directory
            change_cwd( self.project_profile[ 'webroot' ] )
                

            # init the project if necessary
            # (Note: this is a place holder for future expansion.)
            apply( state.init_state, (), state_profile )


            state_profile[ 'state' ] = state

            return ( state_profile, "Successfully loaded state %s.%s."%( state_profile['state_name'],
                                                                         state_profile['state_name'] )
                     )

        except LoadException, details:
            error_msg = "Invalid state properties.\nDetails: %s"%( details )
             
        except ImportError, details:
            error_msg = "Could not import state %s.%s. Details: %s"%( state_profile['state_name'],
                                                                      state_profile['state_name'],
                                                                      details ) 

        except AttributeError, details:
            error_msg = "Could not instantiate state class '%s'. Make the sure class \
            exists in module '%s'.\nDetails: Attribute Error: %s"%( state_profile['state_name'],
                                                                    state_profile['state_name'],
                                                                    details ) 
        except SyntaxError, details:
            error_msg = "SyntaxError: %s"%( details ) 

        except:
            error_msg = "Unexpected error occured loading state %s.%s.\n \
            Traceback: %s"%( state_profile['state_name'],
                             state_profile['state_name'],
                             traceBack() )


        # post exception processing
        self.logger.writeError( "__load_state: " + error_msg, SYSTEM_LOG_ERROR )

        # change back to project directory
        change_cwd( self.project_profile[ 'webroot' ] )

        return ( None, error_msg )




    def parse_state_path( self, state_path ):
        """ Internal method for extracting the state path, state dir.
            and call method from a string. """

        # /
        # /state.method
        # /dir/state.method

        self.logger.writeEntry( "parse_state_path: Parsing call path: %s"%( state_path ),
                                SYSTEM_LOG_DEBUG )

        # we use the os.path method to help us with this.

        state_profile = {}
        state_profile[ 'path' ] = os.path.split( state_path )[0]
        state_profile[ 'state_name' ] = os.path.split( state_path )[1]

        # extract method
        if string.find( state_profile[ 'state_name' ], '.' ) == -1:
            state_profile[ 'state_name' ] = state_profile[ 'state_name' ] + '.'  

        ( state_name, method ) = string.split( state_profile[ 'state_name' ], '.' )

        if state_name != '':
            if not method:
                self.logger.writeEntry( "parse_state_path: No method defined for state %s; defaulting to project's render()."%( state_name ),
                                        SYSTEM_LOG_DEBUG ) 
                method = 'render'
                
            self.logger.writeEntry( "parse_state_path: User has slected to invoke %s.%s()."%( state_name,
                                                                                              method ),
                                    SYSTEM_LOG_DEBUG )
 
        state_profile[ 'state_name' ] = state_name
        state_profile[ 'method' ] = method
        state_profile[ 'full_path' ] = os.path.join( self.project_profile['webroot'], state_profile['path'][1:] )
        state_profile[ 'call_path' ] = os.path.join( state_profile[ 'path' ] , state_name )

        self.logger.writeEntry( "parse_state_path: Resulting state_profile:\n%s"%( format_dict(state_profile ) ),
                                SYSTEM_LOG_DEBUG )

        return state_profile


    def __debug( self, subject, message, tb="", log_cache="" ):
        """ Convenience method for returning a pretty debug
        page with exception information. """


        error_string = """Content-type: text/html


        <html>
        <body bgcolor="white">
        
        
        <table align="center" width="80%%" >

        <tr>
           <td valign="top" ><i>Error</i></td>
           <td>%s</td>
        </tr>
        <tr>
           <td valign="top"><i>Explanation</i></td>
           <td>%s</td>
        </tr>
        <tr bgcolor="#C0C0C0" >
           <td valign="top" ><i>Traceback</i></td>
           <td><pre>%s</pre></td>
        </tr>
        </table>

        <pre>
        %s
        </pre>

        </body>
        </html>
        """


        return error_string%( subject, message, tb, log_cache )



    def __change_namespace( self, dir='' ):
        """ Updates the directory class sot hat it points to the 
            appropriate name space. When dispatching, the namespace is 
            set to that of the relative dir. path to the state. """

        pass

