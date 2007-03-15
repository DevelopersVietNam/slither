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
import time


# Non-stnadard imports 
from wpl.directory import Directory
from wpl.key_gen import KeyGen




class UserProfile( Directory.Directory ):


    def __init__( self, id='', init_data={}, default_get=None ):

        # initialize the directory
        Directory.Directory.__init__( self, init_data, default_get )

        self.__id = id
        if id == '':
            self.__id = KeyGen.generate_dated_key( length=16 )
        

        self.__creation_time = time.time()

        # state stack is a list of strings representing
        # State object to be executed
        self.__state_stack = []

        pass


    def pushStateStack( self, state_name ):

        if state_name != '':
            self.__state_stack.append( state_name ) 
            return self.getStackLength()
        else:
            return 0


    def popStateStack( self ):

        if len( self.__state_stack ) > 0:
            state_name = self.__state_stack[-1]
            del( self.__state_stack[-1] )
            return state_name
        else:
            return '' 


    def getStackLength( self ):
        return len( self.__state_stack )



    def getCreationTime(self, format_string='' ):
        if format_string != '':
            return time.strftime( format_string, time.localtime( self.__creation_time ) )
        else:
            return self.__creation_time


    def getId(self):
        return self.__id 


    def setId(self, id):
        if id != '':
            self.__id = id



if __name__ == '__main__':


    print "\n******** Testing UserProfile ***********\n"

    print "Creating a new UserProfile instance with no custom ID..."
    up = UserProfile()

    print "Printing empty UserProfile..."
    print up.toString()

    print "Getting the generated ID..."
    print up.getId()

    print "Getting the creation time in ticks..."
    print up.getCreationTime()

    print "Getting the creation time in local format..."
    print up.getCreationTime( format_string = "%m-%d-%Y" )

    print "\nTesting stack."
    print "Pushing a state onto the stack..."
    print up.pushStateStack( "aState" )

    print "Pushing another state...."
    print up.pushStateStack( "anotherState" )

    print "Getting stack length..."
    print up.getStackLength()

    print "Poping a state..."
    print up.popStateStack()
   
    print "Poping another state..."
    print up.popStateStack()

    print "Attempting to pop emty stack..."
    print up.popStateStack() 


    print "\nTesting directory capabilities..."
    print "Storing a value at root..."
    up['root_var'] = 'root_value' 

    print "Creating a directory..."
    up.create( '/a_dir' )
  
    print "Changing to directory..."
    up.cd( 'a_dir' )

    print "Storing value in directory..."
    up['dir_var'] = 'dir_value'

    print "Printing directory..."
    print up.toString()
