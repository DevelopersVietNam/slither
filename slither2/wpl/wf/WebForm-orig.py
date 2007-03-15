"""
<cvs>

<author>
  $Author: gkt $
</author>
<date>
  $Date: 2005/03/07 23:13:50 $
</date>
<id>
  $Id: WebForm-orig.py,v 1.1 2005/03/07 23:13:50 gkt Exp $
</id>
<synopsis>

WebForm is used to do web form processing. It handles much of the setup 
typically required and provides a much simpler CGI interface than the Python
"cgi" module. The documentation below explains in greater detail, and a 
tutorial is under development.
</synopsis>
</cvs>
"""

"""
<documentation type="module">
<synopis>
The WebForm class library is designed to allow web programs (so-called CGI
scripts) to be developed with a clear separation of concerns. CGI programming
is often characterized by a need to take input from forms, usually authored
in HTML and consisting of a number of 'input' variables (e.g. text fields,
text areas, checkboxes, selection lists, hidden variables), perform some
business logic, and then render HTML.

There are many similar approaches, such as Zope (gaining popularity) and
XML. However, these approaches suffer from much complexity. WebForm is unique
in that code generation is a completely separate concern from the actual
business logic. It is also well integrated with Python in making sure
exceptions are caught and reported (during development) to the web browser
window. This radically reduces cycle time of development, because it is a pain
to mill through those HTTP logs and figure out your errors, especially in a
live environment. (Syntax errors still resulted in the dreaded server error
messages. However, this will also be supported by a future update.)

At the core of WebForm is the WriteProcessor class library (which is part of
WebForm but is separately useful). This library allows you to perform
substitutions with a simple markup. You will want to take a look at that
library's documentation to understand how it works in detail. In summary,
WebForm allows you to process an entire file. Substitutions can be performed
on the various lines of the file against an environment. There are two types
of substitutions, both of which are very easy to understand:
   1. once substitutions - the line is processed once, and variables from
      the environment are substituted into a line.

   2. looping substitutions - the line is processed multiplet times by an
      implicit loop over a data structure.

The accompanying examples show how to make use of the looping substitutions,
which simply involve creating a dictionary data structure and creating a
descriptor for how the data in the dictionary is organized.
</synopsis>
</documentation>
"""

import os, string, os.path
import cgi, WriteProcessor, SimpleWriter, Emitter
import ConfigParser
import sys, traceback
import StringIO
import hwStackTrace
import smtplib
from Directory import Directory
from SimpleCookie import SimpleCookie

