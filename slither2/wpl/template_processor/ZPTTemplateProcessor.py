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

import sys
import os.path
import string


from wpl.template_processor.TemplateProcessor import TemplateProcessor
from PageTemplates.PageTemplate import PageTemplate

from HTMLMask import *


class ZPTTemplateProcessor( TemplateProcessor ):


    def __init__( self ):
        TemplateProcessor.__init__( self )
        pass



    def encode(self, alt_template_file = "", prepend_text=''):
        """
        Process the template using the ZPT toolkit from Zope. 
        """


        template_file = self.encode_target
        if alt_template_file and\
           alt_template_file != "":
            template_file = alt_template_file

        template_file = string.strip( template_file )

        # look for the file in the search path
        template_file_with_path = ""
        for search_path in self.search_path:

            template_file_with_path =  os.path.join( search_path, template_file )
            if os.path.isfile( template_file_with_path ):
                break;
            else:
                template_file_with_path = ""


        if template_file_with_path == "":
            raise IOError( "Could not find file %s in search path."%(template_file) )

        # open the file and read it
        template_string = open( template_file_with_path, "r" ).read()


        # create ZPT PageTemplate
        pt = PageTemplate() 

        # import template to the PageTemplate engine
        pt.write( template_string )

        #td = {}
        #for k in self.default_vars.keys():
        #    td[ k ] = maskHTML( self.default_vars[ k ] )
        
        # "cook" and render the document
        #output = unmaskHTML( apply( pt, [], td ) )
        output = apply( pt, [], self.default_vars )
        self.last_encoding = prepend_text + output


        #sys.stderr.write( "ENCODING: %s"%( self.last_encoding ) )

        # up the counter and cache the results
        self.encode_count = self.encode_count + 1

        # Finally, return the result.
        return self.last_encoding


