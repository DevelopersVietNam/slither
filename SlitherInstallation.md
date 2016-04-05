# Introduction #

Slither is a web framework that was presented as part of our book, Web Programming in Python, which has recently gone out of print. We still get a number of inquiries from folks who like the idea of a web framework that can be run within a standard Apache Web Server setup. This guide aims to help you get your first Slither application up and running as quickly/painlessly as possible.

# Disclaimer #

While Slither continues to be a reliable code base and is actually used in some production applications, the code itself and this tutorial are provided _as is_. We would be interested in working with developers to continue development but as of this writing there are no plans to continue evolving Slither. Please contact the developers if you have an interest in helping us out and participating in a possible next-generation effort.

# Prerequisities #

Before continuing, please make sure you set up Apache Web Server on your system. We do not cover the installation of Apache here in any kind of detail. (It's at best at 30,000 ft. view.)

For the purpose of this tutorial, please enable the following capabilities in your Apache setup:

  * User directory support: This allows you to access pages such as `http://<host-or-IP>/~<your-username>/page.html` from a `public_html` directory.
  * CGI Scripts: The ExecCGI option should be enabled on your user directory or its cgi-bin.
  * Set UID on Execution (suexec): In general, you should enable scripts so they will run as your uid/gid (primary) when a CGI script executes in your user directory. You do **not** want to run your scripts as the superuser (i.e. root).

We only support Unix-style operating systems officially. This includes operating systems such as Linux, OS X, and Solaris--platforms on which Slither is known to run. In particular, if you want to run Slither on Windows, you should not read the rest of this tutorial--unless, of course, you are porting Slither to Windows and want to help us write new instructions! ;-) We are not opposed to Microsoft but have not tested any of our work on Windows and its many variants.

You must also have Subversion support installed. In particular, you need access to the **svn** command. Most modern Linux distributions either have it installed already or can add it easily.

