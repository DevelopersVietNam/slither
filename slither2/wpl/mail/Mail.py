"""
        wpl.mail is a library file used to send e-mail from a Python application.
        This file part of the wpl.mail.Mail library.
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

Module
======
hwMail


Synopsis
========
hwMail is reposnisible fore reading a configuration file for various
sendmail initialization parmaters. The config file is also used
to identify various e-mail groups. Users can use the sendMail and
sendIndividualMail functions to send an e-mail either to a defined
group or an individual e-mail addres respectively.

Successful transmission of e-mails results in the method returning
a 1. If errors occur, exceptions are caught and reviewed. If the exception
is a non fatal SMTP exception (dropped socket, corrupted stream, etc.)
an attempt is made to resend the message. This is done until a maximum
number of attempts is reached. If the exception is fatal, but still
SMTP related, the send method called will return a 0. Otherwise, the
the exception is considered fatal and the user (callign applciation)
will be held responsible for dealing with the problem.

Each activity of the module is loged to a file. The log file
carries the configuration file name as a prefix and '.log' as the
extenson. Certain messages are marked with a standard label. This is
done to aid in searching for records within the log. Furute log modules
will be able to interface to these lables and perform simple queries
and statistics.


Usage
=====
hwMail was designed to provide a robust mechanism for delivering
e-mail notifications. It is guranteed not to raise any exceptions
even in cases where the SMTP server is unaccessible.

If you intend to send e-mail notifications in your applciation, you will
need to:

1) Import the hwMail module:

   import hwMail

2) Include a mail configuration file in an accassabledirectory
   (typically the directory where your source application lives).
   An example file is included at the end of these notes.

3) (optional) Run the testConfig() method in the interpreter.
   testConfig() will attempt to check your configuration file for
   syntax errors and will send an e-mail to a provided e-mail address
   to check the SMTP configuration.

4) In your applciation, instantitate the hwMail object:

   hwm = hwMail( '/dir/to/config.file', 'true' )
   
   The second paramter will ensure that logging is turned on. To turn
   off logging, set the second paramter to 'false'.

5) When a need arises to send e-mail, simply call the sendMail(...) functions:

   hwm.sendMail( 'config_file_group', 'subject', 'the message' )
   
   hwMail will take care of oppening the SMTP connection, delivering the mail,
   and tracking any failures. In the event that an error occurs, it will be
   logged in the log file. No exceptions will be thrown once the hwMail
   object has been instantiated.
   
   Optionally, you can use hwMail to send an e-mail to a single address
   that is supplied within your source code (and NOT from the configuration
   file):
   
   hwm.sendIndividualMail( 'e-mail address', 'subject', 'message' )
   
   This is useful for sending e-mail to non technical people. For example,
   a billing applciation may want to deliver a statement to a user account.
   This can be performed by calling the sendIndividualMail(...) method within
   a loop.

   Another variation on the sendIndividualMail is the use of a from address. The
   following statement will cause e-mail to be sent to a user from a specified 
   e-mail address (normally the from address is obtained from the mail conf file).

   hwm.sendExtendedIndividualMail( 'from address' , 'to address', 'subject', 'message' )

   If your code already packs the appropriate header fields (namely From: , To:, Subject: )
   you may use the sendRawMail function as follows:

   hwm.sendRawMail( 'email addr', 'well formed message', from_addr='from e-mail address' ) 

   NOTE: in the second form, the email address will default to an empty string.
   It is expected that the To: filed is properly formed in the body message body.

   This method will not check the message for well formed fields. If you decide
   to use this method, make sure to test your applciation before going live.

   You may need to send a batch of e-mail to a list of address and cc/bcc addresses.
   You can use the following method to do just that:

   hwm.sendBatchMail( 'from_address', [ to_list ], subject, message, cc_list=[], bcc_list=[] )

   The to_list, cc_list, and bcc_lists are expected to be Python lsits. If they are not,
   an error results (logged in the appropriate log file) andno mail is sent resutling
   in the value 0 being returned. Also, the cc and bcc lists are optional. If noting is
   included or an empty list is provided no cc or bcc information will be added to
   the email header.


6) Optionally, you may need to queue several e-mail to be sent at a later time, or
   to be compile dinto a single e-mail that will be sent to a specified group
   of recepeients. Queuing is performed in two stages:
   1) E-mails are queued using the queueMail(...) method as follows:

      hwm.queueMail( <list of or individual e-mail address>, <subject>, <message body> )

   2) At a certain point, the e-mail queue is flushed using the method flushQueue(...)
      as shown by the following:
      
      hwm.flushQueue()                                         or
      hwm.flushQueue( <group defined in conf file> )           or
      hwm.flushQueue( <group defined in conf file> , 'true' )

   In the first step, you use an interface similar to sendIndividualMail(...) to
   queue the e-mail messages. Then the e-mail message is flushed in one of three ways.
   Calling flushQueue() without any parmaters will cause the queued messages to be
   sent to their original recepients (specified when the mail was queued). Optionally,
   you can pass a conf. file specified group name to flushQueue. This will cause the
   method to compile all of the queued message sinto a single mail message that will
   be sent to all recepients specified under the group in the conf file. The last form
   od flushQueue will take an optional string 'true' to flush the queue even if
   there are one or more errors when an attempt was made to send the e-mail.

   flushQueue() will return either 0 or 1 if the operation failed on one or more
   messages or completely succeeded, respectively. To identify the failed deliveries,
   you must review the mail log.


7) There is now support for error recovery. Based on the configuration file, heMail
   will save the email with failed delivery results to an internal queue. You can then
   use the public flush method to try and send the e-mail next time around.

   To take advantage of this feature, you must add the following line to the server
   configuration section of the configuration file:

   queue_failed_sends=true

   This instructs heMail to create a *.error-q file that contins a queue
   of error messages. The next time that you load your app or at any point
   you may attempt to resend the failed messages by performing a flush on the
   queue as shown below:

   hwm.flushErrorQueue()

   Another attempt is made to send the e-mail. If this attempt fails as well,
   the e-mails are queued up again. You can use an option paramter to force
   the queue to be flushed even if the second attempt fails as shown below:

   hwm.flushErrorQueue( 'true' )


Limitations
===========

The ConfigParser class used requries Python interpreter 1.5.2 or newer.



Example Configuration File
==========================

The following is a configuration file. You may want to copy and
paste the text into a new file so that you are starting off with
a well formed file.

BEGIN OF FILE >>>>>>>>>

# hwMail - example configuration file.
#
# hwMail uses the standard Python ConfigParser class
# to interpret configuration files. This configuration
# file is an example of a config file that would result
# in no errors when used by hwMail.
#
# Sections are defined using a pair of brackets '[]'. Each
# section can have zero or more options. Options are defined
# at property=value pairs. For example, opt1=value1 is a 
# valid definition. You can optionally seperate the property value
# pair with a colon as in the following: opt1: value1. Either case
# will result in the definition of a new property named opt1 that 
# has a value value1. No options can exist outside of a heading!
#
# The smtp section is the only required sections. All other sections
# are user defined. The only options that hwMail understands are
# user=e-mail address types. For example, JohnShafaee=pshafaee@hostway.net
# is an option that hwMail will use to e-mail John Shafaee. You can
# create custom sections and list varying e-mail address of people based
# on the section name. For example, below you will see the developer section.
# Under the developer section you will list all user=e-mail address that 
# you want hwMail to e-mail when that group name is used. All user=e-mail
# options listed under the DEFAULT section will be used on every call to
# hwMail's sendMail method.
#
# All lines beginning with '#' or ';' will be considered
# comment lines and are ignored by hwMail. Please read the
# comments above each section to learn more about the options
# available.
#


[DEFAULT]
pshafae=pshafae@yahoo.com


# REQUIRED SECTION
# host=<domain name of host where the desired SMTP server is runing>
# from_addr=<address that should appear in FROM field of all e-mails>
[smtp]
host=localhost
from_addr=cctrans@hostway.net


[developer]
JohnShafaee=pshafaee@hostway.net



<<<<<<<<<< END OF FILE



Author Info
===========
John Shafaee (pshafaee@hostway.net)
Jason Duffy  (duffy@hostway.net)

Contributions by:
George K. Thiruvathukal (george@hostway.net)


Date: July 28, 2000 (of first write, v. 0.1)
Version 1.6

"""




