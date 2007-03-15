"""
        wpl.directory is a library file used to create a scoped name space in Python.
        This file part of the wpl.directory.Directory library.
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



Directory.py - A scoped dictionary abstraction for Python

This class is named after a very familiar concept from operating systems:
the directory, which is an integral part of filesystem management.

We'll not go into that here. Instead we'll discuss why you'd want such a 
thing.

In BizTools, a number of tools basically need the ability to keep state
information. As the number of tools increases, we are going to want the 
ability to segregate the state for a specific tool easily. Dictionaries
allow the possibility of doing this but the experience is ultimately 
unwieldly and requires a great deal of self-discipline. In practice, most
of us (including the author of this module) lack the self-discipline and
end up polluting the namespace with garbage and making life miserable for
everyone else.

A typical usage scenario is the following:

1. A tool is about to be dispatched (e.g. the ControlPanel). The BizTools
    driver will change the directory to a tool-specific directory.


The tool needs to keep state between invocations. This is the nature of 
CGI and the web: it is inherently stateless. The only way to have states
is with a persistent object. We use a Python dictionary for this.

2. The tool has its own "directory" for reading/writing entries. It also
    might need access to the root directory, where BizTools maintains a
    number of settings.

3. The tool might want to keep other directories. This is true for commands
    that are particularly complex and (themselves) need to maintain state.

4. The tool finishes a certain activity. The tool needs a way to clean
    state information that's no longer needed. 

5. Every time a tool runs, it's persistent information needs to be saved.
    As many tools and functions can be executed freely in BizTools, it is
    possible that one tool is brought up, then another, then back to the
    same tool again, etc.


I started with the assumption that this is a special kind of dictionary with
scoping capabilities. In many respects, the same kind of work that goes
into making a compiler symbol table needed to be done here. 

Class Directory is a subclass of UserDict. It has a number of functions 
related to directory management. The most important thing to note is that
a Directory, being a dictionary, can do ANYTHING a Python dictionary can
do. So by default it has all of those functions and operators. Some have
been overridden to provide specific functionality to the directory.

"""

from UserDict import UserDict
from string import whitespace, join

def my_split(s, sep=None, maxsplit=0):
    """my_split(str [,sep [,maxsplit]]) -> list of strings

    Return a list of the words in the string s, using sep as the
    delimiter string.  If maxsplit is nonzero, splits into at most
    maxsplit words If sep is not specified, any whitespace string
    is a separator.  Maxsplit defaults to 0.

    This version of split avoids the call to splitfields() that messes
    up everything. I can't believe they got this one wrong.

    """
    if sep == None:
        sep = whitespace
    res = []
    i, n = 0, len(s)
    if maxsplit <= 0: maxsplit = n
    count = 0
    while i < n:
        while i < n and s[i] in sep: i = i+1
        if i == n: break
        if count >= maxsplit:
            res.append(s[i:])
            break
        j = i
        while j < n and s[j] not in sep: j = j+1
        count = count + 1
        res.append(s[i:j])
        i = j
    return res

