"""
        wpl.key_hen is a library file used to generate unique random keys in Python.
        This file part of the wpl.key_gen.KeyGen library.
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


# Standard imports
import string
import whrandom
import time


good_chars = string.digits + string.lowercase[:26] + string.uppercase[:26] 



def generate_key( length=10, char_set='all' ):
    """ Randomly generates a key of specified length. """

    if char_set == 'digits':
        char_list = string.digits
    elif char_set == 'letters':
        char_list = string.lowercase[:26] + string.uppercase[:26]
    else:
        char_list = good_chars

    char_list_limit = len( char_list ) - 1

    key = ''
    i = 0
    while i < length:
        key = string.join( [ key , char_list[ whrandom.randint( 0, char_list_limit ) ] ], '' )
        i = i + 1

    return key 



def generate_dated_key( format_string="%m-%d-%Y", length=10, char_set='all', delim="." ):
    """ Generates a key that also contians a time
        component. """

    return string.join( [ time.strftime( format_string, time.localtime( time.time() ) ), generate_key(length=length, char_set=char_set)  ], delim )



if __name__ == '__main__':

    print "\n********** KeyGen Test ************\n"

    print "Generating a default 10 letter random key:"
    print generate_key()

    print "Generating a 23 charachter random key:"
    print generate_key( length=23 )

    print "Generating a 12 charachter number only key:"
    print generate_key( length=12, char_set='digits' )

    print "Generating a 12 charachter letter only key:"
    print generate_key( length=12, char_set='letters' )

    print "Generating a 12 charachter dated key:"
    print generate_dated_key( length=12 )

    print "Generating a 12 charachter key with time values as well:"
    print generate_dated_key( length=12, format_string="%m-%d-%Y-%H-%M" )


    print "\n********** End of Test ************\n"
  
    
