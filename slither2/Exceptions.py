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




class StateInterfaceException( Exception ):
    def __init__( self, value ):
        self.__value = value

    def __str__( self ):
        return self.__get_value()    

    def __repr__( self ):
        return self.__get_value()   

    def __get_value( self ):
        if type( self.__value ) == type( "" ):
           return self.__value
        else:
           return `self.__value`



class LoadException( Exception ):
    def __init__( self, value ):
        self.__value = value

    def __str__( self ):
        return self.__get_value()    

    def __repr__( self ):
        return self.__get_value()   

    def __get_value( self ):
        if type( self.__value ) == type( "" ):
           return self.__value
        else:
           return `self.__value`



class StageProcessException( Exception ):
    def __init__( self, value ):
        self.__value = value

    def __str__( self ):
        return self.__get_value()

    def __repr__( self ):
        return self.__get_value()

    def __get_value( self ):
        if type( self.__value ) == type( "" ):
           return self.__value
        else:
           return `self.__value`