class PathRef:
    """
    Used to index subdirectory information in the Directory class.
    Subdirectories are instances of PathElement. 
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'PathRef "%s"' % self.name

    __repr__ = __str__

    def __hash__(self):
        return hash(self.name)

    def __cmp__(self, other):
        if isinstance(other, PathRef):
            return cmp(self.name, other.name)
        else:
            return 1

class PathElement(PathRef):
    """
    Used to wrap subdirectory content, which is a nested dictionary.
    Inherited from PathRef to get the name information.
    """
    def __init__(self, name, data):
        PathRef.__init__(self, name)
        self.data = data

    def __str__(self):
        return 'PathElement "%s" w/%d Entries' % (self.name, len(self.data.keys()))

    __repr__ = __str__

class Directory(UserDict):
    def __init__(self, init_data={}, default_get=None):
        """
        Construct a Directory instance. A Directory is a UserDict, so we
        must make it possible for clients to supply an initial dictionary
        (or even, Directory) on which this Dictionary will be based.

        default_get: default value to be returned in the event get() is
        called with a key not present in the Directory.

        Attributes:
        self.top_path: The starting point is always root ("/")
        self.top_data: The starting directory is always the starting
           dictionary (the dictionary belonging to root).
        self.current_path: The current directory, self.top_data
        self.stack: The pushd()/popd() stack.
        self.pe_cache: Cache of PathRef objects. PathRef objects are used
           to refer to subdirectories. The idea of caching them is to
           optimize lookup of subdirectories. For example, if a user asks
           for /xyz/pdq, PathRef("xyz") is used to find the subdirectory,
           relative to "/" (the starting point) and PathRef("pdq") gets
           the next subdirectory. By keeping a cache, we don't need to
           repeatedly construct these path components when looking up
           a path. (XYZ: Users should call clear_cached_information() to
           remove any temporary data structures prior to pickling.)
        
        """
        UserDict.__init__(self,init_data)

        # The value to be returned anytime a get fails (not implemented yet)
        self.default_get = default_get

        # Name of root path
        self.top_path = '/'

        # Data (dictionary) of root path
        self.top_data = self.data

        # Current path (for pushd/popd)
        self.current_path = self.top_path

        # pushd/popd stack
        self.stack = []

        # PathElement cache
        # always contains associations between a subdir name 
        # and a PathElement. e.g. "name" -> PathElement("name", None)
        self.pe_cache = {}

    def import_list(self, content):
        """
        This form allows you to import a list of triples to initialize
        the dictionary--quickly. The triples consist of path, key, value.
        The path will be created if it does not exist.
        """
        for triple in content:
            (path, key, value) = triple
            if not path[0] == "/":
                continue
            dir = self.create(path)
            dir[key] = value
            
    def __getPathRef(self, name):
        """
        Given a path component, get the index (a PathRef instance) if it
        exists. If no such instance exists, create one and store it in
        self.pe_cache). This is an internal method.

        """
        if not self.pe_cache.has_key(name):
            self.pe_cache[name] = PathRef(name)
        return self.pe_cache[name]

    def __fast_lookup(self, path):
        """
        This method gets the subdirectory's dictionary. The path is first
        split into its components. Then the internal __fast_lookup_list()
        method call is performed to actually locate the subdirectory's
        dictionary.
        """
        path_elements = self.__split_path(path)
        return self.__fast_lookup_list(path_elements)

    def __fast_lookup_list(self, path):
        """
        See __fast_lookup(). This internal method is used when we already
        have split the path into a list of path components.

        """
        data = self.top_data
        for dir in path:
            pe = self.__getPathRef(dir)
            data = data[pe].data
        return data

    def __split_path(self, path):
        """
        An internal method to split a path (specified as a string) into
        a list containing the components. e.g. /p1/p2/.../pN is split into
        ["p1","p2", ..., "pN"].
        """
        return my_split(path, '/')

    def __displace_path(self, path):
        """
        Compute a displacement from self.current_path. The path must be
        specified as a string. This string (path) is split into its components
        and then the displacement from self.current_path is computed. When
        "." and ".." are found, they are evaluated. Note that this method
        is used to create a CANONICAL path, which means that the path
        that is computed may/may not exist yet. This detail is very important
        as no assumptions are made in this routine, except to ensure that
        the canonical path has the potential to be valid. For example,
        using ".." to refer to a directory above "/" is strictly prohibited
        and results in an exception. All other paths must actually be used
        before an exception will occur.

        """
        path_parts = self.__split_path(self.current_path)
        rel_path_parts = self.__split_path(path)
        for part in rel_path_parts:
            if part == '.':
                continue
            if part == '..':
                if len(path_parts) < 1:
                    raise "cannot 'cd' above /"
                path_parts.pop()
            else:
                path_parts.append(part)

        return path_parts
                

    def __compute_path_list(self, path):
        """
        Given a path, absolute or relative, compute the new path as a list.
        This is the internal method that is used to determine what the path
        would be after changing it in some way. If the path begins with "/",
        then the value of self.current_path is going to be completely
        replaced. Otherwise, it's a relative path and represents a
        displacement. Another internal method, __displace_path() handles
        the details of computing the new path for relative paths.
        """
        if type(path) == type([]):
            return path
        elif type(path) == type(''):
            if path[0] == '/':
                return my_split(path, '/')
            else:
                return self.__displace_path(path)
        else:
            raise "Invalid Path Type", type(path)

    def __compute_path_string(self, path):
        """
        See __compute_path_list(). This basically gives the string
        representation of the list of path components computed by
        the forementioned internal method.
        """
        return "/" + join( self.__compute_path_list(path), "/" )

    def create(self, path):
        """
        Create a subdirectory using the specified path. The path may
        be specified as a list or a string. A list will be taken as
        an absolute path, starting from "/". A string can be an absolute
        path (beginning with "/") or a relative one. The internal
        method, __compute_path_list() will compute the absolute
        path and attempt to create the subdirectories, beginning from "/".
        The create() routine is semantically equivalent (at least in terms
        of outcome) to mkdir -p path in Unix.
        """
        path_elements = self.__compute_path_list(path)
        data = self.top_data
        dirPath = []
        for dir in path_elements:
            pe = self.__getPathRef(dir)
            if not data.has_key(pe):
                data[pe] = PathElement(dir,{})
            dirPath.append(dir)
            data = data[pe].data 
        return data

    mkdir = create

    def copy_dir(self, path1, path2, **props):
        """
        Perform a deep copy of the directory referred by path1 to path2.
        
        The following keyword properties may be specified and result
        in different behavior.
        
        keys: The list of keys to be copied from path1 to path2. Using
              this option only copies the entries in path1 and does not
              perform a deep copy.

        """
        p1_data = self.__fast_lookup(path1)
        try:
            p2_data = self.__fast_lookup(path2)
        except:
            p2_data = self.create(path2)

        # check for the "entries" property.
        keys = props.get('keys', None)

        # if not specified or None, perform a deep copy.
        if keys == None:
            p2_data.update(p1_data)
        # otherwise just copy the entries, if they're present.
        else:
            for name in keys:
                if p1_data.has_key(name):
                    p2_data[name] = p1_data[name]

    def getpwd(self):
        """
        This method makes the Directory class "feel" like Unix. It simply
        returns the current active directory. (current working directory
        a la Unix)
        """
        return self.current_path
    
    def pushd(self, path):
        """
        This is the equivalent of d.cd(path). Before this happens,
        the current values of self.current_path and self.data are pushed
        onto a context stack for subsequent use by popd().

        """
        self.stack.append( (self.current_path, self.data) )
        self.current_path = path
        self.data = self.__fast_lookup(path)

    def popd(self):
        """
        See pushd(). Attempting to call this method more times than pushd()
        has been called will result in the current directory being set to "/"
        and the dictionary associated with the root level directory.

        """

        if len(self.stack) == 0:
            self.data = self.top_data
            self.current_path = self.top_path
            return None
        else:
            previous_dir = self.stack.pop()
            self.current_path = previous_dir[0]
            self.data = previous_dir[1]
            return previous_dir

    def cd(self, path=None):
        """
        Change directory to path, which may be absolute or relative.
        Calling this method with path == None results is equivalent to
        cd("/").

        """

        if path != None:
            returnValue = (self.current_path, self.data)
            try:
                if path[0] != '/':
                    path_parts = self.__displace_path(path)
                    path = self.__compute_path_string(path_parts)
                    
                self.data = self.__fast_lookup(path)
                    
            except:
                raise "DirectoryError","Directory %s does not exist." % str(path)
            self.current_path = path
            return returnValue
        else:
            returnValue = (self.current_path, self.data)
            self.current_path = '/'
            self.data = self.top_data
            return returnValue

    def __compute_str(self, dict, path=[]):
        """
        Compute the string representation for a particular directory/
        path combination. This is an internal method that is driven by
        toString() and __str__() methods.

        """
        localRepr = ''
        TAB = "  "

        # first the header
        tabs = len(path)
        localRepr = tabs * TAB
        localRepr = localRepr + "{\n"
        localRepr = localRepr + (tabs + 1) * TAB + "# directory /" + join(path,"/") + '\n'

        # now the current dictionary's entries
        for k in dict.keys():
            if not isinstance(dict[k], PathElement):
                localRepr = localRepr + (tabs + 1) * TAB
                localRepr = localRepr + "%s : %s\n" % (repr(k), repr(dict[k]))

        # now descend into each subdirectory
        for k in dict.keys():
            if isinstance(dict[k], PathElement):
                #localRepr = localRepr + (tabs + 1) * TAB  +
                path.append(dict[k].name)
                localRepr = localRepr + self.__compute_str(dict[k].data, path)
                path.pop()

        # footer
        localRepr = localRepr + tabs * TAB
        localRepr = localRepr + "}\n"

        return localRepr

    def toString(self, path="/"):
        """
        Driver method to compute the string representation of a directory,
        starting at path.

        """
        entry = self.__fast_lookup(path)
        if type(path) == type(''):
            path = my_split(path, '/')
        return self.__compute_str(entry, path)


    def keys(self):
        """
        Returns a list of keys for the entries in the current directory,
        excluding subdirectory objects.
        """
        nonPEKeys = []
        for k in self.data.keys():
            if not isinstance(k,PathRef):
                nonPEKeys.append(k)
        return nonPEKeys

    def dirs(self):
        """
        As keys() excludes subdirectory information for the current directory,
        this method returns a list of subdirectories present in the current
        directory. The values returned are all PathElement instances.
        """
        
        subdirs = []
        for k in self.data.keys():
            if isinstance(k,PathRef):
                subdirs.append(self.data[k])
        return subdirs

    def values(self):
        """
        Returns a list of values for the entries in the current directory,
        excluding subdirectory objects.
        """
        nonPEValues = []
        for v in self.data.values():
            if not isinstance(v,PathElement):
                nonPEValues.append(v)
        return nonPEValues

    def items(self):
        """
        Similar to keys() and values() but returns the key/value pairs,
        excluding subdirectory objects.
        """
        nonPEItems = []
        for item in self.data.items():
            if not isinstance(item[1],PathElement):
                nonPEItems.append(item)
        return nonPEItems

    def clear(self):
        """
        Removes all entries in the current directory, excluding subdirs.
        """
        for k in self.keys():
            if not isinstance(k, PathRef):
                del(self.data[k])

    def clear_all(self):
        """
        Removes everything in the current directory, including subdirs.
        """
        for k in self.data.keys():
            del(self.data[k])

        
    def __len__(self):
        """
        Returns the number of entries in the current directory, not
        counting subdirs, which should not be counted since (for all
        practical purposes) they are supposed to be transparent to
        the end user. (And keys() doesn't show them for that matter.)
        """
        return len(self.keys())

    def has_key(self, key):
        """
        Strictly speaking, we don't need to override this. However, this
        protects against malicious use where someone creates a
        PathRef(some-key) and tests membership.
        """
        return key in self.keys()

    def scoped_get(self, key):
        """
        Given a current directory, an attempt is made to find the
        key in the current directory and then in all ancestors, up to
        and including "/".
        """
        scope_path = self.__split_path(self.current_path)

        # Try to work from the current scope outward.
        while len(scope_path) > 0:
            dict = self.__fast_lookup_list(scope_path)
            if dict.has_key(key):
                return dict[key]
            scope_path.pop()

        # Failing that, try top level scope as a last result and use
        # the default_get value that was specified at construction time.
        return self.top_data.get(key, self.default_get)

    def scoped_get_list(self, key, **props):
        """
        Return a list of all directories, starting with the current and
        working out to "/", where a particular key was found.
        result = 'directory'|'tuple_list'
        """

        result_type = props.get('result','dictionary')
        if result_type == 'tuple_list':
            result = []
        elif result_type == 'dictionary':
            result = {}
        else:
            result = {}

        scope_path = self.__split_path(self.current_path)
        while len(scope_path) > 0:
            dict = self.__fast_lookup_list(scope_path)
            # print '*',scope_path, dict.keys()
            if dict.has_key(key):
                # print "found"
                if type(result) == type([]):
                    result.append( ("/" + join(scope_path,"/"), dict[key]) )
                elif type(result) == type({}):
                    result["/" + join(scope_path,"/")] = dict[key]
                print result
            scope_path.pop()
        return result

    def find(self, key, **props):
        """
        This preliminary version of find should be used with the understanding
        that it could completely change until it is renamed to find().

        To use this method, you specify a "key" that you're seeking. This
        key can be of any valid type that can index a dictionary. If you
        are trying to find a directory, it must be a proper string and may
        refer only to a single subdirectory.

        Properties may be specified:
        type:
          'dirs' -> equivalent to -type d in Unix.
          'keys' -> equivalent (roughly) to -type f (the file entries)
                    in Unix.
        result:
          'tuple_list': Return a list of tuples of the form (where, what),
              where 'where' is the directory where found
                and 'what' is the value that was found. In the case of
                           a directory, it's name is returned as the where
                           and what.
          'dictionary': Return a dictionary where result[where] = what.
          
        """
        result_type = props.get('result','dictionary')
        if result_type == 'tuple_list':
            result = []
        elif result_type == 'dictionary':
            result = {}
        else:
            result = None

        anchor = props.get('anchor','/')
        self.pushd(anchor)
        self.__find(key, props.get('type','keys'), result)
        self.popd()
        return result

    def __find(self, key, type, result):
        """
        Internal method to find the specified key. Type and result are
        obtained from the property list and set explicitly.
        """
        cwd = self.getpwd()
        if type in ['keys','all']:
            for k in self.keys():
                if k == key:
                    self.__found(result, self.data[k], cwd)
                
        if type in ['dirs','all']:
            for d in self.dirs():
                if d.name == key:
                    self.__found(result, None, cwd)

        for d in self.dirs():
            self.cd(cwd)
            self.cd(d.name)
            self.__find(key, type, result)
            
    def __found(self, result, what, where):
        """
        Record what was found where, based on what type of result is
        being constructed.
        """
        if type(result) == type([]):
            result.append( (where, what) )
        elif type(result) == type({}):
            result[where] = what
        
    def walk(self, **props):
        """
	Walk is a general routine for walking the Directory. There are several
	properties that can be set. This routine can conceivably be driven
	by a more specialized routine for convenience purposes.

	Properities:
	anchor = where to start (path /x/y/z/p...)
	traversal_type = 'dfs'|'bfs'
	depth = maximum depth (an integer, >= 0). If not specified, depth is
	  assumed infinite.
	on_dir = object with an on_dir(directory_name) method. If not specified,
          nothing is to be done when a directory is encountered.
	on_entry = object with an on_entry(directory_name, entry, value) method. If not
	  specified, nothing is to be done when an entry is encountered..
	"""

        # 'traversal_type' must be 'dfs' or 'bfs'. If omitted or incorrect,
        # it will be set to 'dfs'.

        traversal_type = props.get('traversal_type','dfs')
	if traversal_type not in ['dfs','bfs']:
           traversal_type = 'dfs'

        # Other properties are optional.
	anchor =  props.get('anchor', '/')
	depth = props.get('depth', None)
	on_dir = props.get('on_dir',None)
        if not hasattr(on_dir,'on_dir'):
           raise 'on_dir must refer to an object with an on_dir() method'

	on_entry = props.get('on_entry', None)
        if not hasattr(on_entry,'on_entry'):
           raise 'on_entry must refer to an object with an on_entry() method'
        
        self.pushd(anchor)
        self.__walk(traversal_type, depth, on_dir, on_entry, 0)
        self.popd()

    def walk_bfs(self, walk_obj, anchor="/", max_depth=None):
        self.walk(traversal_type='bfs', depth=max_depth, on_dir=walk_obj,
	          on_entry=walk_obj, anchor="/")

    
    def walk_dfs(self, walk_obj, anchor="/", max_depth=None):
        self.walk(traversal_type='dfs', depth=max_depth, on_dir=walk_obj,
	          on_entry=walk_obj, anchor="/")
    
    def __walk(self, traversal_type, depth, on_dir, on_entry, current_depth):

        # 'depth' is pruned here
        if depth != None and current_depth >= depth:
           return

        # The current working directory always needs to be known for proper
        # directory navigation and to make sure 'on_entry' and 'on_dir' are
        # replete with information.
       
        cwd = self.getpwd()

        if traversal_type == 'dfs':
           self.__walk_on_dir(on_dir, cwd)
           for d in self.dirs():
              self.cd(cwd)
              self.cd(d.name)
	      self.__walk(traversal_type, depth, on_dir, on_entry, current_depth+1)

        for k in self.keys():
           self.__walk_on_entry(on_entry, cwd, k, self.data[k])

        if traversal_type == 'bfs':
           self.__walk_on_dir(on_dir, cwd)
           for d in self.dirs():
              self.cd(cwd)
              self.cd(d.name)
	      self.__walk(traversal_type, depth, on_dir, on_entry, current_depth+1)

    def __walk_on_dir(self, on_dir, cwd):
        if on_dir: on_dir.on_dir(cwd)

    def __walk_on_entry(self, on_entry, cwd, name, value):
        if on_entry: on_entry.on_entry(cwd, name, value)

    def __getitem__(self, key):
        """
        See scoped_get(). It was a long period of soul searching. But I
        finally decided that gets and subscripts should return an item
        if it is found anywhere within scope, since this is a common usage.
        The problem is that you won't necessarily know where it was found,
        in which case an additional routine is provided.
        """

        if self.data.has_key(key):
            return self.data[key]
        return self.scoped_get(key)

    def get(self, key, failobj=None):
        """
        This version of get only considers the current directory.
        """
        if failobj != None:
            return self.data.get(key, failobj)
        else:
            return self.data.get(key, self.default_get)

    def get_dir(self, path):
        """
        This allows a lookup to be performed. The form is a regular
        path but must contain at least one trailing element to indicate
        the entry to be found. Examples shown in test_5()
        """
        path_parts = my_split(path, "/")
        if len(path_parts) < 1:
            return None 
        dir = path_parts[0:-1]
        entry = path_parts[-1] 
        try:
            dict = self.__fast_lookup_list(dir)
        except:
            raise "Invalid directory %s" % (self.__compute_path_string(dir))
        return dict[entry]

    def set_dir(self, path, value):
        """
        This allows an entry to be set in a directory. The form is a regular
        path but must contain at least one trailing element to indicate
        the entry to be set. Examples shown in test_5()
        """
        path_parts = my_split(path, "/")
        if len(path_parts) < 1:
            raise "set_dir requires at least one path component (an entry name)" 
        dir = path_parts[0:-1]
        entry = path_parts[-1] 
        dict = self.create(dir)
        dict[entry] = value

    def __str__(self):
        return 'Directory: ' + self.__compute_str(self.top_data)

#
# test_2() demonstrates the find() function (and how you can quickly
# import data into a Directory using a list of triples.
#
def test_2():
    d = Directory()
    d.import_list([ ('/','a','5'),
                    ('/a','a',10),
                    ('/b','a','15'),
                    ('/a/c','a','1000') ])
    print "d.find('a') = ", d.find('a')

    print "d.find('a', type='all') = ", d.find('a', type='all')

    print "d.find('a', type='all', result='tuple_list') = ", d.find('a', type='all', result='tuple_list')

    print "d.find('a', type='all', result='dictionary') = ", d.find('a', type='all', result='dictionary')

def test_3():
    d = Directory()
    d.import_list([ ('/','a','5'),
                    ('/a','a',10),
                    ('/b','a','15'), ('/b','b1','10'), ('/a/c/c1','c1',5),
                    ('/a/c','a','1000'), ('/a/d','a','200') ])
    print "directory",d
    print "from /, d.scoped_get_list('a') = ", d.scoped_get_list('a', result='tuple_list')

    d.cd("/a/c")
    print "from /a/c, d.scoped_get_list('a') = ", d.scoped_get_list('a')
    d.cd('/a/c/c1')
    print "from /a/c, d.scoped_get_list('b1') = ", d.scoped_get_list('b1')
    d.cd('/a/d')
    print "from /a/d, d.scoped_get_list('a') = ", d.scoped_get_list('a')
    d.cd('/b')
    print "from /b d.scoped_get_list('b1') = ", d.scoped_get_list('b1')
    print "from /b d.scoped_get_list('b1') as list = ", d.scoped_get_list('b1', result='tuple_list')
    

def test_1():
    d = Directory()

    d['user'] = 'george'
    d['userid'] = 25

    cp = d.create('/ControlPanel')
    cp_edituser = d.create('/ControlPanel/edituser')

    cp['current_func'] = 'cmd_edituser'
    cp['activations'] = ['edituser_form', 'edituser_entry']

    cp_edituser['new_name'] = 'georgio'
    cp_edituser['new_password'] = 'armani'

    print "Entire Directory"
    print d.toString('/')

    print "/ControlPanel"
    print d.toString('/ControlPanel')

    print "/ControlPanel/edituser"
    print d.toString("/ControlPanel/edituser")

    print "pushd /ControlPanel"
    d.pushd('/ControlPanel')
    print d.data


    print "pushd /ControlPanel/edituser"
    d.pushd('/ControlPanel/edituser')
    print d.data
    print

    print "popd"
    info = d.popd()
    print "popped %s" % str(info[0])
    for k in d.keys():
        print k
    print

    print "popd"
    info = d.popd()
    print "popped %s" % str(info[0])
    for k in d.keys():
        print k
    print

    print "cd /ControlPanel"
    prev = d.cd('/ControlPanel')
    print "previous dir is %s" % prev[0]
    print "keys in /ControlPanel %s" % str(d.keys())


    print "cd /ControlPanel/edituser"
    prev = d.cd('/ControlPanel/edituser')
    print "previous dir is %s" % prev[0]
    print "keys in /ControlPanel/edituser %s" % str(d.keys())


    print "cd /"
    prev = d.cd('/')
    print "previous dir is %s" % prev[0]
    print "keys in / %s" % str(d.keys())

    print "trying a bad path"
    print "cd /A/B/C"
    try:
        prev = d.cd('/A/B/C')
        print "previous dir is %s" % prev[0]
        print "keys in /A/B/C %s" % str(d.keys())
    except:
        print "very good. It failed."
        pass


    print "Scope tests"
    d.cd('/ControlPanel/edituser')
    print 'user', d.scoped_get('user')
    print 'userid',d.scoped_get('userid')
    print 'undefined is None in this case', str(d.scoped_get('undefinedattribute'))
    print 'current_func', d.scoped_get('current_func')

    print 'user', d['user']
    print 'userid', d['userid']
    try:
        print 'undefined should results in KeyError', str(d['undefinedattribute'])
    except KeyError:
        print 'good, a key error was obtained for undefinedattribute.'

    print 'current_func', d['current_func']
    return d

class Walk4:
    def on_dir(self, cwd):
        print 'directory', cwd

    def on_entry(self, cwd, name, value):
        print 'entry in %s (%s -> %s)' % (cwd, name, value)

def test_4():
    d = test_1()
    w = Walk4()

    tests = [
    "d.walk(traversal_type='dfs', anchor='/', on_dir=w, on_entry=w, depth=None)",
    "d.walk(traversal_type='dfs', anchor='/', on_dir=w, on_entry=w, depth=None)",
    "d.walk(traversal_type='bfs', anchor='/ControlPanel', on_dir=w, on_entry=w, depth=None)"
    ]

    for t in tests:
       print 'running test ',t
       exec(t)
       print ''

def test_5():
    d = test_1()

    d.get_dir("/user")

    try:
        d.get_dir("/username")
    except:
        print "test passed - username not found as expected"
            
    try:
        print d.get_dir("/ControlPanel/edituser")
    except:
        print "test passed - edituser is a subdir, should not be found"

    print d.get_dir("/ControlPanel/edituser/new_name")

    try:
        print d.get_dir("/")
    except:
        print "test passed, path requires at least one dir, one entry."

def test_6():
    d = Directory()
    try:
        d.set_dir("/","0")
    except:
        print "test passed; path requires at least one dir, one entry."
    d.set_dir("/top","1")
    d.set_dir("/top/a","2")
    d.set_dir("/top/b","3")
    d.set_dir("/top/a/a","4")
    d.set_dir("/top/b/a","5")
    d.set_dir("/top/a/b","6")
    d.set_dir("/top/b/b","7")
    print d.toString("/")

tests = {
    'test_1' : test_1,
    'test_3' : test_3,    
    'test_2' : test_2,
    'test_4' : test_4,
    'test_5' : test_5,
    'test_6' : test_6
    }
    
import sys
if __name__ == '__main__':
    runtest = tests.get(sys.argv[1], None)
    if runtest != None: runtest()
