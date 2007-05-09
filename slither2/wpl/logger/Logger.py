"""
        wpl.logger is a library file used to generate log files from a Python application.
        This file part of the wpl.logger.Logger library.
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



# Standard Imports
import string
import time
import os
import sys
import os.path

#sys.stderr.write( "path = %s"%( sys.path ) )

if os.name == 'posix':
  import fcntl
  # GKT
  FCNTL = fcntl


# Non-Standard Imports
from LogStrategy import LogStrategy
from wpl.trace.Trace import traceBack
from wpl.trace.Trace import stackTrace 
from wpl.trace.Trace import getLineNumber 
from wpl.trace.Trace import getSourceFileName

# imported for testing only
import StderrStrategy


# global constants
MULTI_LINE_INDENT = "     "
TODAY_S_LINK = 'today.log'


# category constants
WARNING = 'WARNING'
ERROR   = 'ERROR'
DEBUG   = 'DEBUG'
ENTRY   = 'ENTRY'
ALL     = 'ALL'




class LogWriter:


    def __init__(self, base_log_file_name, ** options ):

        # check for valid base name
        if base_log_file_name[-1] not in ( string.letters + string.digits ):
           raise Exception( "Base log file name '%s' is invalid."%( base_log_file_name ) ) 
       
        # separate base name to path and file name
        self.__path = os.path.dirname( base_log_file_name )
        self.__base_name = os.path.basename( base_log_file_name )
        self.__log_file_name = ''
        self.__log_file = None

        # custimization options
        self.__log_details = 0 
        self.__log_context = 1
        self.__print_log_labels = 1
        self.__date_delim  = '-'

        # handle options
        self.setOptions( init_opts = options )

        # generate file name
        self.__generate_file_name() 

        # attempt to load the file
        self.__load_log()

        # if we failed to load the file, 
        # we need to raise an exception
        if self.__log_file == None:
            raise Exception( "ERROR: Could not create log file '%s' at instantiation."%(self.__log_file_name) )

        # initialize message cache
        self.__msg_cache = []

        # instantiate the default logger
        self.__strategy_dict = {} 

        # valdiate additional strategies
        if options.has_key( 'strat_dict' ) and type( options[ 'strat_dict' ] ) == type({}):
            for strat in options[ 'strat_dict' ].keys():
                if isinstance( options[ 'strat_dict' ][ strat ], LogStrategy ): 
                    self.__strategy_dict[ strat ] = options[ 'strat_dict' ][ strat ] 
                else:
                    pass


        # setup logging categories
        self.__category_exclude_list = []
        self.__category_list = [ ALL ]
        if options.has_key( 'cat_list' ):
           self.__category_list = option[ 'cat_list' ] 

       
        # set the context
        self.__base_context = str(time.time())
        self.__context = self.__base_context
        pass


    def setCategoryList( self, cat_list ):
        self.__category_list = cat_list


    def setCategoryExcludeList( self, cat_list ):
        self.__category_exclude_list = cat_list
      

    def resetCategoryExcludeList( self ):
        self.__category_exclude_list = []


    def resetCategoryList( self ):
        self.__category_list = [ ALL ]
        

    
    def setOptions( self, ** options ):
        """ Method used to set various custimization 
            options supported by the logger. """


        if options.has_key( 'init_opts' ):
            for key in options[ 'init_opts' ].keys():
                options[ key ] = options[ 'init_opts' ][ key ]

        self.__log_details = options.get( 'log_details', self.__log_details )
        self.__log_context = options.get( 'log_context', self.__log_context )

        self.__print_log_labels = options.get( 'print_log_lablels', self.__print_log_labels )
        self.__date_delim       = options.get( 'date_delim', self.__date_delim )

        #print "log_details = %s"%( self.__log_details )
        #print "log_context = %s"%( self.__log_context )



    def extendContext( self, extension ):
        """ Let's users add more values to the end of the 
            contect field. """

        # periods are reserved symbols in the context block; 
        # we replace user periods with under score chars
        extension = string.replace( extension, '.', '_' )
        self.__context = string.join( [self.__base_context, extension], '.' ) 


    def resetContext( self ):
        """Resets the contect variable to the initial
        dynamic value assigned."""
        self.__context = self.__base_context


    def getMessageCache( self ):
        return string.join( self.__msg_cache, '' )


    def writeError(self, message, strat_list=[] ):
        self.__write( self.__context, ERROR, message, strat_list )
        pass


    def writeWarning(self, message, strat_list=[]):
        self.__write( self.__context, WARNING, message, strat_list )
        pass


    def writeDebug( self, message, strat_list=[] ):
        self.__write( self.__context, DEBUG, message, strat_list )
        pass


    def writeEntry( self, message, category='no category', strat_list=[] ):
        # NOTE: I WILL NEED TO HANDLE CONTEXT MECH. HERE
        self.__write( self.__context, category, message, strat_list )




    def __write( self, context, category, message, strat_list=[] ):
        """ Base method for writing a log entry to 
            all log strategies. """


        # log only specified categories
        if ( category not in self.__category_list and\
             ALL not in self.__category_list ) or\
             category in self.__category_exclude_list:
           return

        # load the file
        self.__load_log()        

        # if we could not load the file, exit silently
        if self.__log_file == None:
           sys.stderr.write( "\nERROR: Null log file descriptor; no log entry written." )
           return


        # log details if user desires
        if self.__log_details == 1:
            message = string.strip( message )

            details = "(logged in %s on line %s)"%( getSourceFileName(2), getLineNumber(2) )

            tb = ""
            if traceBack() != "(no exceptions)":
                tb = "(traceback)\n%s"%( traceBack() )            

            message = "%s\n%s\n%s"%( details, message, tb )



        try:
           # first log to the log file
           self.__file_lock( 'lock' )
           self.__write_to_file( context, category, message )
           self.__file_lock( 'un-lock' )

           # write all available strategies
           # NOTE: it is expected that additional strategies are
           #       are thread safe.
           for strat in self.__strategy_dict.keys():
               if strat in strat_list or 'all' in strat_list:
                   self.__strategy_dict[ strat ].write_entry( context=context, category=category, message=message )
               else:
                   # don't do anything
                   pass


        except:
           sys.stderr.write( "\nERROR: Could not write to one or more strategies.\n" )
           sys.stderr.write( "\nMESSAGE:\n%s\n"%( message ) )
           sys.stderr.write( "\nTRACE BACK:\n%s\n"%( traceBack() ) )
           self.__file_lock( 'un-lock' )

        pass




    def __file_lock( self, operation ):

        if os.name == 'posix' and self.__log_file != None:
           try:
              if operation == 'lock':
                 op = FCNTL.LOCK_EX
              else:
                 op = FCNTL.LOCK_UN

              fcntl.flock( self.__log_file.fileno(), op )
           except IOError, details:
              sys.stderr.write( "\nERROR: Could not obtain/release lock." )
              sys.stderr.write( "\nDETAILS:\n%s"%( details ) )




    def __load_log( self ):
        """ Loads a specified log file, roteates logs,
            and sets the today link to the currently 
            loaded log. """

        # load the log file if the log file name is none
        # or if the file name has changed
        if self.__log_file == None or self.__generate_file_name() == 1:
            try:
                self.__log_file = open( self.__log_file_name, 'a' )

                link_name =  string.join( [self.__base_name , TODAY_S_LINK], '.' )

                # if link exists remove it
                if os.path.islink( os.path.join( self.__path, link_name ) ):
                    # DEBUG
                    #print "removing link."
                    os.unlink( os.path.join( self.__path, link_name ) )

                # set a softlink 'today' to point to the current log
                os.symlink( self.__log_file_name , os.path.join( self.__path, link_name ) )
            except:
                sys.stderr.write( "\nERROR: LogWriter could not create log file name '%s'."%( self.__log_file_name ) )
                sys.stderr.write( "\nTRACE BACK:\n%s."%( traceBack() ) )
                self.__log_file = None
        else:
            pass


    def __generate_file_name( self ):
        """ Generates a log file name based on the
            a specified base name ans the current locale time. """

        previous_name = self.__log_file_name

        # generate log file name
        base_log_file_name = os.path.join( self.__path , self.__base_name )

        date_format_string = "%%m%s%%d%s%%Y"%( self.__date_delim, self.__date_delim )
        
        date_ext = time.strftime( date_format_string , time.localtime( time.time() ) )
        term_ext = "log"
        self.__log_file_name = string.join( [base_log_file_name,date_ext, term_ext], '.' )

        # return boolean to describe a change
        # in the name of the file
        if previous_name != self.__log_file_name:
           return 1
        else:
           return 0


    def __write_to_file( self, context, category, message ):
        """ Internal method for writing to the log file.
            We always, regardless of preferences, will log to a log
            file; that's why this is included here as opposed to
            being handled as a strategy. """

        # remove unwanted white space before and at the end of the message
        message = string.strip( message )

        # check for multi-lined entry
        if string.find( message, '\n' ) != -1:

            lines = string.split( message, '\n' )
 
            #DEBUG
            #print ">>>>> lines : %s"%( lines )

            i = 0
            while i < len(lines):
                lines[i] = string.join( [ MULTI_LINE_INDENT, lines[i] ], '' )
                i = i + 1

            # reconstruct the message
            message = string.join( lines , '\n' )

            message = '\n' + message


        # log context
        if self.__log_context != 1:
            context = ""

        if self.__print_log_labels == 1:
          context = "context:" + context
          category = "category:" + category


        # time stamp
        time_stamp = time.asctime( time.localtime( time.time() ) ) 
        entry = "[%s] [%s] [%s] > %s\n"%( time_stamp, \
                                          context,    \
                                          category,   \
                                          message )

        # cache the message
        self.__msg_cache.append( entry )

        self.__log_file.write( entry )
        self.__log_file.flush()



def test_func( wpll ):
   try:
       print "\traising an exception and lgging it in except block."
       raise Exception( "Error! Raised a test exception." )
   except Exception:
       wpll.writeDebug( "An exception just occured." )


if __name__ == '__main__':


   print "\n******* Testing Logger ***********\n"

   print "Instantiating a logger..."

   stderr_strat = StderrStrategy.StderrStrategy()
   wpll = LogWriter( "TestLog", log_details = 0, log_context = 1, strat_dict={ 'stderr' : stderr_strat } )

 
   print "Writing a log with: "
   print "\tno category or extra strat list entry..."
   wpll.writeEntry( "Simple log message with no category or extra strat. list." )

   print "\t'MyCategory' category and no extra strat. list..."
   wpll.writeEntry( "Simple log message with 'MyCategory' and no extra strat. list.", 'MyCategory' )

   print "\t'MyCategory' category and stderr in extra strat. list..."
   wpll.writeEntry( "Simple log message with 'MyCategory' and stderr in extra strat. list...", 'MyCategory' )
  
   
   print "\nTurning off context and turning on details."
   wpll.setOptions( log_details = 1, log_context = 0 )
 
   print "\nWriting entries with additional convenience methods:"
   print "\twriting a DEBUG message..."
   wpll.writeDebug( "A DEBUGGING message." )

   print "\twriting a WARNING message..."
   wpll.writeWarning( "A WARNING message." )

   print "\twriting an ERROR message..."
   wpll.writeError( "An ERROR message." )


   print "\nWriting another multi-line message..."
   wpll.writeEntry( """This is a multi-line entry.\nLine two.""" )

   print "\nWriting another multi-line message..."
   wpll.writeEntry( """This is another multi-line entry.\n
   Line 2\n\n
   Last line.""" )


   print "\nPrinting message cache..."
   print '\n',wpll.getMessageCache()


   print "\nTesting category selection mechanism..."
   print "\tselecting no categories."
   wpll.setCategoryList( [] ) 
   print "\tprinting three entries with different categories; these should NOT end up in the logs."
   wpll.writeEntry( "SHOULD NOT BE IN LOG.", 'MyCategory' )
   wpll.writeDebug( "SHOULD NOT BE IN LOG." )
   wpll.writeError( "SHOULD NOT BE IN LOG." )

   print "\n\tselecting DEBUG and ERROR category."
   wpll.setCategoryList( [ DEBUG, ERROR ] )
   print "\tprinting three messages; the DEBUG and ERROR messages should only log."
   wpll.writeEntry( "SHOULD NOT BE IN LOG.", 'MyCategory' )
   wpll.writeDebug( "Should be logged." )
   wpll.writeError( "Should be logged." )

   print "\n\tselecting ALL categories using reset method."
   wpll.resetCategoryList()
   print "\tprinting three messages; they should all be logged."
   wpll.writeEntry( "Should be logged 1 of 3.", "MyCategory" )
   wpll.writeDebug( "Should be logged 2 of 3." )
   wpll.writeError( "Should be logged 3 of 3." )

   # turn context logging back on
   wpll.setOptions( log_context = 1 )

   print "\nCalling test function that handels exception."
   test_func( wpll )

   print "\nLogging to stderr srtategy."
   wpll.writeEntry( "Logging to stderr strategy.", strat_list=[ 'stderr' ] )


   print "\nTesting context extension."
   wpll.extendContext( "myPersisObject.123245" )
   wpll.writeEntry( "Log with new context." )


   print "\n******* End of test **********\n"
