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

import re

from wpl.wp.Emitter import Emitter, ListEmitter
from UserDict import UserDict

class Variable(UserDict):
  def __init__(self, dict):
    UserDict.__init__(self, dict)

  def __str__(self):
    rep = '<<'
    rep = rep + self['var']

    if self['format'] != None:
       rep = rep + '%' + self['format']
    if self['onfail'] != None:
       rep = rep + '|' + self['onfail']
    rep = rep + '>>'
    return rep
  
  __repr__ = __str__
    
class SimpleWriter:
  def __init__(self, emitter=Emitter()):
    #if hasattr(emitter, 'emit'):
    if isinstance(emitter, Emitter):
      self.emitter = emitter
    else:
      self.emitter = Emitter()
    self.wpPat = re.compile("""
         <<
          (?P<var>
            [A-Za-z_]
            [A-Za-z_0-9]*?
          )
          (?P<format>
            %
            .+?
          )?
          (?P<onfail>
	    [|]
            .*?
          )?
         >>
        """, re.VERBOSE
      )

    self.defaultEmitter = Emitter()
    self.rep = []
    self.varList = []

  def compile(self, line):
    self.rep = []
    self.varList = []
    pos = 0
    while 1:
      matched = self.wpPat.search(line, pos)
      if not matched: 
         self.rep.append(line[pos:])
         break
      var = matched.group('var')
      self.varList.append(var)
      textBefore = line[pos:matched.start()]
      self.rep.append(textBefore)
      matchedText = line[matched.start():matched.end()]
      self.rep.append(Variable(matched.groupdict()))
      pos = matched.end()
      
  def evaluate(self, evalEnv):
    # This is to play it safe. If performance suffers, I can eliminate
    # this statement.
    myEvalEnv = {}
    myEvalEnv.update(evalEnv)
    #myEvalEnv = evalEnv.copy()
    result = ''
    for expr in self.rep:
      if type(expr) == type(''):
        result = result + expr
      else:
        var = expr['var']

        format = expr.get('format', '%s')
        if not format:
           format = '%s'
        format = format[1:] 

        if expr['onfail'] != None:
           onfailValue = expr['onfail']
           onfailValue = onfailValue[1:]
        else:
           onfailValue = str(expr)

        deleteVar = 0
        if not myEvalEnv.has_key(var):
           deleteVar = 1 
           myEvalEnv[var] = onfailValue

        pySyntax = '%' '(' + var + ')' + format
        try:
           formattedText = pySyntax % myEvalEnv
        except:
           pySyntax = '%('+var+')s'
           try:
              formattedText = pySyntax % myEvalEnv
           except:
              convErrorMessage = '<b>Cannot convert ' + var + ' to string.</b>'
              formattedText = convErrorMessage
        result = result + formattedText

        if deleteVar:
           del(myEvalEnv[var])

    # Hopefully, this results in a GC. The copy should have a 0 RC.
    myEvalEnv = evalEnv
    return result
        
  def emit(self, evalEnv):
    text = self.evaluate(evalEnv)
    self.emitter.emit(text)

  def getRep(self):
    return self.rep

  def getVars(self):
    return self.varList

  def hasVar(self, var):
    return var in self.varList

  def __repr__(self):
    result = '<SimpleWriter>' + "\n"
    for r in self.rep:
      if type(r) == type(''):
         result = result + "  <text>" + r + "</text>\n"
      else:
         result = result + "  <var"
         for attr in r.keys():
            if r[attr] != None:
              result = result + " " + attr + "=" + '"' + r[attr] + '"'
         result = result + "/>\n"
    return result + "</SimpleWriter>"

