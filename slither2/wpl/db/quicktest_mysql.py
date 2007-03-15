#!/usr/local/python1.5/bin/python1.5.2

# This is a quick test you can run. It connects to the 'customers' database
# on enigma and prints the list of plans. It uses the 'MySQLdb_new' kludge
# module in this directory.

import sys
import Path
import DBFactory

msda = DBFactory.getNewMySQLDataAccess('quicktest_mysql.conf')
print msda

msda.execute('select Id, Name from Plan')

rs = msda.getRecords()

for r in rs:
   print str(r)

sys.exit(0)
