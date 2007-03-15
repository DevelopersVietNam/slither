__all__ = [ 'WebForm', 'SimpleCookie' ]

import os
import os.path


# __path__[0] contains the directory where the module root was found.
# os.getcwd() is the path to the dir containing the top of the package
# hierarchy. This will be dependent on sys.path.

# module_dir_fp is the full path to this directory.
cwd = os.getcwd()
module_dir_fp = os.path.join( cwd, __path__[0])


# we need the parent to find the sibling package subdirectories (for wpl)
# parent_dir is the full path to that directory, which is required for
# listdir to work properly (I think).
(parent_dir,junk) = os.path.split(module_dir_fp)

# this is the parent based on the subdirectory path __path__.
(parent,dir) = os.path.split(__path__[0])

# get the list of peer directories
subdirs = os.listdir(parent_dir)

# add them, if they're really dirs. It's possible subdirs returns files, 
# hence the test for "isdir" below.
for dir in subdirs:
   subdir = os.path.join(parent,dir)
   subdir_fp = os.path.join(cwd, subdir)
   if os.path.isdir(subdir_fp):
      __path__.append(subdir)

#print 'path',__path__
