"""

        Number Game is an example Slither based application.
        This file part of the Number Game.
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

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
        IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
        FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE
        LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
        BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
        BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
        LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
        SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""


from State import State
from Exceptions import StageProcessException
import random

class PickNumber( State ):

    # The code here is pretty intuitive:
    # 1. Get the random_number from the form (it's a hidden variable)
    # 2. If any conversion error occurs--raise an exception and re-render
    #    this state's form.
    # 3. If the number and random_number match, user got it right. So
    #    schedule the Congratulations state!
    # 4. Otherwise, compute whether the user needs to guess higher or lower
    #    We use a StageProcessException page to indicate that the page
    #    must be rendered again. (Personally, we should think about this
    #    and the need to be able to re-enter a state.) This does work 
    #    elegantly though.

    def process( self ):
        try:
           random_number = int(self.Request['random_number'])
           number = int(self.Request['number'])
        except:
           self.Response['what_to_do'] = 'Illegal Value Encountered; only a numeric value is permitted!'
           raise StageProcessException(self.render())

        if number == random_number:
           self.scheduleState( "/Congratulations.render" )
        else:
           if (number < random_number):
              self.Response['what_to_do'] = 'Your guess was too low. Try higher!'
           else:
              self.Response['what_to_do'] = 'Your guess was too high. Try lower.'
              
           raise StageProcessException(self.render())


    # This first test case must mix some business logic in the rendering
    # This would probably go away if we added another state.

    def render( self ):
        if not self.Request.has_key('random_number'):
            self.Response['random_number'] = random.randint(1,100)
        else:
            self.Response['random_number' ] = self.Request['random_number']

        #self.set_encode_file_name('PickNumber.html')
        return self.encode('PickNumber.html')

    def MyRender( self ):
        return self.render()

    def _my_private( self ):
        return self.render()
