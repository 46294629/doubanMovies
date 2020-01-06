import pymysql

class MySQLdb():
    def __init__(self, db="", host="127.0.0.1",port=3306,user="root",passwd="12344321"):
        self._db = pymysql.connect(database=db,host=host,port=port,user=user,password=passwd,charset="utf8")

    def query(self,sql):
        cursor = self.get_dictcursor()
        cursor.execute(sql)
        res = cursor.fetchall()
        #self._db.commit()
        cursor.close()
        return res

    def execute(self,sql):
        try:
            cursor = self.get_cursor()
            cursor.execute(sql)
            self._db.commit()
            cursor.close()
            return
        except Exception as e:
            print "error in execute:%s" %str(e)
            raise Exception(e)

    def executemany(self,sql,datas):
        try:
            cursor = self.get_cursor()
            cursor.executemany(sql, datas)
            self._db.commit()
            cursor.close()
            return
        except Exception as e:
            print "error in executemany:%s" %str(e)
            raise Exception(e)

    def get_cursor(self):
        return self._db.cursor()

    def get_dictcursor(self):
        return self._db.cursor(cursor=pymysql.cursors.DictCursor)

    def close(self):
        self._db.close()