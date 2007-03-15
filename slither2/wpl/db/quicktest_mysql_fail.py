#!/usr/local/python1.5/bin/python1.5.2

# This test is *supposed* to fail, because most the Python above does
# *not* have the latest MySQLdb installed in 'site-packages'

import sys
import Path
import DBFactory

msda = DBFactory.getMySQLDataAccess('quicktest_mysql.conf')
print msda

msda.execute('select Id, Name from Plan')

rs = msda.getRecords()

for r in rs:
   print str(r)

sys.exit(0)
