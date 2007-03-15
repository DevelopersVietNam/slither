"""
        wpl.wp is a library file used to generate files via templates.
        This file part of the wpl.wp.WriteProcessor library.
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

# Standard Stuff
import string
import types

# Modules Used

from StringIO import StringIO
from UserList import UserList
from UserDict import UserDict

from wpl.wp.BasicSet import BasicSet
from wpl.wp.Emitter import Emitter, ListEmitter
from wpl.wp.SimpleWriter import SimpleWriter
from wpl.wp import ListFunctions
from wpl.util.types import *

TRIPLE_QUOTES = '"""'

class FileRules:
  def __init__(self):
    self.rules = {}

  def addRule(self, var, function):
    self.rules[var] = function

  def matchRule(self, var):
    if self.rules.has_key(var):
      return self.rules[var]
    else:
      return None

# Looping rules now share a common base class. The idea here is to make sure
# that they are all written similar to one another.

class LoopingRuleAdapter:
  def __init__(self):
    pass

  def preprocess(self):
    raise "LoopingRuleAdapter","Abstract Method preprocess() Invoked"

  def getVarList(self):
    return self.variables

  def evaluate(self, wp):
    raise "LoopingRuleAdapter","Abstract Method evaluate() Invoked"

  def getPattern(self, pattern):
    if isAnyString(pattern):
      return pattern
    elif isAnyList(pattern):
      textPattern = '('
      sep = ''
      for part in pattern:
        textPattern = textPattern + sep + self.getPattern(part)
        sep = ','
      textPattern = textPattern + ')'
      return textPattern
    else:
      return None

class LoopingRuleList:
  def __init__(self):
    self.ruleTable = {}

  def match(self, varList):
    if len(varList) > 0:
       return self.ruleTable.get( str(BasicSet(varList)), None)
    else:
       return None

  def addRule(self, loopingRule):
    if not isinstance(loopingRule, LoopingRuleAdapter):
       raise "WriteProcessor","only instances of LoopingRuleAdapter are permitted"
    if self.match(loopingRule.getVarList()):
       raise "WriteProcessor","attempt to introduce a conflicting rule"

    self.ruleTable[ str(BasicSet(loopingRule.getVarList())) ] = loopingRule

  def __repr__(self):
    repr = ''
    for rule in self.ruleTable.values():
       repr = repr + str(rule) + '\n'
    return repr



class DictLoopingRule(LoopingRuleAdapter):
  def __init__(self, keyPattern, valuePattern, values, sortByKey=1):
    LoopingRuleAdapter.__init__(self)
    self.keyPattern = keyPattern
    self.valuePattern = valuePattern
    self.values = values
    self.sortByKey = sortByKey
    self.variables = []
    self.preprocess()


  def preprocess(self):
    # Patterns can now be specified as a string or a list of names.
    self.keyPattern = self.getPattern(self.keyPattern)
    self.valuePattern = self.getPattern(self.valuePattern)
    self.combinedPattern = '(' + self.keyPattern + ',' + self.valuePattern + ')'
    testPattern = '(' + self.keyPattern + ',' + self.valuePattern + ')'
    testStmt = 'for ' + testPattern + ' in self.values.items(): pass'

    # This code uses metaprogramming to look into the current environment
    # and find out what variables exist before and after the "exec" statement
    # is executed below. Thus we need to make sure the namespace does not get
    # polluted when we call vars(). This is why the next two statements are
    # defined.

    envBefore = None
    envNow = None

    # Take a snapshot of the variables in the current environment.
    envBefore = vars().copy()

    # Now let us check whether the user's pattern is valid. At the same
    # time, we will also determine what variables are actually being used
    # in the pattern.

    try:
      exec testStmt
    except:
      raise "LoopingRule", "Data structure element does not match pattern"

    # Now take a snapshot of the variables after exec.
    envNow = vars().copy()

    # Compute the SET difference between the new and old environments.
    for var in envBefore.keys():
      if envNow.has_key(var): del envNow[var]

    
    varSet = BasicSet(envNow.keys())
    self.variables = varSet.rep

  def getVarList(self): 
    return self.variables

  def evaluate(self, wp):
    if self.sortByKey:
      _L_ = self.values.keys()
      _L_.sort()
      if self.sortByKey < 0:
        _L_.reverse()
      stmt = 'for ' + self.keyPattern + ' in _L_: '
      stmt = stmt + self.valuePattern + ' = self.values[' + self.keyPattern + '];'
    else:
      stmt = 'for ' + self.combinedPattern + ' in self.values.items(): '
    stmt = stmt + ' wp.emit(vars()),'
    exec stmt

  def __repr__(self):
    rep = 'DictLoopingRule(key="%s", value="%s",\n\tcombined="%s",\n\tsorting=%d\n\tmatches="%s")' % (str(self.keyPattern), str(self.valuePattern), str(self.combinedPattern), self.sortByKey, str(self.variables))
    return rep

