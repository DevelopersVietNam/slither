"""
The way to use it is to make sure you have this class in your top directory.

There should be a .pythonpathrc file (alternatively, you can specify your
own file. Make sure it is reachable though. This code will not tank if your
file isn't found, since 'rc' files are inherently optional in customary use.

You can put one or more directories per line, separated by whitespace. You
can change the separator if desired.
"""



import sys
import string
import os.path


DEFAULT_FILE_LIST = [
  ".pythonpathrc",
  "pythonpathrc",
  ]
  


class Path:
  
  def __init__(self, sep=":", rcFile=""):

    self.exclude_list = []

    if rcFile=="":
      for file_name in DEFAULT_FILE_LIST:
        if self.readFile( file_name, sep ) == 1:
          break
        else:
          pass
    else:
      self.readFile( rcFile, sep )


  def readFile( self, path_file_name, sep=":" ):

    if not os.path.isfile( path_file_name ):
      #print "Not a path file: ", path_file_name
      return 0

    f = open( path_file_name, 'r' )
    dir_listing = f.readlines()

    #print "PATH: dir_listing: ", dir_listing

    self.resetExcludeList()
    path_list = []
    for dir_chunk in dir_listing:
      dir_chunk = string.strip( dir_chunk )

      if dir_chunk == '':
        continue

      dirs = string.split( dir_chunk, sep )

      for dir in dirs:

        # get any operation commands
        ( o, d ) = self.parsePathEntry( dir )
          
        if o == '-':
          #DEBUG
          #print "PATH: Excluding dir '%s'"%( dir )
          self.exclude_list.append( d )
        else:
          path_list.append( dir )


    #print "PATH: Exclude list: ", str( self.exclude_list )
    #print "PATH: Path list: ", path_list

    # add the dirs and subdirs    
    for dir in path_list:
      (o, d ) = self.parsePathEntry( dir )

      if o == '+':
        self.addSubDirs( d )
      elif o != '#':
        self.addDir( d )

    return 1



  def resetExcludeList( self ):
    self.exclude_list = []



  def parsePathEntry( self, entry ):
    """ Parses a Path entry for op codes
    and directory names."""

    # clean the entry
    entry = string.strip( entry )

    if len( entry ) < 2:
      return ( '#', '' )

    # get any operation commands
    dir = ''
    op = ''
    if entry[0] in ( '-', '+' ):
      # operation code found
      op = entry[0]
      dir = entry[1:]
    elif entry[0] == "#":
      # this is a comment
      op = '#'
      dir = ''
    else:
      # this is just a directory
      dir = entry
      dir = string.strip( dir )

    if dir == '':
      op = '#'

    return ( op, dir )


  def addDir(self,dir):
    """ Adds a directory to the sys.path variable."""

    if not dir in self.exclude_list and \
       not dir in sys.path and \
       os.path.isdir( dir ):
      #DEBUG
      #print "PATH: Adding DIR '%s'"%( dir )
      sys.path.append(dir)
    else:
      #print "PATH: Path is not valid or exluded; not added: ", dir
      pass



  def addSubDirs( self, base='.' ):
     """ Adds all directories under the provided base
     directory to the python path variable.
     
     NOTE:If base is a relative path, then all dirs
     found will have a relative path as their base. To
     work with absolutel paths, the supplied base parameter
     must be an absolute path. No automatic resolution is performed.
     """

     #DEBUG
     #print "PATH: Adding SUB-DIR '%s'"%( base )

     os.path.walk( base, walk_dir_tree, self )   

    
  def __repr__(self):
    out_string = "sys.path [\n"
    for entry in sys.path:
      out_string = out_string + "  %s\n"%( entry )

    out_string = out_string + "\n]"
      
    return out_string


def walk_dir_tree( arg, dirname, names ):
  """ Helper method used to walk the tree and 
  add the dirs to the path python path."""

  if string.find( dirname, 'CVS' ) == -1:
     arg.addDir( dirname )



global path
path = Path()



