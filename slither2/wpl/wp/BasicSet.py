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

class BasicSet:

   def __init__(self, L=[]):
      self.resetData(L)

   def resetData(self, L):
      self.rep = []
      for elem in L:
         self.insert(elem)

   def insert(self, elem):
      if elem not in self.rep:
         self.rep.append(elem)

   def remove(self, elem):
      if elem in self.rep:
         self.rep.remove(elem)

   def union(self, another):
      if isinstance(self, BasicSet):
         L = self.rep
      else:
         L = another
      unionSet = BasicSet(self.rep)
      for elem in L:
         unionSet.insert(elem)
      return unionSet

   def intersect(self, another):
      if isinstance(self, BasicSet):
         L = self.rep
      else:
         L = another
      interSet = BasicSet(self.rep)
      for elem in interSet.rep:
         if elem not in L:
            interSet.remove(elem)
      return interSet

   def equals(self, other):
      if len(self.rep) != len(other.rep):
         return 0
      for elem in self.rep:
         if elem not in other.rep:
            return 0
      return 1

   def sortRep(self):
      self.rep.sort()

   def __str__(self):
      self.sortRep()
      return 'Set:' + str(self.rep)

   def __repr__(self):
      return str(self)