# This looping rule allows iteration over any list of tuples. This will 
# probably be the preferred class for creating tables and selection lists.

class ListLoopingRule(LoopingRuleAdapter):
  def __init__(self, valuePattern, values):
    LoopingRuleAdapter.__init__(self)
    self.valuePattern = valuePattern
    self.values = values
    self.variables = []
    self.preprocess() 

  def preprocess(self):
    self.valuePattern = self.getPattern(self.valuePattern)
    testStmt = 'for ' + self.valuePattern + ' in self.values: pass'

    # This code uses metaprogramming to look into the current environment
    # and find out what variables exist before and after the "exec" statement
    # is executed below. Thus we need to make sure the namespace does not get
    # polluted when we call vars(). This is why the next two statements are
    # defined.

    envBefore = None
    envNow = None

    # Take a snapshot of the variables in the current environment.
    envBefore = vars().copy()

    # Now let us check whether the user's pattern is valid. At the same
    # time, we will also determine what variables are actually being used
    # in the pattern.

    try:
      exec testStmt
    except:
      raise "ListLoopingRule", "Data structure element does not match pattern"

    # Now take a snapshot of the variables after exec.
    envNow = vars().copy()

    # Compute the SET difference between the new and old environments.
    for var in envBefore.keys():
      if envNow.has_key(var): del envNow[var]
    varSet = BasicSet(envNow.keys())
    self.variables = varSet.rep

  def evaluate(self, wp):
    stmt = 'for ' + self.valuePattern + ' in self.values: '
    stmt = stmt + ' wp.emit(vars()),'
    exec stmt

  def __repr__(self):
    return 'ListLoopingRule(pattern="%s"\n\tmatches="%s")' % \
              (str(self.valuePattern), str(self.variables))
  
# This looping rule is for lists of dictionaries. The most notable specimen
# is the list of Record (which is a UserDict, which is a {}). When you want
# to take the results of an SQL query and quickly substitute them into a
# template, this is the way to do it!

