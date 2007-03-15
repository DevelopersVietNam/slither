"""

        Number Game is an example Slither based application.
        This file part of the Number Game.
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

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
        IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
        FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE
        LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
        BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
        BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
        LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
        SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""

# slither imports
from Project import Project
from ExceptionTable import ExceptionHandler 

# WPL resources
from wpl.logger.Logger import LogWriter
from wpl.trace.Trace import traceBack
from wpl.wp.Emitter import StringEmitter
from wpl.wp.WriteProcessor import WriteProcessor


class NumberGame( Project ):

    def __init__( self ):
        pass

    def render( self ):
        emitter = StringEmitter()
        writer = WriteProcessor( "NumberGameStart.html",
                                 self.project_profile.get( 'search_path', ['.']),
                                 self.Response,
                                 emitter )
        writer.process()
        return emitter.getResult() 

    def preprocess( self ):
        pass

    def postprocess( self ):
        #self.Response.set_template_processor( "zpt" )
        #self.Response.set_encode_file_name( "BasicTemplate.zpt" )
        pass

    def load_plugins( self ):
        """ Overid ofr Project method used to laod
        plugin object that will be made available to
        all states. """

        # create and add logger plugin
        logger = LogWriter( './Files/logs/StateLog', log_details = 0 )
        self.plugin_table.addPlugin( 'logger', logger )
        

    def load_exceptions( self ):
        pass
