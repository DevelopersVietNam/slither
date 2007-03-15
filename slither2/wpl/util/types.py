#
# These utilities can be used (statically) to perform various
# general functions (e.g. type testing, etc.)

from UserDict import UserDict
from UserList import UserList

def isPythonList(list):
  return type(list) == type([])

def isPythonDict(dict):
  return type(dict) == type({})

def isUserList(list):
  return isinstance(list, UserList)

def isUserDict(dict):
  return isinstance(dict, UserDict)

def isAnyList(list):
  return isPythonList(list) or isUserList(list)

def isAnyDict(dict):
  return isPythonDict(dict) or isUserDict(dict)

def isPythonString(s):
  return type(s) == type('')
  
def isAnyString(s):
  return type(s) == type('')