We recommend anyone who is new to Linux and wants to try out Slither to install [Ubuntu Linux](http://www.ubuntu.com), which is among the more usable and manageable Linux distros out there.

# Let's get started #

Ok, enough of the preliminaries.

Let's make sure your Apache setup is ready to rock-n-roll. We also need to make sure you really can run Subversion, which is absolutely necessary to work through this tutorial.

Let's grab some very quick "test" scripts to see whether we can run CGI scripts properly on your Apache Web Server setup.
```
svn checkout http://slither.googlecode.com/svn/trunk/aws
```

You can perform this checkout anywhere you like. I suggest you do it in your public\_html or cgi-bin directory (or wherever you plan to install Slither). Again for the purpose of getting going quickly, let's assume you are doing this in your user directory (public\_html or public\_html/cgi-bin). Your configuration may vary but try not to be too weird, unless you can't help yourself.

```
cp aws/sanity.py ~/public_html
```

or

```
cp aws/sanity.py ~/public_html/cgi-bin
```

Now you need to make sure the permissions are correct on the script:
```
chmod 755 sanity.py
```

You might also need to rename the script to sanity.cgi, if you are requiring a particular extension (i.e. using cgi\_handler with a '.cgi' or other extenion).

Anyway, you also need to make sure your home directory, public\_html, and/or cgi-bin are also at a minimum having the right permissions for you/group to access it. I recommend just doing this:
```
chmod 711 ~
chmod 711 ~/public_html
chmod 711 ~/public_html/cgi-bin
```

Now you will want to take your web browser (running on your system or on another system) to test your setup. Try `http://<host-or-IP>/~<your-username>/sanity.py` or `http://<host-or-IP>/~<username>/cgi-bin/sanity.py` (or replace .py with .cgi). You should see output similar to the following:

```
hostname: xenon
 
whoami: george
```

Of course, you would see the hostname (ServerName) associated with your Apache setup and hopefully your username here. If you don't see your username and see **apache** or something else (other than **root**) you might be ok but will likely need to make sure the "other" permissions include "x" when trying to run any script.

# On to Slither #

Assuming you are able to run a CGI script as described in the preceding section, we're now ready to move on to Slither itself.

Let's grab the code for the Slither web framework itself. You should make sure you're in the `public_html` or `cgi-bin` directory.
```
svn checkout http://slither.googlecode.com/svn/trunk/slither2
```

Let's also go ahead and grab the code for the Slither sample projects:
```
svn checkout http://slither.googlecode.com/svn/trunk/slither2_projects
```

If all has gone well, you'll see two subdirectories in your current working directory: `slither2` and `slither2_projects`, which contain the framework code and sample application, respectively. Please do not continue if you are not seeing these directories. It means--more than likely--that you are lacking proper Subversion support.

# Configuring Slither #

We'll begin by configuring Slither itself. Change to the `slither2` directory. There are two important files that need to be renamed and edited:

  * DriverConf.py.in: The main configuration file for Slither.
  * pythonpathrc.in: A list of directories to be searched for framework and application-specific library code

```
cp DriverConf.py.in DriverConf.py
cp pythonpathrc.in pythonpathrc
```

At this point, you could try running Slither. Of course, it probably would not work, because the configuration files don't contain the right information to search for libraries, let alone the sample application (Number Game) itself.

Here is a sample `DriverConf.py` configuration for my setup:
```
#
# Driver specific configuration
#

LOG_FILE_NAME = '/home/gkt/public_html/slither2/logs/Driver'
PATH_FILE = '/home/gkt/public_html/slither2/pythonpathrc'

#
#
#

# slither projects webroot
sp_webroot = '/home/gkt/public_html/slither2_projects'


NumberGame = {
'webroot' : '%s/NumberGame'%( sp_webroot ),
'project_module' : 'NumberGame',
'project_class' : 'NumberGame',
}

projects = {
'NumberGame' : NumberGame
}
```

In the above, you must replace `/home/gkt/public_html` with the full path to the **parent** directory of your `slither2` and `slither2_projects` directories. Ordinarily, this will be `/home/<username>/public_html` or `/home/<username>/public_html/cgi-bin`. (It can be anything, as long as your Apache Web Server configuration allows.)

Slither takes advantage (for the most part) of the use of "Python as the configuration language". The first two variable definitions are explained below:

  * LOG\_FILE\_NAME: Where to write the logs. The trailing component is the _prefix_ to be used for naming the log file itself. In the above example, the logs will be written to directory `/home/gkt/public_html/slither2/logs`. The log filename itself will be prefixed with `Driver`. In Slither, there are separate log streams for events associated with the framework code vs. application-specific logging. (We'll cover the latter shortly in _Configuring the Number Game_ section.)
  * PATH\_FILE: A list of directories (one per line) that will be searched for application code and any other desired/needed Python libraries.

The remainder of the configuration file will work _as is_. For the curious, however, here is a brief explanation of what is going on:

  * Each application that you plan to run within Slither simply needs to have some metadata (a descriptor, a Python dictionary), which is then stored in a the `projects` dictionary. The descriptor tells where to find the application code (webroot), the project main module (project\_module) and the project's main class (project\_class).
  * the `projects` dictionary is required in this file. Without it, the main driver for Slither will assume there are no applications to be run.

Here is what you should have (minimally) in your `pythonpathrc` file:
```
/home/gkt/public_html
/home/gkt/public_html/slither2
```

Again you will need to replace `/home/gkt/public_html` with the appropriate path to reach your `slither2` directory.

Note that it is not necessary to include `slither2_projects` (the path to it) in this file, because the driver configuration is used to configure the applications you want (and add them dynamically to the python path.)

Finally, you need to make sure the logs directory is writable by the user/group Apache is running as:
```
mkdir slither2/logs
chmod 775 slither2/logs
```

# Configuring the sample application (Number Game) #

As configured in `DriverConf.py`, we have an entry for reaching the `NumberGame` sample application. This entry should point to the full path to `slither2_projects/NumberGame`.

We now need to make sure the NumberGame application configuration is completed. Change to the NumberGame directory:

```
cd slither2_projects/NumberGame
```

Copy the sample configuration file so we can edit it:
```
cp ProjectConf.py.in ProjectConf.py
```

Here is the file:
```
BASE_PROJECT_DIR = '/home/gkt/public_html/slither2_projects'

DOCROOT = '%s/NumberGame/Files'%( BASE_PROJECT_DIR )

SESSION_DIR = '%s/session'%( DOCROOT )
LOG_DIR     = '%s/logs'%( DOCROOT )


LOG_FILE_NAME = '%s/NumberGame'%( LOG_DIR )

HTML_SEARCH_PATH = [ '.', '%s/NumberGame'%(BASE_PROJECT_DIR) ]

LOCAL_PROPS = {

   'log_file_name' : '%s/NumberGame'%( LOG_DIR ) ,
   'user_profile_dir' : SESSION_DIR,
   'encode_target' : 'BasicTemplate.html',
   'search_path' : HTML_SEARCH_PATH,

}
```

The only line you will need to edit here is the one containing the `BASE_PROJECT_DIR` variable. You need to make sure the path is correct all the way up to `slither2_projects`.

Similar to the driver configuration, there are some directories that need to be created in `slither2_projects` that are guaranteed writable by the user Apache is running your code as:

```
rm -rf slither2_projects/Files
mkdir -p slither2_projects/Files/{session,logs}
chmod -R 775 slither2_projects/Files
```

In the interests of conciseness, we're not presenting all details of this configuration here.

# Testing #

At this point, you are now ready to attempt to run the number game. You should be able to point your browser in the right direction via the following URL(s):

```
http://<host-or-IP>/~<your-username>/Driver.py/NumberGame
http://<host-or-IP>/~<your-username>/Driver.py/cgi-bin/NumberGame
http://<host-or-IP>/~<your-username>/Driver.cgi/NumberGame
http://<host-or-IP>/~<your-username>/Driver.cgi/cgi-bin/NumberGame
```

# Troubleshooting #

Anyway, if all goes well, you should be able to play the sample Number Game application. You probably played this game as a child where you guess a number between 1 and N and your friend will tell you _higher_ or _lower_. Eventually, you have narrowed the search sufficiently and after log2 N steps you will find the answer.

(I realize that anyone reading this is more interested in getting the application working. I couldn't help myself. It's amazing how when we learn this game as children, it isn't called the Binary Search game.)

Well, as you might guess, you might try to run the sample application and--for whatever reason--it won't work.

Here are some things to check:

  * If you get Page not Found or Internal Server Error, you'll need to check the Apache logs. These files are usually written in `/var/log/apache` as `access_log` and `error_log`, respectively.
  * If you are lucky to see something on the screen that looks like a proper page, it means one of two things: a problem locating the application code or a problem with the application code itself. In either case, you can start examining the log files.
  * As noted earlier, `Driver.py` will write information into `slither2/logs/Driver*.log`. This is the place to look, especially if there appears to be some sort of _dispatch_ problem (i.e. you are not seeing the Number Game welcome screen at all.)
  * In the event you are seeing the Number Game but running into some problem, check `slither2_projects/Files/logs`. This may contain some logging output from the application itself.
  * If all else fails, go back and check everything twice. Most Python-related problems are usually the result of a path configuration problem. As you start delving into more advanced applications of Slither (e.g. databases), it could be that some needed Python libraries (e.g. MySQLdb support) are missing. We'll be covering this issue in a separate document. The idea here is to make sure you can get a minimal Slither application up and running in a minimum amount of time.
