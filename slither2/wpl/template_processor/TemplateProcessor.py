"""
        wpl.wf is a library file used to wrap the cgi module with
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



import os.path
import string
import UserDict


from wpl.wp import WriteProcessor, SimpleWriter
from wpl.wp.Emitter import Emitter, createEmitter
from wpl.wp.Emitter import StringEmitter



class TemplateProcessor( UserDict.UserDict ):


    def __init__( self ):
        self.search_path = ["."]
        self.default_vars = {}
        self.encode_target = None
        self.encode_count = 0
        self.last_encoding = ""
        pass

    def check_default_vars(self, current_value, default_value):
        if current_value == None or type(current_value) != {}:
           return default_value
        return current_value

    def check_search_path(self, current_value, default_value):
        if current_value != None or type(current_value) != type([]):
           return default_value
        return current_value

    def check_emit_strategy(self, current_value, default_value):
        #print current_value.__class__
        #print default_value.__class__
        if isinstance(current_value, Emitter):
           return current_value
        return default_value


    def check_encode_target( self, current_value, default_value ):
        # NOTE: Not sure what to check for here as this is allowed
        #       to be None until later defined. For now we simply return
        #       the current_value.
        return current_value


    #def set_emit_strategy( self, strategy ):
    #    """ Update the emit strategy to a new strategy. """
    # 
    #    #print "STRAT: %s"%( isinstance( strategy, StringEmitter ) )
    #    setattr( self, 'emit_strategy', self.check_emit_strategy( strategy, self.emit_strategy  ) )

    def set_search_path(self, search_path):

        if type( search_path ) == type( [] ) or\
           type( search_path ) == type( () ):

            for item in search_path:
                if item not in self.search_path:
                    self.search_path.append( item )
        else:
            pass


    def reset_search_path( self ):
        """ Clears the search path to include only '.'. """
        self.search_path = ['.']


    def add_vars(self, env):
        """
        Add a dictionary of variables to self.default_vars.
        """
        for var in env.keys():
            self.default_vars[var] = env[var]


    def add_var(self, name, value):
        """
        Add a single binding between 'name' and 'value' to self.form_vars.
        """        
        self.default_vars[name] = value



    def set_encode_file_name(self, file_name):
        """
        Set the filename to be encoded via the encode() method. This filename
        should correspond to a text file, possibly containing WriteProcessor
        variables.
        """
        if not file_name:
            raise Exception( "Parameter file_name must have the full path to the template file." )

        p = os.path.split( file_name )

        if p[0] not in self.search_path and\
           p[0] != "":
            self.search_path.append( p[0] )

        self.encode_target = p[1]


    def get_encode_count( self ):
        """ Accessor method used to track the number of times
        that the encode method was called. """

        return self.encode_count


    def get_last_encoding( self ):
        """ Convenience method for effeciently retreiveing the
        results of the last encoding. """

        return self.last_encoding


    def encode(self, alt_template_file = "", prepend_text=''):
        """
        Process the template.. 
        """

        # always use the string emitter
        emitter = StringEmitter()

        last_file_name = self.encode_target
        if alt_template_file != "":
            self.set_encode_file_name( alt_template_file )


        emitter.emit(prepend_text)

        # Now, call the WriteProcessor. In order for this to work, a valid
        # 'encode_target' must have been passed to WebForm (or via the
        # set_encode_target() method call.
        if self.encode_target:
            wpc = WriteProcessor.WriteProcessor
            wp = wpc(self.encode_target, self.search_path, self.default_vars, emitter)
            wp.process()


        # if we set an alternate file, switch back
        if alt_template_file != "":
            self.encode_target = last_file_name


        # up the counter and cache the results
        self.encode_count = self.encode_count + 1
        self.last_encoding = emitter.getResult()

        # Finally, return the result.
        return self.last_encoding


    def __getitem__( self, var ):
        """ Overrides the use of [] operators
        for accessing data values. """
        
        return self.default_vars[ var ]
        pass


    def __setitem__( self, var, value ):
        """ Overloads the use of [] operators for
        setting data values. """

        # always set values in the user name space
        self.default_vars[ var ] = value
        pass


    def __delitem__( self, var ):
        """ Overloads the use of [] operatord for
        removing data values. """

        # only remove values from the user namespace
        if self.default_vars.has_key( var ):
            del self.default_vars[ var ]


    def has_key( self, var ):
        """ Overrides the standard dictionary key
        lookup. """

        return self.default_vars.has_key( var )
    

    def get( self, var, alt=None ):
        """ Overrides the standard dictionary
        safe value retrieval. """

        return self.default_vars.get( var, alt )

    def keys( self ):
        """ Retrievs the keys stored in the data dict. """

        return self.default_vars.keys()
