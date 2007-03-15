"""
        wpl.wf is a library file used to wrap the cgi module with
        a large set of additional features. 
        This file part of the wpl.wf.WebForm library.
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

import os, string, os.path, cgi
import sys, traceback
import StringIO
import ConfigParser


from wpl.wp import WriteProcessor, SimpleWriter
from wpl.wp.Emitter import Emitter, createEmitter
from wpl.directory.Directory import Directory
from wpl.wf.SimpleCookie import SimpleCookie

class WebForm:
    """
    The WebForm class. It is expected that any class wanting to use the
    WebForm pattern will be a subclass. Many of its benefits come from
    interaction with the instance's namespace.
    """
    
    def __init__(self, form, another_web_form=None, **props):
        """
        Construction has become quite a bit different in this release of
        WebForm. Instead of having so many parameters to the constructor,
        keyword parameters are now used, which is equivalent to a property
        based system.

           form - required - an instance of cgi.FieldStorage(). 
           another_web_form - another instance may be used for initialization
             Note: This results in shallow (not deep) cloning and the form
             storage is thus shared.

        The following properties are available:
           default_vars - A directory containing some default variables. These
              are typically "seed" values that are to be treated as form 
              variables. For example, if you are expecting an input 'username',
              you can put it in a dictionary of defaults. This value would be
              assigned to 'username', if 'username' is not found in the 
              form.
 
           search_path - A list of directories to search for HTML. By default
              search_path = ['.'], the current working directory.
             
           content_type - None | 'text/html' | 'text/plain' | 'other valid enc'
              If content_type is set to None, no content header is emitted.

           read_cookies = 'yes' | 'no' | None
              Use cookies. 'yes' means to use them, 'no' means don't use them.
              None may be used instead of 'no'; 'yes' by default

           write_cookies = 'yes' | 'no' | None
              This determines whether cookies should be emitted. By default,
	      'no'.

           emit_strategy = object (instance of Emitter only)

           stdout = Where to send standard output. The only option is to 
              specify sys.stderr, a StringIO object, or a file. By default
              output to sys.stdout goes to a string I/O object.
           
           config_dir - where to find the configuration file. By default,
              the 'config_dir' == '.', the current working directory.

           read_config_file = 'yes' | 'no'

           bind = prefix | None. 'm_' is the default value. To use this
              feature, we require that the prefix end in '_', to avoid
              conflicts with any attribute in the object. Setting bind
              to None will not setattr.

        """

        self.stdout_capture = StringIO.StringIO()

        default_props = {
           'default_vars' : {},
           'search_path' : ['.'],
           'content_type' : 'text/html',
           'write_content_type' : 'yes',
           'read_cookies' : 'yes',
           'write_cookies' : 'yes',
           'emit_strategy' : Emitter(),
           'stdout' : self.stdout_capture,
           'config_dir' : '.',
           'read_config_file' : 'yes',
           'prefix' : 'm_', 
           'encode_target' : None
        }
  

        self.form = form

        # Cloning takes place here.

	if another_web_form != None:
           for prop_name in default_props.keys():
               prop_value = getattr(another_web_form, prop_name)
               props[prop_name] = prop_value
        else:
           for prop_name in default_props.keys():
               if not props.has_key(prop_name):
                  props[prop_name] = default_props[prop_name]

        for prop_name in default_props.keys():
            check_method_name = 'check_%s' % prop_name
            if hasattr(self, check_method_name):
               check_method = getattr(self, check_method_name)
               new_value = check_method(props[prop_name], default_props[prop_name])
               setattr(self, prop_name, new_value)
               #print "prop name = %s"%( prop_name )

        if self.read_config_file == 'yes':
           conf_vars = self.__parse_config_file()
        else:
           conf_vars = {}

        self.cookies = []
        if self.read_cookies == 'yes':
           cookie = self.__load_cookie()
           if cookie != None:
               self.cookies.append(cookie)
               self.startingCookieCount = 1
           else:
               self.startingCookieCount = 0

        self.form_vars = Directory({})
        self.form_vars.update(self.default_vars)
        self.form_vars.update(conf_vars)
        self.file_vars = Directory({})
        self.set_content_standard()

        self.__create_directories(form)


        self.__encode_count = 0

    def check_default_vars(self, current_value, default_value):
        if type(current_value) != {}:
           return default_value
        return current_value

    def check_search_path(self, current_value, default_value):
        if type(current_value) != type([]):
           return default_value
        return current_value

    def check_content_type(self, current_value, default_value):
        if not current_value in ['text/html', 'text/plain', None]:
           return default_value
        return current_value

    def check_write_content_type(self, current_value, default_value):
        if not current_value in ['yes', 'no', None]:
           return default_value
        return current_value

    def check_read_cookies(self, current_value, default_value):
        if current_value not in ['yes','no', None ]:
           return default_value
        else:
           return current_value

    def check_write_cookies(self, current_value, default_value):
        if current_value not in ['yes','no', None ]:
           return default_value
        else:
           return current_value

    def check_emit_strategy(self, current_value, default_value):
        #print current_value.__class__
        #print default_value.__class__
        if isinstance(current_value, Emitter):
           return current_value
        return default_value

    def check_stdout(self, current_value, default_value):
        if isinstance(current_value, StringIO.StringIO): 
           return current_value
        elif current_value in [sys.stderr]:
           return current_value
        return default_value
           

    def check_config_dir(self, current_value, default_value):
        if type(current_value) != type(''):
           return default_value
        else:
           return current_value

    def check_read_config_file(self, current_value, default_value):
        if current_value in ['yes','no']:
           return current_value
        else:
           return default_value

    def check_prefix(self, current_value, default_value):
        if type(current_value) == '' and current_value[-1] == '_':
           return current_value
        elif current_value == None:
           return current_value
        return default_value


    def check_encode_target( self, current_value, default_value ):
        # NOTE: Not sure what to check for here as this is allowed
        #       to be None until later defined. For now we simply return
        #       the current_value.
        return current_value



    def __create_directories(self, form, depth=0):
        for var in form.keys():
            try:
               if type(form[var]) == type([]):
                  form_var = form[var][0]
               else:
                  form_var = form[var]

               if form_var.filename == None:
                  self.form_vars[var] = form_var.value
               else:
                  VAR_DIR = '/%s' % var
                  self.file_vars[var] = (form_var.filename, form_var.file)
                  self.file_vars.create(var)
                  self.file_vars.cd(var)
                  self.file_vars['filename'] = form_var.filename
                  self.file_vars['file'] = form_var.file
                  self.file_vars.cd('/')

               if type(form[var]) == type([]):
                  VAR_DIR = '/%s' % var
                  self.form_vars.create(var)
                  self.form_vars.cd(var)
                  self.form_vars[var] = []
                  varCount = 0
                  for form_var in form[var]:
                     if form_var.filename == None:
                        self.form_vars["%s_%d"%(var,varCount)] = form_var.value
                        self.form_vars[var].append(form_var.value)
                        varCount = varCount + 1
                  self.form_vars.cd('/')
            except:
               raise "WebFormException", str(var) + "=" + str(form[var])


    def set_emit_strategy( self, strategy ):
        """ Update the emit strategy to a new strategy. """

        #print "STRAT: %s"%( isinstance( strategy, StringEmitter ) )
        setattr( self, 'emit_strategy', self.check_emit_strategy( strategy, self.emit_strategy  ) )


    def get_field_storage(self):
        return self.form

    def __parse_config_file(self):
        # Now load the configuration file for the form. Every form is required
        # to have one--no exceptions. This allows you to supply (for example)
        # default values for variables. The WebForm class will actually
        # register every variable appearing here as an actual attribute of
        # the WebForm subclass instance.
        formDefaults = {}
        
        try:
            formId = self.__class__.__name__
            configFile = self.config_dir + '/' + formId + '.conf'
            confParser = ConfigParser.ConfigParser()
            confParser.read( configFile )
            optionList = confParser.options(formId)

            try:
                optionList.remove('__name__')
            except:
                pass
            
            for option in optionList:
                optionValue = confParser.get(formId, option)
                formDefaults[option] = optionValue
        except:
            # If any problem occurs in the ConfigParser, we are going to
            # return whatever we were able to get.
            pass
        return formDefaults

    def __load_cookie(self):
        if os.environ.has_key("HTTP_COOKIE"):
            cookie = SimpleCookie()
            cookie.load(os.environ["HTTP_COOKIE"])

            if len(cookie.keys()):
               return cookie
            else:
               return None
        else:
            return None


    # This method tells you whether any cookies are present int the form.

    def has_cookies(self):
        return len(self.cookies) > 0

    # This method returns the list of cookies to a client.

    def get_cookies(self):
        return self.cookies

    # This method allocates a cookie and links it onto the list of cookies.
    # It's basically a factory method.

    def get_new_cookie(self):
        cookie = SimpleCookie()
        self.cookies.append(cookie)
        return cookie

    
    # This method will tell you whether any cookie can be found that matches
    # a list of vars. Matching occurs if all of the vars are found. An empty
    # To use this method, simply pass as many vars as you'd like to check.
    # e.g. matchCookie('user','key') as in Jason's examples.

    def match_one_cookie(self,*vars):
        if len(vars) < 1: return None
        for cookie in self.cookies:
           matched = 1
           for var in vars:
               if not cookie.has_key(var):
                  matched = 0
                  break
           if matched:
               return cookie
        return None

    def match_all_cookies(self, *vars):
        if len(vars) < 1: return None
        L=[]
        for cookie in self.cookies:
           matched = 1
           for var in vars:
               if not cookie.has_key(var):
                  matched = 0
                  break
           if matched:
               L.append(cookie)
        return L

    def set_content_type(self,mimeTypeName):
        self.content_type = mimeTypeName

    def set_content_standard(self):
        self.set_content_type('text/html')

    def removeContentHeader(self):
        self.content_type = None

    def set_search_path(self, search_path):
        self.search_path = search_path

    def __bind_vars(self):
        """
        Set attributes from self.form_vars in this object.
        """
        prefix = self.prefix
        for var in self.form_vars.keys():
            if not self.__dict__.has_key(prefix + var):
                setattr(self,prefix + var,self.form_vars[var])

    def __flush_vars(self):
        """
        Take any variables beginning with the bind prefix and write them
        out to the form variables.
        """
        prefix = self.prefix
        for var in self.form_vars.keys():
            if self.__dict__.has_key(prefix + var):
                self.form_vars[var] = getattr(self,prefix + var)

    def add_vars(self, env):
        """
        Add a dictionary of variables to self.form_vars.
        """

        for var in env.keys():
            self.form_vars[var] = env[var]

    def add_var(self, name, value):
        """
        Add a single binding between 'name' and 'value' to self.form_vars.
        """
        
        self.form_vars[name] = value

    def get_file_name(self, var):
        """
        Uploaded files get entries written in to the self.file_vars directory.
        Given 'var', go to its directory and get the 'filename' attribute,
        which returns the file name of the uploaded file as supplied by the
        user.
        """
        try:
            VAR_DIR = '/%s' % var
            self.file_vars.cd(var)
            fileName = self.file_vars['filename']
            self.file_vars.cd('/')
            return fileName
        except:
            return None
        
    def get_file_handle(self, var):
        """
        Using this method gets the file handle of the file uploaded by the 
        user so it can be read.
        """
        try:
            VAR_DIR = '/%s' % var
            self.file_vars.cd(var)
            fileHandle = self.file_vars['file']
            self.file_vars.cd('/')
            return fileHandle
        except:
            return None
        
    def process(self):
        """
        Abstract method
        """
        raise "WebForm requires subclass to implement the process() method"

    def set_encode_file_name(self, fileName):
        """
        Set the filename to be encoded via the encode() method. This filename
        should correspond to a text file, possibly containing WriteProcessor
        variables.
        """
        
        self.encode_target = fileName


    def get_encode_count( self ):
        """ Accessor method used to track the number of times
        that the encode method was called. """

        return self.__encode_count



    def encode(self, prepend_text=''):
        """
        Process the form. 
        """
        emitter = self.emit_strategy

        newEnv = self.form_vars.copy()

        # If 'write_cookies' was enabled, emit the cookies. Otherwise, toss
        # the cookies. (Just had to say that.)
        if self.write_cookies == 'yes':
           for cookie in self.cookies[self.startingCookieCount:]:
              emitter.emit(`cookie` + '\n')

        # If 'write_content_type' is 'yes', emit the content type header.
        if self.write_content_type == 'yes':
           emitter.emit('Content-Type: ' + self.content_type + '\n\n')
     
        # If any initial text was passed, emit it. By default, 'prepend_text'
        # is set to the empty string, meaning nothing is to be prepended.
        emitter.emit(prepend_text)

        # Now, call the WriteProcessor. In order for this to work, a valid
        # 'encode_target' must have been passed to WebForm (or via the
        # set_encode_target() method call.
        if self.encode_target != None:
            wpc = WriteProcessor.WriteProcessor
            wp = wpc(self.encode_target, self.search_path, newEnv, emitter)
            wp.process()

        # Finally, return the result.

        self.__encode_count = self.__encode_count + 1

        return emitter.getResult()


errorText = """
<html>
  <head>
    <title>WebForm Processing Error</title>
  </head>

  <body>
    <h1>WebForm Error in Processing</h1>
     <p>An error has been encountered in processing a form.</p>
     <p><<WebForm_Error>></p>
  </body>