class DictListLoopingRule(LoopingRuleAdapter):
  def __init__(self, dictList, variables, additionalBindings={}, empty_text=""):
    if not isAnyList(variables):
       raise "you must specify a Python list or UserList for this looping rule"
    if not isAnyDict(additionalBindings):
       raise "additional bindings must be a Python dictionary or UserDict"

    self.variables = variables
    self.dictList = dictList
    self.additionalBindings = additionalBindings
    self.empty_text = empty_text
    self.preprocess()

    LoopingRuleAdapter.__init__(self)

  def preprocess(self):
    if not isAnyList(self.dictList):
       raise "DictListLoopingRule","A list of dictionaries must be specified"

    self.variables = BasicSet(self.variables + self.additionalBindings.keys())
    self.variables = self.variables.rep

    if len(self.dictList):
       if isUserDict(self.dictList[0]):
          self.checkUserDict()
       else:
          self.checkStandardDict()


  def checkStandardDict(self):
    for dict in self.dictList:
       if not isPythonDict(dict):
          raise "DictListLoopingRule","List of {} must contain only {}"

  # This is a little optimization to avoid excessive calling of UserDict
  # methods. Since we never change the underlying dictionary in a WP
  # processing phase, we grab the ref and avoid all of those expensive
  # __intrinsic__ calls.

  def checkUserDict(self):
    for dict in self.dictList:
       if not isinstance(dict, UserDict):
          raise "DictListLoopingRule","List of UserDict must contain only UserDict"

  def evaluate(self, wp):
    # If the list is empty, nothing will be emitted.
    if not self.dictList:
       wp.emitter.emit(self.empty_text)
       return

    # Standard dictionaries and UserDict are handled slightly different
    # for performance reasons.

    if isPythonDict(self.dictList[0]):
       self.evaluate_dict(wp)

    # If the list is empty, nothing will be emitted.
    if isUserDict(self.dictList[0]):
       self.evaluate_user_dict(wp)

  def evaluate_dict(self,wp):
    if len(self.additionalBindings.keys()):
       for dict in self.dictList: 
          d = dict.copy()
          d.update(self.additionalBindings)
          wp.emit(d)
    else:
       for dict in self.dictList: 
          wp.emit(dict)

  def evaluate_user_dict(self,wp):
    if len(self.additionalBindings.keys()):
       for dict in self.dictList: 
          d = dict.data.copy()
          d.update(self.additionalBindings)
          wp.emit(d)
    else:
       for dict in self.dictList: 
          wp.emit(dict.data)

  def __repr__(self):
    return 'DictListLoopingRule(matches = %s additional %s on empty %s' \
       % (self.variables, self.additionalBindings.keys(), self.empty_text)

  
class LoopingRules:
  def __init__(self):
    self.rules = {}

  def match(self, variableList):
    variableList = ListFunctions.toSet(variableList)
    if self.rules.has_key(`variableList`):
      return self.rules[`variableList`]
    else:
      return None

  def addRule(self, keyPattern, valuePattern, env, sortByKey=1):
    testPattern = '(' + keyPattern + ',' + valuePattern + ')'
    testStmt = 'for ' + testPattern + ' in env.items(): pass'

    # This code uses metaprogramming to look into the current environment
    # and find out what variables exist before and after the "exec" statement
    # is executed below. Thus we need to make sure the namespace does not get
    # polluted when we call vars(). This is why the next two statements are
    # defined.

    envBefore = None
    envNow = None

    # Take a snapshot of the variables in the current environment.
    envBefore = vars().copy()

    # Now let us check whether the user's pattern is valid. At the same
    # time, we will also determine what variables are actually being used
    # in the pattern.

    exec testStmt # This needs to be in an exception context. Will add soon.


    # Now take a snapshot of the variables after exec.
    envNow = vars().copy()

    # Compute the SET difference between the new and old environments.
    for var in envBefore.keys():
      if envNow.has_key(var): del envNow[var]

    patternVars = envNow.keys()
    patternVars = ListFunctions.toSet(patternVars)
    self.rules[`patternVars`] = LoopingRule(patternVars,
                                            keyPattern, valuePattern, env,
                                            sortByKey)

  def __repr__(self):
    rep = 'LoopingRules:\n'
    for (ruleName,rule) in self.rules.items():
      rep = rep + `rule` + '\n'
    return rep