# Log tracking codes; used
# to quickly identify messages

SUCCESS      = '(S100)SUCCESS'
RESOLVED     = '(S200)RESOLVED'
ERROR        = '(E100)ERROR'
FATAL_ERROR  = '(E900)FATAL ERROR'
UNK_ERROR    = '(E200)UNKNOWN ERROR'
WARNING      = '(W100)WARNING'


FALSE         = 'false'
TRUE          = 'true'
FLUSH_SUBJECT = 'hwMail Queued E-Mail Flush'


# Standard module imports
import smtplib
import ConfigParser
import time
import socket
import signal
import string
import sys
import cPickle
import os.path

# Non-standard import
from hwStackTrace import hwStackTrace




class timeoutException:

    """ Used to return process to
    the end of a try block after a
    timeout signal
    """
    
    def __init__( self, value ):
        self.value = value

    def __str__( self ):
        return `self.value`




class fatalTimeoutException:

    """ Used to return process to
    the end of a try block after a
    timeout signal
    """
    
    def __init__( self, value ):
        self.value = value

    def __str__( self ):
        return `self.value`


class hwMail:

    # Config file constants
    server_sec = 'smtp'
    server_host = 'host'
    server_port = 'port'
    from_addr = 'from_addr'
    timeout = 'timeout'
    max_timeouts = 'max_timeouts'
    max_num_attempts = 'max_num_attempts'
    save_errors = 'queue_failed_sends'
    

    def __init__( self, configFile, verbose ):
        
        # Create a log file if versbose mode not diabled
        self.logFile = 0
        if verbose != 'false':
            self.logFile = open( configFile + ".log" , 'a' )
            
        # Process the config file
        self.confParser = ConfigParser.ConfigParser()
        self.confParser.read( configFile )
        self.writeLog( "Config file '" + configFile + "' sucessfully read." )

        # Check for essential conf entries
        self.checkConfEntry( self.server_sec, self.server_host )
        self.checkConfEntry( self.server_sec, self.from_addr )
        self.checkConfEntry( self.server_sec, self.timeout )
        self.checkConfEntry( self.server_sec, self.max_timeouts )
        self.checkConfEntry( self.server_sec, self.max_num_attempts )        

        # set the error recovery fields (this is optional so it does not rely on
        # checking the conf entry )
        try:
            self.SAVE_ERROR = self.confParser.get( self.server_sec, self.save_errors )
            self.writeLog( "Under [" + self.server_sec + "] , " + self.save_errors + "=" + self.SAVE_ERROR )
        except ConfigParser.NoOptionError , detail :
            self.writeLog( WARNING + " No option '" + self.save_errors + "' defined under [" + self.server_sec + "]" )
            self.writeLog( SUCCESS + " Turining OFF errored email recovery." )
            self.SAVE_ERROR = FALSE
            
        
        # Set internal variables        
        self.numTimeouts = 0
        self.mailQueue = []
        self.errorQueueFile = configFile + ".error-q" 

        self.MAX_NUM_ATTEMPTS = int( self.confParser.get( self.server_sec, self.max_num_attempts ) )
        self.MAX_TIMEOUTS = int( self.confParser.get( self.server_sec, self.max_timeouts ) )
        self.TIMEOUT = int( self.confParser.get( self.server_sec, self.timeout ) )
        self.FLUSH_IN_PROGRESS = 0


        # Initialize the smtp server
        self.smtpServer = smtplib.SMTP() 
        self.writeLog( "Module loaded and READY." )
        




    def sendMail( self, group , subject, message ):

        try:
            # Build a list of all emails under the section
            groupList = self.confParser.options( group )

            if len( groupList ) == 1 :
                self.writeLog( WARNING + " No email addresses listed under [" + group + "] or [DEFAULT]" )
                raise smtplib.SMTPException
            else:
                #addrList = ""
                eList = [] # used to remove duplicate entries
                for emailId in groupList:
                    addr = self.confParser.get( group, emailId )
                    addr = string.strip( addr )
                    if emailId != '__name__' and addr not in eList:
                        #addrList = addrList + addr + ","
                        eList.append( addr )

                # send the e-mail
                for emailAddress in eList:
                    #DEBUG
                    #print "Mailing to: ", emailAddress
                    self.send_mail( emailAddress, subject, message )                

                return 1
                
        except ConfigParser.NoOptionError :
            self.writeLog( ERROR + " Option list under [" + str(group) + "] is malformed;  following message NOT SENT >>>>\n" + str(message) + "\n<<<<" )
            return 0

        except ConfigParser.NoSectionError :
            self.writeLog( ERROR + " Email group [" + str(group) + "] not defined; following message NOT SENT >>>>\n" + str(message) + "\n<<<<" )
            return 0
        
        except smtplib.SMTPException:
            self.writeLog( FATAL_ERROR + " One or more fatal errors blocked sending of any e-mail with message >>>>\n" + str(message) + "\n<<<<" )
            return 0
        
        except:
            self.writeLog( UNK_ERROR + " One or more fatal errors blocked sending of any e-mail with message >>>>\n" + str(message) + "\n<<<<" )
            return 0



    def sendIndividualMail( self, email, subject, message ):
        try:
            self.send_mail( email, subject, message )

            return 1

        except smtplib.SMTPException:
            self.writeLog( FATAL_ERROR + " One or more fatal errors blocked sending of any e-mail from sendIndividulaMail(...) with message >>>>\n" + str(message) + "\n<<<<" )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return 0
        except:
            self.writeLog( UNK_ERROR + " One or more fatal errors blocked sending of any e-mail with message >>>>\n" + str(message) + "\n<<<<" )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return 0



    def sendExtendedIndividualMail( self, from_address, email, subject, message ):
        try:
            self.send_mail( email, subject, message, from_addr=from_address )

            return 1

        except smtplib.SMTPException:
            self.writeLog( FATAL_ERROR + " One or more fatal errors blocked sending of any e-mail from sendIndividulaMail(...) (using from address) with message >>>>\n" + str(message) + "\n<<<<" )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return 0
        except:
            self.writeLog( UNK_ERROR + " One or more fatal errors blocked sending of any e-mail with message >>>>\n" + str(message) + "\n<<<<" )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return 0



    def sendBatchMail( self, from_address, to_list, subject, message, cc_list=[], bcc_list=[], xheader=None ):
        """ Provides a means for doing batch sending
        of emails. """

        # require that all to, cc, and bcc are real python lists
        if type( to_list ) != type( [] )    \
           or type( cc_list ) != type( [] ) \
           or type( bcc_list ) != type( [] ):
            self.writeLog( FATA_ERROR + "hwMail.sendBatchMail used it to, cc, or bcc args that are not Python lists. No email sent." )
            return 0


        # create the cc string
        to_str = ''
        for addr in to_list:
            to_str = to_str + addr + ", "

        # remove the last comma
        if to_str != '':
            to_str = to_str[:-2]        

        # create the cc string
        cc_str = ''
        for addr in cc_list:
            cc_str = cc_str + addr + ", "

        # remove the last comma
        if cc_str != '':
            cc_str = cc_str[:-2]
        
        # combine the lists into a real to list
        to_list = to_list + cc_list + bcc_list


        try:
            # send the mail
            self.send_mail( to_list, subject, message, justCompile=FALSE, from_addr=from_address, to_string=to_str, cc_string=cc_str, xheader=xheader )

            return 1

        except smtplib.SMTPException:
            self.writeLog( FATAL_ERROR + " One or more fatal errors blocked sending of any e-mail from sendBatchMail(...) with message >>>>\n" + str(message) + "\n<<<<" )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return 0
        except:
            self.writeLog( UNK_ERROR + " One or more fatal errors blocked sending of any e-mail with message >>>>\n" + str(message) + "\n<<<<" )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return 0




    def sendRawMail( self, recepient , message ):
        try:
            self.send_mail( recepient, None, message )

            return 1

        except smtplib.SMTPException:
            self.writeLog( FATAL_ERROR + " One or more fatal errors blocked sending of any e-mail from sendRawMail(...)[two parameter] with message >>>>\n" + message + "\n<<<<" )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return 0
        
        except:
            self.writeLog( UNK_ERROR + " One or more fatal errors blocked sending of any e-mail with message >>>>\n" + message + "\n<<<<" )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return 0




    def queueMail( self, recepient, subject , message ):
	""" Queue mail in a dictionary. Programmer may then flush
        the queue. This is convenietn for combining/consolidating
        reports into a single e-mail, or queue e-mail to be sent at
        asynchrouneously from the mail compilations. Recepients CANNOT
        be conf file group names.
        """

        # Check if we are given a single e-mail address
        if type( recepient ) == type("string"):
            recepient = [ recepient ]

        # Compile the message, but don't send it
        msg = self.send_mail( recepient, subject, message, TRUE )
        
        # Create mail tuple
        mailTuple = ( recepient , msg )

        # Queue the mail
        self.mailQueue.append( mailTuple )




    def flushQueue( self, group=None, forceFlush=FALSE ):
        """ Flush the e-mail queue to their defined destination
        or compile all to a single e-mail to be sent to new
        destination defined in group. New destination must be a
        group that exists in the conf file."""

        result = 0

        # Get some statistics on the report to be compiled
        numQueuedMails = len( self.mailQueue )
        
        if group != None and numQueuedMails > 0:
            # compile the mails into a single e-mail
            msg = "This e-mail contains '%d' e-mail messages queued by hwMail that have been re-directed to this account.\n\n"%(numQueuedMails)
            msg = msg + "---- E-MAILS ----\n\n"

            i = 0
            for emailTuple in self.mailQueue:
                for email in emailTuple[0]:
                    i = i + 1
                    msg = msg + "Message %d of %d\n"%( i , numQueuedMails )
                    msg = msg + "================\n"
                    msg = msg + "To: " + email + "\n"
                    msg = msg +  emailTuple[1] + "\n\n"

            # Send the e-mail to the recepeint group
            result = self.sendMail( group , FLUSH_SUBJECT, msg )

        else:
            # send the e-mails to their respective recepeients
            numEmails = 0
            for emailTuple in self.mailQueue:
                for email in emailTuple[0]:
                    result = result + self.sendRawMail( email , emailTuple[1] )
                    numEmails = numEmails + 1

            if result != numEmails:
                result =  0
            else:
                result = 1


        # If we successed in sending ALL of the e-mails,
        # flush the queue. Otherwise flush if it is forced.
        if result != 0 or forceFlush == TRUE:
            self.mailQueue = []


        return result


    def getMailQueue( self ):        
        return self.mailQueue
    


    def loadMailQueue( self, mailQueue, action="JOIN" ):
        if action == "JOIN":
            self.mailQueue = self.mailQueue + mailQueue
            return 1
        elif action == "REPLACE":
            self.mailQueue = mailQueue
            return 1            
        else:
            return 0



    def load_error_queue( self, errorQueueFile ):
        """ Internal method for loading and retuning an
        error queue; should nto be called outside of the
        class. """

        try:

            errorQueue = []
            if os.path.isfile( errorQueueFile  ):
                eqFile = open( errorQueueFile , "r" )                
                errorQueue = cPickle.load( eqFile )
                eqFile.close()

            return errorQueue
            
        except:
            self.writeLog( WARNING + "while loading error queue file '%s'."%( self.errorQueueFile ) )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return None
            


    def save_error_queue( self, errorQueueFile, errorQueue ):
        """Internal method for saving a queue to a file. Should
        not be called outside the method. """

        try:
            eqFile = open( errorQueueFile , "w" )
            cPickle.dump( errorQueue, eqFile )
            eqFile.close

            self.writeLog( "errorQueue = %s"%( errorQueue ) )

            self.writeLog( SUCCESS + " Saved error queue with '%d' stored e-mails to file."% ( len( errorQueue ) ) )

            return 1
        except:
            self.writeLog( WARNING + " Error occured while saving error queue file '%s'."%( self.errorQueueFile ) )
            self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
            return 0



    def addToErrorQueue( self, email_tuple ):
        """ Saves all the information needed to send an e-mail
        if a failure occured during the first send. """

        if self.SAVE_ERROR != TRUE:
            return 0

        # load the queue
        errorQueue =  self.load_error_queue( self.errorQueueFile  )

        if self.FLUSH_IN_PROGRESS != 0 :
            self.writeLog( SUCCESS + " In flush mode; error not added to queue." )
        elif errorQueue != None:           
            # add the message to the queue
            errorQueue.append( email_tuple )           

            self.writeLog( SUCCESS + " Added mail to error queue; another attempt will be made on the next error queue flush." )
        
            # pickle the queue file and close
            self.save_error_queue( self.errorQueueFile, errorQueue )
            
            return 1
        else:
            self.writeLog( WARNING + " No error added to error queue due to I/O exceptions." )
            return 0



    def flushErrorQueue( self, forceFlush=FALSE ):
        """ Attempts to send teh errored email. If attempts
        fail, and forceFlush is set to YES, then clears the
        queue regardless of the new attempt. """

        savedErrorQueue = []
        errorQueue =  self.load_error_queue( self.errorQueueFile  )
        
        if errorQueue != None:

            self.FLUSH_IN_PROGRESS = 1
            for email_tuple in errorQueue:
                
                # try to send the email
                ( from_addr, addrList, message ) = email_tuple

                result = 0
                try:
                    result = self.send_mail( addrList, None, message )
                except smtplib.SMTPException:
                    self.writeLog( FATAL_ERROR + " One or more fatal errors blocked sending of any e-mail from flushErrorQueue(...) with message >>>>\n" + str(message) + "\n<<<<" )
                    self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
                    result = 0
                except:
                    self.writeLog( UNK_ERROR + " One or more fatal errors blocked sending of any e-mail with message >>>>\n" + str(message) + "\n<<<<" )
                    self.writeLog( "STACK TRACE -> %s"%( hwStackTrace() ) )
                    result = 0

                
                if result == 1:
                    self.writeLog( SUCCESS + " Sent mail to '%s' from the error queue."%( addrList ) ) 
                elif forceFlush != FALSE:
                    # remove from the list
                    self.writeLog( WARNING + " Could NOT send mail in error queue to '%s'; Force flush requested, removing mail from error queue."%( addrList ) )
                else:
                    self.writeLog( ERROR + " Could not send mail in the error queue; will retry on next load." )
                    savedErrorQueue.append( email_tuple )

            self.save_error_queue( self.errorQueueFile, savedErrorQueue )
            self.FLUSH_IN_PROGRESS = 0

            return 1
        else:
            self.writeLog( WARNING + " Could not use the error queue due to I/O problems." )
            self.FLUSH_IN_PROGRESS = 0
            return 0




    def send_mail( self, addrList, subject, message, justCompile=FALSE, from_addr=None, to_string=None, cc_string=None, xheader=None ):
        
        # Add subject header to message
        #if subject != '':
        #    message = "Subject: " + subject + "\n\n" + message

        # Check to see if we are just compiling the message
        if justCompile != FALSE:
            return message


        # Attempt to send message by throtteling.
        # This is necessary to avoid conenction failures caused
        # by smtplib.

        self.numTimeouts = 0
        numAttempt = 0
        sent       = 0

        while sent == 0:
            try:
                #DEBUG
                #self.writeLog( "Entering loop." )

                # Create a connection to the SMTP server
                self.smtpServer.connect( self.confParser.get( self.server_sec, self.server_host ) )

                # DEBUG
                #self.writeLog( "Setting alarm." )
                
                # Set a timer
                signal.signal( signal.SIGALRM, self.timeOutHandler )
                signal.alarm( self.TIMEOUT )

                # DEBUG
                #self.writeLog( "Sending mail." )

                # set the from address if provided
                if from_addr == None:
                    from_addr = self.confParser.get( self.server_sec, self.from_addr )


                # create the propper string rep. of the to list
                if to_string == None or to_string == '':
                    if type( addrList ) == type( [] ):
                        to_string = ''
                        for addr in addrList:
                            to_string = to_string + str( addr ) + ", "

                        # remove the last comma
                        if to_string != '':
                            to_string = to_string[:-2]

                    else:
                        to_string = addrList


                # create cheader string
                xheader_string = ''
                if xheader != None and type(xheader) == type({}):
                    for key in xheader.keys():
                        xheader_string = "%s: %s\n"%( key , xheader[ key ] )  + xheader_string

                    # remove trailing new-line
                    xheader_string = xheader_string[:-1]

                    # add a new line at the head
                    xheader_string = "\n" + xheader_string


                # Edit message to provide sender's To: address
                if subject == None:
                    # this is a raw e-mail, do nothing
                    pass
                elif cc_string == None or cc_string == '':
                    message = "From: %s\nTo: %s\nSubject: %s%s\n\n%s"%( from_addr, to_string, subject, xheader_string, message )
                else:
                    message = "From: %s\nTo: %s\nCc: %s\nSubject: %s%s\n\n%s"%( from_addr, to_string, cc_string, subject, xheader_string, message )


                #self.writeLog( "message -> %s" %( message ) )


                # Send the e-mail
                resultDict = self.smtpServer.sendmail( from_addr, addrList, message )

                #DEBUG
                #self.writeLog( "Resetting alarm after success." )
                
                # Reset the alarm
                signal.alarm( 0 )

                # Check if we did not send mail cleanly
                if numAttempt > 0 or self.numTimeouts > 0:
                    self.writeLog( RESOLVED + " exception on attempt '%d'; mail sent to: %s" %(numAttempt, addrList) )
                else:
                    self.writeLog( SUCCESS + " successfully sent mail to: %s" %(addrList) )
        
                # If any e-mail was undilivered
                for key in resultDict.keys():
                    self.writeLog( WARNING + " Recepient '" + str( resultDict[ key ] ) + "' did not receive an e-mail!" )


                self.smtpServer.quit()
                sent = 1

                #DEBUG
                #self.writeLog( "Quit server and set sent to %d" %(sent) )


            except timeoutException :
                signal.alarm( 0 )
                self.writeLog( WARNING + " timeout occured on attempt '%d' to address '%s'. Trying to send again." %(self.numTimeouts, str(addrList)) )
                

            except :
                # We catch all exceptions that are raised. If the exception is
                # well known (par tof the list in the if clause below) then the
                # the error is bubbled up to the calling method. Otherwise,
                # we attempt to send the mail up the maximum attempt count.
                
                
                signal.alarm( 0 )

                self.writeLog( ERROR + " exception '%s' with value '%s' occured while sending mail." %(sys.exc_info()[0] , sys.exc_info()[1] ) )

                self.writeLog( "Stack trace -> " + hwStackTrace() )

                if sys.exc_info()[0] not in [ fatalTimeoutException, smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused, smtplib.SMTPDataError ]:
                    
                    numAttempt = numAttempt + 1
                    
                    self.writeLog( WARNING + " failed to send on error attempt no. '%d' to address '%s'." %(numAttempt, str(addrList)) )

                    # If we tried this three time, it is going to fails
                    if numAttempt == self.MAX_NUM_ATTEMPTS:
                        self.writeLog( FATAL_ERROR + " after making '%d' attempts to send mail to address '%s'; mail NOT sent." %(numAttempt, addrList) )

                        self.addToErrorQueue( [ from_addr, addrList, message ] )
                        
                        self.smtpServer.quit()                        
                        raise

                    # Sleep a time exponential to 
                    time.sleep( 2 + numAttempt*3 )

                else:
                    self.addToErrorQueue( [ from_addr, addrList, message ] )
                    
                    self.writeLog( FATAL_ERROR + " exception '%s' with value '%s' while sending mail to address '%s'; mail NOT sent." %( sys.exc_info()[0], sys.exc_info()[1], str(addrList) ) ) 
                    self.smtpServer.quit()
                    raise




    def timeOutHandler( self, signal, stackFrame ):
        """ Method handles processor time outs. """

        if self.numTimeouts == self.MAX_TIMEOUTS :
            self.writeLog( FATAL_ERROR + " timeout occured after '" + str( self.TIMEOUT ) + "' seconds; mail NOT sent." )
            
            self.smtpServer.quit()
            raise fatalTimeoutException, FATAL_ERROR + " Timeout occured after waiting '" + str( self.TIMEOUT ) + "' seconds. Mail not sent."

        else:
            # DEBUG
            #self.writeLog( "Quiting server." )
            
            self.smtpServer.quit()
            self.numTimeouts = self.numTimeouts + 1
            raise timeoutException( "Timeout has occured." )





    def writeLog( self, message ):
        try: 
            # If logging is turned on, write to file
            if self.logFile != 0 :
                currentTime = time.asctime( time.localtime( time.time() )) 
                self.logFile.write( currentTime + " : " + message + "\n" )
                self.logFile.flush()
        except error :
            # If an I/O error occurs, write something to the stdandard
            # error stream.
            sys.stderr.write( FATAL_ERROR + " hwMail could not write to log file!\n \
            Error -> " + str( error ) + "\nMessage to be written:\n" + message )


            

    def checkConfEntry( self, sec, opt ):
        try:
            value = self.confParser.get( sec, opt )
            self.writeLog( "Under [" + sec + "] , " + opt + "=" + value )
        except ConfigParser.NoOptionError , detail :
            self.writeLog( FATAL_ERROR + " No option '" + opt + "' defined under [" + sec + "]" )
            #print str( detail )
            raise
        except ConfigParser.NoSectionError , detail :
            self.writeLog( FATAL_ERROR + " Section [" + sec + "] not defined" )
            #print str( detail )
            raise




    def __del__( self ):
        if self.logFile !=0 :
            self.logFile.close()





