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



from State import State


class Congratulations( State ):

    # There is nothing to process() since this is the end of the line.
    # All passengers must now leave the train.

    def process( self ):
        return "Nothing to Return"


    # Render the Congratulations HTML page.

    def render( self ):
        #self.set_encode_file_name('Congratulations.html')
	return self.encode( 'Congratulations.html' )