class WriteProcessor:

  # fileName can either be string (a file specification) or a file (handle)

  def __init__(self, fileName, searchPath, env, emitter=Emitter(), **props):
    #if hasattr(emitter,'emit'):
    if isinstance(emitter, Emitter):
      self.emitter = emitter
    else:
      self.emitter = Emitter()
    self.searchPath = searchPath

    if type(fileName) == types.FileType or isinstance(fileName, StringIO):
      self.fileName = None
      self.fp = fileName
    elif type(fileName) == types.StringType:
      self.fileName = fileName
      self.fp = None
    else:
      raise "Write Processor","fileName must be a valid file name or handle"

    self.env = env
    self.stack = []
    self.ruleTable = {}
    self.wp = SimpleWriter(self.emitter)
    self.loopingRules = LoopingRuleList()
    self.props = props
    if props.has_key('triple_quotes'):
       self.triple_quotes = str(props['triple_quotes']) in ['1', 'Y']
    else:
       self.triple_quotes = 0

  def __repr__(self):
    return "WriteProcessor:" + `self.loopingRules`

  def addLoopingRule(self, keyPattern, valuePattern, env, sortByKey=1):
    rule = DictLoopingRule(keyPattern, valuePattern, env, sortByKey)
    self.loopingRules.addRule(rule)

  def addListLoopingRule(self, valuePattern, value):
    rule = ListLoopingRule(valuePattern, value)
    self.loopingRules.addRule(rule)

  def addDictListLoopingRule(self, dictList, variables, additionalBindings={}, empty_text=""):
    rule = DictListLoopingRule(dictList, variables, additionalBindings, empty_text)
    self.loopingRules.addRule(rule)

  def addRecordLoopingRule(self, dictList):
    self.addDictListLoopingRule(dictList)

  def addFileRule(self, fileName, var, function):
    if not self.ruleTable.has_key(fileName):
      self.ruleTable[fileName] = FileRules()
    if callable(function):
      self.ruleTable[fileName].addRule(var, function)

  def getEmitter(self):
    return self.emitter

  def process(self):
    if self.fp == None:
      self.processFile()
    else:
      self.processFileHandle()


  # processFile() and processFileHandle() are really intended to be internal
  # (and private) methods. You should not directly call these. Use process()
  # and it will call the appropriate method based on whether you constructed
  # a WriteProcessor with a file name or file handle.

  def processFile(self):
    for dir in self.searchPath:
      try:
        self.fp = open(dir + "/" + self.fileName, 'r')
      except:
        continue
      if self.fp != None: break
    if self.fp == None:
      raise "Write Processor", "Cannot open: " + str(self.fileName)
    self.processFileHandle()

  def processFileHandle(self):
    fileName = self.fileName
    while 1:
      line = self.fp.readline()
      if not line:
         break

      # If the triple-quote mechanism for grouping lines as a single
      # line is available...
      if self.triple_quotes:

         # and if the line begins with triple quotes, collect all lines 
         # until the (a) the closing triple quote is found or (b) the 
         # end of file is encountered. End of file will not prevent what
         # has been collected thus far from being processed.

         if string.find(line, TRIPLE_QUOTES) == 0:
            text = ''
            while 1:
               line = self.fp.readline()
               if not line:
                  break
               if string.find(line,TRIPLE_QUOTES) == 0:
                  break
               text = text + line + '\n'
            line = text

      # If a file was specified for inclusion (this should cut of the cycle
      # eventually but most of us have been pretty careful not to include
      # files recursively.

      if line[0] == '>':
        includedFile = line[1:-1]
        currentFileState = (self.fileName, self.fp)
        self.fileName = includedFile
        self.stack.append(currentFileState)
        self.processFile()
        (self.fileName, self.fp) = self.stack.pop()
      else:
        self.wp.compile(line)
        varList = self.wp.getVars()
        ruleBasedEval = 0

        loopingRule = self.loopingRules.match(varList)
        if loopingRule != None:
          loopingRule.evaluate(self.wp)
          ruleBasedEval = 1
        else:
          for var in varList:
            if self.ruleTable.has_key(self.fileName):
              fileRules = self.ruleTable[self.fileName]
              function = fileRules.matchRule(var)
              if function:
                function(self.wp, self.env)
                ruleBasedEval = 1
        if not ruleBasedEval:
          self.wp.emit(self.env)
    self.fp.close()

  def processList(self, list=[]):
    self.emitter = ListEmitter(list)
    self.process()