class WebForm:
    """
    <documentation type="class">
    <synopsis>
    WebForm is intended to be an abstract class. (There isn't much way in
    Python to enforce its use per se.) Thus it should not be instantiated
    directly. Instead a subclass should be created. Generally, the subclass
    only needs to do the following:
      1. Delegate initialization to this class from its __init__ method.
         This is very easily done as follows:
           WebForm.__init__(self, form, defaultVars, searchPath)
      2. Override the process() method with your customized business logic.
         Your business logic can assume that form data has been posted and
         any default bindings are initialized. There are a number of methods
         that can be called from within the process() method to do useful
         WebForm operations. These are discussed in the tutorial example.
      3. Optionally, override the addRules() method to specify looping style
         rules. You'll see in the tutorial that looping rules typically are
         used to fill in certain types of HTML elements, such as tables,
         selection lists, checkboxes, etc.

    </synopsis>
    
    <attribute name="formVars">
    The variables from 'input' tags defined in the form doing the POST. 
    </attribute>

    <attribute name="fileVars">
    The variables that correspond to uploaded files. Everyone will need to
    let me know if additional APIs are needed for the purpose of working with
    uploaded files. For now, you will be able to get the contents of the file
    without trouble, since the <xref module="cgi"/> module already addresses
    this consideration.
    </attribute>

    <attribute name="searchPath">
    Where to find any included files.
    </attribute>
      
    <attribute name="prefix">
    This is only used if you ask WebForm to bind all entries in
    formVars as variables. The binding process allows your business logic
    to make references such as 'self.[prefix][form-var] = ...' or
    '[var] = self.[prefix][form-var]' instead of having to refer to
    self.formVars[var] or self.getFormVar(var). Having the prefix makes
    it possible to minimize the likelihood of clobbering your object's
    namespace when the bindings are actually made. This particular
    attribute is initialized to the empty string. To override it, you
    can use the setPrefix() method in your overridden process() method.
    </attribute>
    </documentation>
    """
    
    def __init__(self, form, defaultVars={}, searchPath=["."], autoDispatch=1, **props):
        """
        <documentation type="constructor">
        <synopsis>
        Initialize the instance. As mentioned, you will not be creating
        instances of WebForm (nor should you). Instead, make a subclass
        and delegate initialization from your subclass' __init__ method.
        </synopsis>

        <param name="form">
        cgi.FieldStorage(), passed down upon initialization by the
        WebFormDispatcher class.
        </param>

        <param name="defaultVars">
        a set of variables that represent default values.
        These values come from a .conf file that matches the class name
        of the WebForm subclass. The WebFormDispatcher reads the .conf
        file and creates this for you automagically.
        </param>

        <param name="searchPath">
        list of directories to be searched for HTML (or any
        included file being referenced from within your HTML code). This
        is used by the WriteProcessor instance when generating code
        from the <xref class="WebForm" method="encode"/> method.
        </param>

        <param name="encodeTarget">
        The name of the HTML file to be used when generating code. This
        is initialized to None here but actually is initialized by
        the WebDispatcher when dynamically creating an instance of any
        WebForm subclass.
        </param>
        </documentation>
        """

        if props.has_key('config_dir'):
            self.config_dir = props['config_dir']
        else:
            self.config_dir = '.'


        self.form = form
        self.argv = sys.argv[:]
        confVars = self.parseConfFile()
        self.cookies = []
        cookie = self.loadCookie()
        if cookie != None:
            self.cookies.append(cookie)
            self.startingCookieCount = 1
        else:
            self.startingCookieCount = 0

        self.formVars = Directory({})
        self.formVars.update(defaultVars)
        self.formVars.update(confVars)
        self.hiddenVars = []
        self.fileVars = Directory({})
        self.searchPath = searchPath
        self.setContentStandard()

        self.extractFormVariables(form)
        self.encodeTarget = None
        self.prefix = ""
        self.autoDispatch = autoDispatch

    def extractFormVariables(self, form, depth=0):
        for var in form.keys():
            try:
               if type(form[var]) == type([]):
                  form_var = form[var][0]
               else:
                  form_var = form[var]

               if form_var.filename == None:
                  self.formVars[var] = form_var.value
               else:
                  VAR_DIR = '/%s' % var
                  self.fileVars[var] = (form_var.filename, form_var.file)
                  self.fileVars.create(var)
                  self.fileVars.cd(var)
                  self.fileVars['filename'] = form_var.filename
                  self.fileVars['file'] = form_var.file
                  self.fileVars.cd('/')

               if type(form[var]) == type([]):
                  VAR_DIR = '/%s' % var
                  self.formVars.create(var)
                  self.formVars.cd(var)
                  self.formVars[var] = []
                  varCount = 0
                  for form_var in form[var]:
                     if form_var.filename == None:
                        self.formVars["%s_%d"%(var,varCount)] = form_var.value
                        self.formVars[var].append(form_var.value)
                        varCount = varCount + 1
                  self.formVars.cd('/')
            except:
               raise "WebFormException", str(var) + "=" + str(form[var])


    def getFieldStorage(self):
        return self.form

    def parseConfFile(self):
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

    # This method (internal) loads a cookie from the environment.

    def loadCookie(self):
        if os.environ.has_key("HTTP_COOKIE"):
            try:
                cookie = SimpleCookie()
                cookie.load(os.environ["HTTP_COOKIE"])
            except CookieError:
                server = smtplib.SMTP('localhost')
                excf = StringIO.StringIO()
                traceback.print_exc(file=excf)
                server.sendmail('hwMail@hostway.com',['duffy@hostway.net'],\
                    "Subject: Cookies choked in WebForm processing!\n\n%s\nHTTP_COOKIE looks like:\n%s\n" % (excf.getvalue(), os.environ["HTTP_COOKIE"]))
                server.quit()
                return None

            if len(cookie.keys()):
               return cookie
            else:
               return None
        else:
            return None


    # This method tells you whether any cookies are present int the form.

    def hasCookies(self):
        return len(self.cookies) > 0

    # This method returns the list of cookies to a client.

    def getCookies(self):
        return self.cookies

    # This method allocates a cookie and links it onto the list of cookies.
    # It's basically a factory method.

    def getNewCookie(self):
        cookie = SimpleCookie()
        self.cookies.append(cookie)
        return cookie

    
    # This method will tell you whether any cookie can be found that matches
    # a list of vars. Matching occurs if all of the vars are found. An empty
    # To use this method, simply pass as many vars as you'd like to check.
    # e.g. matchCookie('user','key') as in Jason's examples.

    def matchOneCookie(self,*vars):
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

    def matchAllCookies(self, *vars):
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

    def setContentType(self,mimeTypeName):
        self.contentType = 'Content-type: ' + mimeTypeName + '\n\n'

    def setContentStandard(self):
        self.setContentType('text/html')

    def removeContentHeader(self):
        self.contentType = None

    def setSearchPath(self, searchPath):
        self.searchPath = searchPath

    def setPrefix(self,prefix):
        if type(prefix) == type(""):
            self.prefix = prefix

    # This method allows you to bind the form variables BY NAME and spare
    # yourself the agony of having to do self.var = form[var].value calls.
    # Here we also provide the ability to prepend a prefix to the variable
    # name. This method will NOT clobber any pre-existing binding in this
    # object (self).
    #
    # To make sure everyone understands what's going on here:
    # Suppose your form has some variables. Variables come from various
    # tags, such as <INPUT name="someVar" value="someValue">. After this
    # call, your Form instance (or subclass) will have self.someVar
    # (or self.<prefix>someVar) as an attribute.

    def bindVars(self, prefix=None):
        """
        <documentation type="method">
        <synopsis>
        This method will take all of the entries defined in
        <xref class="WebForm" attribute="formVars">formVars</xref> and
        make actual instance variables in the current object using
        Python's setattr() method. The name of the instance variable
        will be whatever is contained in <xref class="WebForm" attribute="prefix"/>
        followed by the actual name appearing in the 'input' tag from
        the form. As these variables are effectively 'cached' in the current
        object, the companion routine <xref class="WebForm" method="flushVars"/>
        must be called to ensure the variables are actually written through
        for the next form (usually needed for processing hidden variables).
        </synopsis>
        </documentation>
        """
        if not prefix:
            prefix = self.prefix
        for var in self.formVars.keys():
            if not self.__dict__.has_key(prefix + var):
                setattr(self,prefix + var,self.formVars[var])

    def flushVars(self, prefix=None):
        """
        <documentation type="method">
        <synopsis>
        This method writes all of the instance variables previously bound
        to the current object back to <xref class="WebForm" attribute="formVars"/>.
        Python's getattr() is used to find all such variables (as well as
        any new variables that may have been added by the
        <xref class="WebForm" method="addFormVar"/> method.
        </synopsis>
        </documentation>
        """
        if not prefix:
            prefix = self.prefix
        for var in self.formVars.keys():
            if self.__dict__.has_key(prefix + var):
                self.formVars[var] = getattr(self,prefix + var)

    def addVars(self, env):
        """
        <documentation type="method">
        <synopsis>
        This method allows you to take a dictionary of bindings and add them
        to <xref class="WebForm" attribute="formVars"/> This can be particularly
        useful for dumping the result of a database selection, a dynamically'
        generated list of options, etc.
        </synopsis>
        <param name="env">
        The dictionary of bindings.
        </param>
        </documentation>
        """

        for var in env.keys():
            self.formVars[var] = env[var]

    def addVar(self, name, value):
        """
        <documentation type="method">
        <synopsis>
        This method allows you to take a dictionary of bindings and add them
        to <xref class="WebForm" attribute="formVars"/> This can be particularly
        useful for dumping the result of a database selection, a dynamically'
        generated list of options, etc.
        </synopsis>
        <param name="env">
        The dictionary of bindings.
        </param>
        </documentation>
        """
        
        self.formVars[name] = value

    def markHidden(self,var):
        """
        <documentation type="method">
        <synopsis>
        This method allows you to take a dictionary of bindings and add them
        to <xref class="WebForm" attribute="formVars"/> This can be particularly
        useful for dumping the result of a database selection, a dynamically'
        generated list of options, etc.
        </synopsis>
        <param name="env">
        The dictionary of bindings.
        </param>
        </documentation>
        """

        if self.formVars.has_key(var):
            self.hiddenVars.append(var)
        
    def getFormVar(self, var):
        """
        <documentation type="method">
        <synopsis>
        This method allows you to take a dictionary of bindings and add them
        to <xref class="WebForm" attribute="formVars"/> This can be particularly
        useful for dumping the result of a database selection, a dynamically'
        generated list of options, etc.
        </synopsis>
        <param name="env">
        The dictionary of bindings.
        </param>
        </documentation>
        """
        
        if self.formVars.has_key(var):
            return self.formVars[var]
        else:
            return None
        
    def getFormVarDirectory(self):
        return self.formVars

    def getFileVarDirectory(self):
        return self.formVars

    def getFileName(self, var):
        try:
            VAR_DIR = '/%s' % var
            self.fileVars.cd(var)
            fileName = self.fileVars['filename']
            self.fileVars.cd('/')
            return fileName
        except:
            return None
        
    def getFileHandle(self, var):
        try:
            VAR_DIR = '/%s' % var
            self.fileVars.cd(var)
            fileHandle = self.fileVars['file']
            self.fileVars.cd('/')
            return fileHandle
        except:
            return None
        
    def process(self):
        """
        <documentation type="method">
        <synopsis>
        This method is effectively an NOP. Your subclass should override
        this method to do some useful business logic, such as querying the
        database, defining variables to fill in dynamically generated
        elements, etc.
        </synopsis>
        </documentation>
        """
        pass

    def setEncodeFileName(self, fileName):
        """
        <documentation type="method">
        <synopsis>
        This allows you to change what web page is going to come up next.
        It is usually a reference to an HTML file, although it does not
        have to be, since WebForm always makes sure to generate a content
        HTML header when doing code generation.
        </synopsis>
        <param name="fileName">
        The top-level file to be used for doing code generation
        </param>
        </documentation>
        """
        
        self.encodeTarget = fileName

    def encode(self, emitStrategy=Emitter.Emitter(), text=None):
        """
        <documentation type="method">
        <synopsis>
        Generate the code after the business logic from your subclass'
        <xref class="WebForm" method="process"/> method is executed.
        </synopsis>
        <param name="additionalVars">
        Any last-minute bindings you wish to establish. Generally, you
        should use the methods <xref class="WebForm" method="addFormVar"/>
        and <xref class="WebForm" method="addFormVars"/> to make additional
        bindings from within your subclass'
        <xref class="WebForm" method="process"/> method.
        </param>
        </documentation>
        """

        # Check whether the strategy was specified by name
        # Construct object of that type if possible.
        # If not, use StringEmitter.
        
        if type(emitStrategy) == type(''):
            emitStrategy = Emitter.createEmitter(emitStrategy)

        # If the emitStarategy is not a proper subclass of Emitter,
        # replace with a StringEmitter instance.
        
        if not isinstance(emitStrategy, Emitter.Emitter):
            emitStrategy = Emitter.Emitter()

        
        newEnv = self.formVars.copy()

        #for var in additionalVars.keys():
        #   newEnv[var] = additionalVar[var]
        if self.encodeTarget != None:
            if self.autoDispatch:
               # If there were incoming cookies, we only write
               # the *new* cookies. self.startingCookieCount can only
               # be 0 or 1, based on the condition in __init__().

               for cookie in self.cookies[self.startingCookieCount:]:
                  emitStrategy.emit(`cookie` + '\n')

               # Content goes next.
               if self.contentType:
                  emitStrategy.emit(self.contentType)
     
            # Emit any "initial" text (i.e. stuff to be prepended, usually
            # from stray print statements in the process() method.

            if text:
               emitStrategy.emit(text)

            # This is the actual content, i.e. rendering of the page.

            wp = WriteProcessor.WriteProcessor(self.encodeTarget, \
                                               self.searchPath, newEnv, \
                                               emitStrategy)
            self.addRules(wp)
            wp.process()
        # else:
        #   should probably encode to standard output by default...  
        return emitStrategy.getResult()

    def addFormVarRule(self,wp):
        """
        <documentation type="method">
        <synopsis>
        This rule allows you to generate a nice looking table of all
        variables defined in the WebForm. Should your subclass provide
        its own rules, using the <xref class="WebForm" method="addRules"/>
        method, it will be necessary to call this method explicitly or
        the <xref class="WebForm" method="addDefaultVars"/> method.
        </synopsis>
        <param name="wp">
        The WriteProcessor instance being used for code generation (supplied
        by the <xref class="WebForm" method="encode"> method, which is called
        immediately after the <xref class="WebForm" method="process"> method.
        </param>
        </documentation>
        """
        
        env = {}
        for var in self.formVars.keys():
            varName = cgi.escape(var)
            varValue = self.formVars[varName]
            varType = type(varValue)
            varType = cgi.escape(`varType`)
            varValue = cgi.escape(`varValue`)
            env[varName] = (varType,varValue)
        if len(env) == 0:
            env['N/A'] = ('N/A','N/A')
        wp.addLoopingRule('WebForm_VarName',\
                          '(WebForm_VarType, WebForm_VarValue)', env)

    def addHiddenVarRule(self,wp):
        """
        <documentation type="method">
        <synopsis>
        This rule allows you to add all hidden variables (easily) to the
        next WebForm. Should your subclass provide
        its own rules, using the <xref class="WebForm" method="addRules"/>
        method, it will be necessary to call this method explicitly or
        the <xref class="WebForm" method="addDefaultVars"/> method.
        </synopsis>

        </documentation>
        """
        
        env = {}
        for var in self.hiddenVars:
            env[var] = self.formVars[var]
        if len(env) == 0:
            env['N/A'] = 'N/A'
        wp.addLoopingRule('WebForm_HiddenVarName','WebForm_HiddenVarValue',\
                          env)

    def addDefaultRules(self,wp):
        """
        <documentation type="method">
        <synopsis>
        This will add rules for emitting hidden variables easily and
        dumping all variables for the purpose of debugging. This is
        equivalent to calling both
        <xref class="WebForm" method="addHiddenVarRule"/> and
        <xref class="WebForm" method="addFormVarRule"/>. The same comments
        apply when you override the
        <xref class="WebForm" method="addRules"/> method.
        
        </synopsis>
        <param name="wp">
        The WriteProcessor object being used, which is supplied automatically
        for you.
        </param>
        </documentation>
        """
        
        self.addFormVarRule(wp)
        self.addHiddenVarRule(wp)
        
    def addRules(self,wp):
        """
        <documentation type="method">
        <synopsis>
        Subclasses will override this method to supply their own rules.
        When overriding this method, the
        <xref class="WebForm" method="addDefaultRules"> method should be
        called to establish some useful default rules that are designed
        to facilitate debugging and propagation of hidden variables.
        </synopsis>
        <param name="wp">
        The WriteProcessor object being used, which is supplied automatically
        for you.
        </param>
        </documentation>
        """
        
        self.addDefaultRules(wp)



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
    
    def __init__(self,searchPath,formId=None,contentType="text/html"):
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
        <param name="searchPath">
        where to find included (HTML) files/fragments
        </param>
        <param name="formId">
        the form to be loaded. Typically, this will simply be the 'name'
        of the program, which is sys.args[0].
        </param>
        <param name="contentType">
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
        statement = statement + '(form,formDefaults,searchPath)'
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
        
        _form_.setEncodeFileName(formId + '.html')

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
        
        try:
            stdout = sys.stdout
            sys.stdout = out = StringIO.StringIO()
            _form_.process()
            sys.stdout = stdout
        except:
	    sys.stdout = stdout
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
