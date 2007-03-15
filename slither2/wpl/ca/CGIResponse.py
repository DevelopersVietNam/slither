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


import os
import os.path
import string 
import UserDict


from wpl.template_processor import TemplateProcessor
from wpl.wp import WriteProcessor, SimpleWriter
from wpl.wp.Emitter import Emitter, createEmitter
from wpl.wp.Emitter import StringEmitter
import SimpleCookie



errorText = """
<html>
  <head>
    <title>CGIResponse Processing Error</title>
  </head>

  <body>
    <h1>CGIResponse Error in Processing</h1>
     <p>An error has been encountered in processing a form.</p>
     <p>Details: <<Error>></p>
  </body>
</html>
"""



# constant names of well known template processors
ZPT = "zpt"
WRITE_PROCESSOR = "write processor"



class CGIResponse( UserDict.UserDict ):

    
    def __init__(self, **props):
        """
        Instead of having so many parameters to the constructor,
        keyword parameters are now used, which is equivalent to a property
        based system.

           content_type - None | 'text/html' | 'text/plain' | 'other valid enc'
              If content_type is set to None, no content header is emitted.

           write_cookies = 'yes' | 'no' | None
              This determines whether cookies should be emitted. By default,
	      'yes'.

           template_processor = TemplateProcessor or a sub class
              This is the underlying frameowrk for handling all
              template processing.

        """

        default_props = {
           'content_type' : 'Content-Type: text/html',
           'write_cookies' : 'yes',
           'template_processor' : TemplateProcessor.TemplateProcessor()
        }
  

        for prop_name in default_props.keys():
            check_method_name = 'check_%s' % prop_name
            if hasattr(self, check_method_name):
               check_method = getattr(self, check_method_name)
               new_value = check_method(props.get(prop_name, None), default_props[prop_name])
               setattr(self, prop_name, new_value)
               #print "prop name = %s"%( prop_name )

        #print "self.write_cookies: ", self.write_cookies
        #print "self.content_type: ", self.content_type


        self.cookies = SimpleCookie.SimpleCookie()
        self.response_header_dict = {}



    def check_content_type(self, current_value, default_value):
        if current_value == None:
           return default_value
        return current_value


    def check_write_cookies(self, current_value, default_value):
        if current_value == None or current_value not in ['yes','no' ]:
           return default_value
        else:
           return current_value


    def check_template_processor(self, current_value, default_value):
        if current_value == None or not isinstance( current_value, TemplateProcessor.TemplateProcessor ):
            return default_value
        else:
            return current_value


    def set_cookie(self, name, value, domain="", path="", expires="" ):
        """ Creates a new cookie based on the vars
        that are passd in. """


        if not name:
            raise Exception( "Cookie must have a valid string name." )
        
        self.cookies[ name ] = value

        if domain:
            self.cookies[ name ][ "domain" ] = domain

        if path:
            self.cookies[ name ][ "path" ] = path

        if expires:
            self.cookies[ name ][ "expires" ] = expires

        return self.cookies[ name ]


    def get_cookie( self, name ):
        """ Retreives a preset cookie. """
        
        if self.cookies.has_key( name ):
            return self.cookies[ name ]
        else:
            return None
        

    def remove_cookie( self, name ):
        """ Removes a preset cookie."""

        if self.cookies.has_key( name ):
            del self.cookies[ name ]

    def remove_all_cookies( self ):
        """Clears all preset cookies. """
        self.cookies.clear()


    def set_content_type(self, mime_type ):
        """ Sets the new content type. NOTE: Automatically
        adds the ContentType phrase. To override, use ocerride_content_type() """
        self.content_type = "Content-Type: %s"%(mime_type)

    def get_content_type( self ):
        """ Retreives the MIME type set as the
        response to ContentType header. """
        return self.contet_type


    def set_response_header( self, header_name, value ):
        """ Sets any number of HTTP server response header
        values. """

        self.response_header_dict[ header_name ] = value


    def set_redirect( self, url ):
        """ Convenience method for setting a Location
        header for redirecting users to a new URL. """

        self.set_response_header( "Location", url )


    def remove_response_header( self, header_name ):
        """ Removes a response header from the list
        of headers set. """

        if self.response_header_dict.has_key( header_name ):
            del self.response_header_dict[ header_name ]
        

    def override_content_type( self, content_type_string ):
        """ Overrides the content type string header all
        together with a new value. This method makes no
        attempt to ensure propper header format. """

        self.content_type = content_type_string
        


    ######
    # From this point on we are cloning and
    # working with the emitter interfaces


    def set_search_path(self, search_path):
        self.template_processor.set_search_path( search_path )


    def add_vars(self, env):
        """
        Add a dictionary of variables to the template processor.
        """
        self.template_processor.add_vars( env )
        

    def add_var(self, name, value):
        """
        Add a single binding between 'name' and 'value' to self.form_vars.
        """
        self.template_processor.add_var( name, value )


    def get_template_processor( self ):
        """ Convenience method for retreiving
        the underlying template processer instance. """
        return self.template_processor 


    def set_template_processor( self, tp_name ):
        """ Instantiates and sets a new template processor
        based on the list of well known processor names. If the
        name dprocessor can't be found, we raise an exception."""

        if tp_name == ZPT:
            from wpl.template_processor import ZPTTemplateProcessor
            tp = ZPTTemplateProcessor.ZPTTemplateProcessor()
        elif WRITE_PROCESSOR:
            tp = TemplateProcessor.TemplateProcessor()
            
        else:
            raise Exception( "TemplateProcessor name %s not supported."%(tp_name) )

        # a template processor must have been instantiated
        # set the instance
        self.set_template_processor_instance( tp )
        


    def set_template_processor_instance( self, tp ):
        """ Sets a new template processor. This only changes the
        template process instance. The vars in the object
        are still maintained. """


        if isinstance( tp , TemplateProcessor.TemplateProcessor ):
            tp.default_vars.update( self.template_processor.default_vars )
            self.template_processor = tp
        else:
            raise Exception( "Parameter tp is not a wpl.template_processor.TemplateProcessor class." )

        pass
    

    def set_encode_file_name(self, file_name):
        """
        Set the filename to be encoded via the encode() method. This filename
        should correspond to a text file, possibly containing WriteProcessor
        variables.
        """
        self.template_processor.set_encode_file_name( file_name )


    def get_encode_count( self ):
        """ Accessor method used to track the number of times
        that the encode method was called. """

        return self.template_processor.get_encode_count()



    def encode(self, alternate_template_file="", prepend_text=''):
        return self.template_processor.encode( alternate_template_file, prepend_text )


    def encode_final_document(self, prepend_text=''):
        """
        Process the template.. 
        """

        header_string = ""


        # If there are server headers, emit those first
        if len( self.response_header_dict.keys() ) > 0:
            for header in self.response_header_dict.keys():
                header_string = header_string +  "%s:%s\n"%( header, self.response_header_dict[header] )
                

        # If 'write_cookies' was enabled, emit the cookies. Otherwise, toss
        # the cookies. (Just had to say that.)
        cookies_str = string.strip( str( self.cookies ) )
        if self.write_cookies == 'yes' and cookies_str != "" :
            header_string = header_string + cookies_str + "\n" 

            
        # If 'write_content_type' is 'yes', emit the content type header.
        if self.content_type:
            header_string = header_string + self.content_type + "\n\n"

        if prepend_text:
            header_string = header_string + prepend_text

        # call the template processor's encode method
        result = self.template_processor.encode( prepend_text=header_string )
        
        return result



    def __getitem__( self, var ):
        """ Overrides the use of [] operators
        for accessing the tempalte processor data values. """
        
        return self.template_processor[ var ]
        pass


    def __setitem__( self, var, value ):
        """ Overloads the use of [] operators for
        setting template processor data values. """

        # always set values in the user name space
        self.template_processor[ var ] = value
        pass


    def __delitem__( self, var ):
        """ Overloads the use of [] operatord for
        removing data values. """

        del self.template_processor[ var ]


    def has_key( self, var ):
        """ Overrides the standard dictionary key
        lookup. """

        return self.template_processor.has_key( var )
    

    def get( self, var, alt=None ):
        """ Overrides the standard dictionary
        safe value retrieval. """

        return self.template_processor.get( var, alt )


    def keys( self ):
        """ Retrieves all of the keys in the response
        object data. """

        return self.template_processor.keys()

    def error(self, message, emitContentHeader=1):
        """
        This is used to guarantee that any error that occurs when dispatching a
        form results in valid HTML being generated. It also guarantees that a
        meaningful message will also be displayed.
        """
        
        env = {}
        env['Error'] = message
        
        if emitContentHeader:
            print 'Content-type: text/html\n\n'
            
        wp = SimpleWriter.SimpleWriter()
        wp.compile(errorText)
        print wp.evaluate(env)


    def __str__( self ):
        """ Prints representation of the object. """

        s = "Data stored in Response:\n"
        for k in self.keys():
            s = s + "%s : %s\n"%( k, self.get( k, "" ) )



        return s