def testConfig( configFile, testEmailAddress, testGroup  ):
    print "\n***** Begin of hwMail test ******\n"

    try:
        print "Instantiating hwMail object with configuration file '" + configFile + "'",
        hwm = hwMail( configFile, "true" )
        print "\t[  OK  ]"

        print "\nSending test e-mail to '" + testEmailAddress + "'..."
        print "Return result: ", hwm.sendIndividualMail( testEmailAddress, "Testing hwMail Individual" , "hwMail individual is alive!" )

        print "\nSending test e-mail to group '" + testGroup + "'..."
        print "Return result: ", hwm.sendMail( testGroup, "Testing hwMail Group" , "hwMail group is alive!" )

        print "\nQueueing some e-mails..."
        hwm.queueMail( testEmailAddress, "Testing hwMail Queue 1", "A queued message!" )
        hwm.queueMail( testEmailAddress, "Testing hwMail Queue 2", "Another queued message!" )
        hwm.queueMail( testEmailAddress, "Testing hwMail Queue 3", "Another queued message!\nThis time with a new line in the message." )

        print "Flushing e-mails to the test address..."
        hwm.flushQueue( "developer"  )

        print "\nQueuing some e-mails..."
        hwm.queueMail( testEmailAddress, "Testing hwMail Queue 1", "A queued message!" )
        hwm.queueMail( testEmailAddress, "Testing hwMail Queue 2", "Another queued message!" )
        hwm.queueMail( testEmailAddress, "Testing hwMail Queue 3", "Another queued message!\nThis time with a new line in the message." )
        
        print "Flushing e-mails to respective addresses..."
        hwm.flushQueue()


        print "\nQueueing some more e-mail..."
        hwm.queueMail( testEmailAddress, "Testing hwMail SAVED Queue 1", "A queued message!" )
        hwm.queueMail( testEmailAddress, "Testing hwMail SAVED Queue 2", "Another queued message!" )
        hwm.queueMail( testEmailAddress, "Testing hwMail SAVED Queue 3", "Another queued message!\nThis time with a new line in the message." )        

        print "Obtaining the queue via getMailQueue() call..."
        q = hwm.getMailQueue()

        print "Saving queue to a file..."
        qFile = open( "savedMailQueue.hwm" , "w" )
        cPickle.dump( q , qFile )
        qFile.close()

        print "Creating a new hwMail object..."
        hwm2 = hwMail( configFile, "true" )

        print "Loading the saved mail queue..."
        qFile = open(  "savedMailQueue.hwm" , "r" )
        q = cPickle.load( qFile )
        result = hwm2.loadMailQueue( q )

        print "Flushing the mail queue..."
        hwm2.flushQueue( "developer" )


        print "\nTesting batch send of e-mails..."
        xheaders = { 'X-Mailer' : 'hwMail', 'X-Magic' : 'blue'  }
        result = hwm.sendBatchMail( 'pshafae@localhost', [ 'pshafae@localhost' , 'pshafaee@hostway.net' ], 'Testing Batch' , 'Batch is workinf...yeah!' , [ 'duffy@hostway.com' ], [ 'jas@friendmail.net' ], xheaders )
        print "Result = ", result
        
        
        print "\nReview '" + configFile + ".log' for any errors."        


    except (ConfigParser.MissingSectionHeaderError, ConfigParser.NoOptionError, ConfigParser.NoSectionError ),detail :
        print "\t[FAILED]"
        print "DETAILS -> " + str( detail )
        


    print "\n***** End of hwMail test ******\n"






def dufftest():
    hwm = hwMail("mail.conf", 'y')
    
    try:
        i = 0
        while i < 1000:
            result = hwm.sendRawMail("pshafae@localhost","""From: pshafae@localhost
To: pshafae@localhost
Subject: STRESS TEST hwMail

This is stress testing the hwMail v. 1.0 module.
""" )

            #pirnt "Result = " , str( result )
            i = i + 1
            
    except:
        print "Exception occurred after send '%d' messages." %(i)
        raise





if __name__ == '__main__':
    #
    # Replace 'mail.conf' with any other desired
    # configuration file name. Also, replace
    # 'pshafae@localhost' with an e-mail address
    # that you know has no problems receiving e-mail.
    #
    testConfig( "mail.conf" , "pshafaee@shrike.depaul.edu", "developer" )

    #dufftest()



