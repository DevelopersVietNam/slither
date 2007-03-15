#!/usr/local/python1.5/bin/python1.5.2

import sys
import Path
import DBFactory

pgda = DBFactory.getPostgreSQLDataAccess('quicktest_pgsql.conf')
print pgda

pgda.execute('select name from BTUser')

rs = pgda.getRecords()

for r in rs:
   print str(r)
sys.exit(0)
