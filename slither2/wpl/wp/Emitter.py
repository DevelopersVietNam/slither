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


class Emitter:
  def __init__(self):
    pass

  def emit(self,text):
    print text,

  def getResult(self):
    return None

class ListEmitter(Emitter):
  def __init__(self, initList=[]):
    if type(initList) == type([]):
      self.output = initList
    else:
      self.output = []
    Emitter.__init__(self)

  def emit(self,text):
    self.output.append(text)

  def getList(self):
    return self.output

  def __repr__(self):
    rep = ''
    for text in self.output:
      rep = rep + text
    return rep

  def getResult(self):
    return self.getList()

class StringEmitter(Emitter):
  def __init__(self):
    self.text = ""
    Emitter.__init__(self)

  def emit(self, text):
    self.text = self.text + text

  def getText(self):
    return self.text

  def __repr__(self):
    return self.text

  def getResult(self):
    return self.getText()

def createEmitter(emitter):
  if emitter in ['Emitter','ListEmitter','StringEmitter']:
    stmt = 'return %s()' % (emitter)
    exec stmt
  else:
    return Emitter()
