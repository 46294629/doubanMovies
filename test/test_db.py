import sys
import time
sys.path.append("../db")
from mysql import MySQLdb

db=MySQLdb("test")
sql = 'insert into test_tb (value) values("test3");'
print db.execute(sql)
sql="select * from test_tb"
print db.query(sql)
time.sleep(10)
sql="select value from test_tb"
print db.query(sql)