</html>
"""

def error(form, message, emitContentHeader=1):
    """
    documentation type="function">
    <synopsis>
    This is used to guarantee that any error that occurs when dispatching a
    form results in valid HTML being generated. It also guarantees that a
    meaningful message will also be displayed.
    </synopis>
    <param name="form">
    The cgi.FieldStorage() object containing all form variables.
    </param>
    <param name="message">
    A human-comprehensible message that describes what happened
    and (in the future) how to resolve the problem.
    </param>
    </documentation>
    """
    
    env = {}
    env['WebForm_Error'] = message

    if emitContentHeader:
       print 'Content-type: text/html\n\n'
    wp = SimpleWriter.SimpleWriter()
    wp.compile(errorText)
    print wp.evaluate(env)

def getWebFormDispatcher(args,htmlSearchPath):
    """
    <documentation type="function">
    <synopsis>
    To use the WebForm system, your main method need only contain a call to
    skeleton dispatcher with the command line arguments.
    </synopsis>
    </documentation>
    """

    # args[0] always contains the name of the program. This should be
    # the name of your form. Basically, each class must be contained in
    # a file that matches the class name. So if your WebForm subclass is
    # 'class OrderPizza(WebForm)', it should be in a file named OrderPizza*.
    #
    
    programName = args[0]

    # Allow for the (real) possibility that the program name might be
    # invoked as a full path or whatever. This would probably break if
    # we ran on Apache Winhose, but since Hostway would never do such
    # a cheesy thing on the server side, I am not going to worry about
    # this hypothetical possibility that "/" isn't the separator.
    
    pathParts = string.split(programName,"/")

    # The last token after "/" is the complete file name.
    realName = pathParts[-1]
    
    mainNameParts = string.split(realName,".")
    # Get rid of the .py or .whatever.
    className = mainNameParts[0]

    # Run, Forrest, Run!
    WebFormDispatcher(htmlSearchPath, className, className)


class WebFormDispatcher:
    """
    <documentation type="class">
    <synopsis>
    A singleton class (i.e. only one instance should be created) that
    is used to dynamically dispatch and execute user defined WebForm
    objects. This class dynamically executes code to import a user-defined
    class (from a module having the same name). The instance is created and
    then processed (using the <xref class="WebForm" method="process"/>) and
    encoded (the part that renders the next HTML form, using
    the <xref class="WebForm" method="encode"/> method.
    </synopsis>
    </documentation>
    """
    
    def __init__(self,search_path,formId=None,content_type="text/html"):
        """
        <documentation type="class">
        <synopsis>
        All of the work is done in the constructor, since this class is
        intended for use as a singleton. That is, an instance is created,
        it does its thing, and then it is not used further. A CGI script
        simply creates this instance in its main method (or as its only
        statement) and that is all there is to it. See the examples for
        how to automate the setup of this class. It is very slick, and very
        easy.
        </synopsis>
        <param name="search_path">
        where to find included (HTML) files/fragments
        </param>
        <param name="formId">
        the form to be loaded. Typically, this will simply be the 'name'
        of the program, which is sys.args[0].
        </param>
        <param name="content_type">
        Generally, leave this alone. We'll need to think a little bit about
        how to get out of the box to generate something non-HTML, such as a
        ZIP file or whatever. This should not be a problem to extend. It
        will probably require us to change some things in the WebForm class.
        </param>
        </documentation>
        """

        # First get all of the data that was defined in the form. The CGI
        # module of Python does this, albeit in a crappy way, since it does
        # not pass the values of 'inputs' that were left blank, for example.
        #
        # We need to peek at the variables to determine what form is to
        # be loaded. The 'input' named WebForm_FormId is reserved for this
        # purpose.
        
	form = cgi.FieldStorage()

        try:
            if not formId:
                formId = form['WebForm_FormId'].value
	except:
            error(form,"Hidden 'WebForm_FormId' variable not defined")
            return

        # This could be deleted but some existing apps could break. I have
        # decided to put the .conf logic into the WebForm class itself.
        
        formDefaults = {}

        # Import the module (form) dynamically. We will swtich to __import__
        # soon, since it has the convenient property of giving a namespace
        # reference.

        __namespace__ = __import__(formId)

        # Dynamically create the form instance. At the end of this, __form__
        # is a reference to the form object.
        
        statement = '_form_ = __namespace__.' + formId
        statement = statement + '(form,formDefaults,search_path)'
        try:
            exec statement
        except:
            error(form,"could not execute " + statement)
            print "<pre>"
            traceback.print_exc(None,sys.stdout)
            print "</pre>"
            return

        # Set (by default) the template for generating HTML output code to
        # be the same name as the form followed by '.html'. This can be
        # changed by the form's process() method.
        
        _form_.set_encode_file_name(formId + '.html')

        #
        # Call the form's business logic (process) method. This method (as
        # mentioned in the WebForm documentation) is to be overridden to
        # actually get your business logic wired in.
        #
        #
        # If an exception occurs during this process, it is sent to the
        # standard output (which, coincidentally is dup'd to the output
        # stream associated with the socket held by the HTTP server. This
        # means (happily) that any run time error a la Python is going to
        # be seen in the browser window
        #
        # GKT Note: We want to do two things here.
        # 1. Provide the option for printing a generic message and showing
        #    no traceback (useful during deployment--don't want customers
        #    to see tracebacks for sure!)
        # 2. Support integration with the hwMail package and logging server
        #    that we are (or hope to be) working on. Flat file logging would
        #    also be VERY nice.
        #

        # Redirection of 'stdout' may take place.

        save_stdout = sys.stdout
        
        try:
            #sys.stdout = self.stdout
            sys.stdout = self.stdout_capture
            _form_.process()
            sys.stdout = save_stdout
        except:
            # XYZ: John, perhaps we can integrate with 'trace' module here.
            # I also want to have in-lined error pages but can do this later.
	    sys.stdout = save_stdout
            error(form,"Exception encountered in business logic [process()]")
            outText = out.getvalue()
            print "<pre>"
            traceback.print_exc(None,sys.stdout)
            print "</pre>"
            print "<h1> output intercepted from process() method </h1>"
            if len(outText) > 0:
               print outText
            return

        #
        # Final Code Generation. It is unlikely an exception will be thrown
        # in here. If one does happen, it is impossible to guarantee that the
        # exception is propagated to the browser. Assuming that the cookies
        # being emitted are well formed (a pretty reasonable assumption), the
        # exception should be processed normally.
        #
        try:
            outText = out.getvalue()
            if len(outText) > 0:
               _form_.encode(text=outText)
            else:
               _form_.encode()
        except:
            error(form,"Exception encountered in HTML generation [encode()]")
            print "<pre>"
            traceback.print_exc(None,sys.stdout)            
            print "<pre>"
            return

        # And that's all she wrote! :-) Sorry, pun TRULY not intended.
