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


import os.path
import os
import sys




def change_cwd( dir, check_only=0 ):
    """ Changes the current working directory to  
        the supplied sirectory name. """

    try:
        # make sure that dir exists and is a directory
        if os.path.isdir( dir ):
            if check_only == 0:
                os.chdir( dir )     
                return ( 1, "Changed dir to '%s'."%( dir ) )
            else:
                return ( 1, "Dir '%s' exists."%( dir ) )
    
        return ( 0, "Dir '%s' is not a valid directory."%( dir ) )
    except:
        return ( 0, "Error while changing dir. to '%s'.\nDetails: %s"%( dir, sys.exc_info()[1] ) )



def format_dict( dict ):
    """ Convenience method for printing local
    Python dictionaries is a pretty way. """

    s = ""
    
    if type( dict ) == type({}):
        for key in dict.keys():
            s = s + "%s : %s\n"%( key, dict[ key ] )
            
    else:
        s = "(not a dictionary)"

    return s

              
        
