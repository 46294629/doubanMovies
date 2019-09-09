#!/usr/bin/python
# -*- coding: utf-8 -*-
from db.mysql import MySQLdb
from get_movies import file_path,get_movie
import chardet
import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')

MovieDB = {'db':"movie",'host':"127.0.0.1",'port':3306,'user':"root",'passwd':"12344321"}

dbs={}
def mysql(reconnect=False, **conn):
    key = str(conn)
    if key not in dbs or reconnect:
        dbs[key] = MySQLdb(**conn)
    return dbs[key]

def checkFormat(ReleaseTime):
    detail_time = ReleaseTime.split('-')
    if len(detail_time) == 3:
        return ReleaseTime
    elif len(detail_time) == 2:
        return ReleaseTime +"-01"
    else:
        return ReleaseTime + "-01-01"

def handle_records():
    with open(file_path, 'r') as f:
        datas = f.readlines()
    failed_record_map = {}
    for data in datas:
        if data == "name;intro;url\n":
            continue
        infos = data.rstrip('\n').split(';')
        ChineseName = infos[0].split('/')[0].strip()

        OtherName = infos[0].split('/')[-1].strip()
        url = infos[-1]
        try:
            directors, actors, types, area, ReleaseTime = get_movie(url, ChineseName)
            if area:
                ReleaseTime = checkFormat(ReleaseTime)
                insert_movie(ChineseName, OtherName,area, ReleaseTime)
                id = query_movie(ChineseName, OtherName,area, ReleaseTime)
                if id != -1:
                    for director in directors:
                        insert_director(director,id)
                    for actor in actors[0:10]:
                        insert_actor(actor,id)
                    for type in types:
                        insert_type(type,id)
                    print id
                    continue
                else:
                    print "id=-1, insert movie go wrong! record is:%s and url is:%s" % (ChineseName, url)
            else:
                print "cannot connect to url.record is:%s and url is:%s" % (ChineseName, url)
            failed_record_map[ChineseName] = url
        except Exception as e:
            print "error:%s when handle record:%s and url is:%s"%(str(e),ChineseName, url)
            return
    if failed_record_map:
        #如果想要显示为中文而非ascii，dumps时应该指明：json.dumps(python_str,ensure_ascii=False)
        #如果开头没有指明编码，打开文件时应该指明：with open("failed_records.json",'a',encoding='utf-8') as w:
        with open("failed_records.json",'a') as w:
            w.write("\n"+json.dumps(failed_record_map))

def insert_movie(ChineseName,OtherName,area,ReleaseTime):
    db = mysql(**MovieDB)
    sql = 'insert into Movies (ChineseName, OtherName,area, ReleaseTime) values ("%s","%s","%s","%s");' %(ChineseName,OtherName,area,ReleaseTime)
    for _ in range(3):
        try:
            db.execute(sql)
            return True
        except Exception as e:
            print "error:%s" %str(e)
            db = mysql(True,**MovieDB)
    return False

def query_movie(ChineseName, OtherName, area, ReleaseTime):
    db = mysql(**MovieDB)
    sql = 'select id from Movies where ChineseName="%s" and OtherName="%s" and area="%s" and ReleaseTime="%s"' % (ChineseName, OtherName, area, ReleaseTime)
    for _ in range(3):
        try:
            res = db.query(sql)
            return res[0]['id']
        except Exception as e:
            print "error:%s" %str(e)
            db = mysql(True,**MovieDB)
    return -1

def insert_director(director,id):
    db = mysql(**MovieDB)
    sql = 'insert into Directors (director, movieId) values ("%s",%d)' %(director,id)
    for _ in range(3):
        try:
            db.execute(sql)
            return True
        except Exception as e:
            print "error:%s" % str(e)
            db = mysql(True, **MovieDB)
    return False

def insert_actor(actor,id):
    db = mysql(**MovieDB)
    sql = 'insert into Actors (actor, movieId) values ("%s",%d)' %(actor,id)
    for _ in range(3):
        try:
            db.execute(sql)
            return True
        except Exception as e:
            print "error:%s" % str(e)
            db = mysql(True, **MovieDB)
    return False

def insert_type(type,id):
    db = mysql(**MovieDB)
    sql = 'insert into Types (type, movieId) values ("%s",%d)' %(type,id)
    for _ in range(3):
        try:
            db.execute(sql)
            return True
        except Exception as e:
            print "error:%s" % str(e)
            db = mysql(True, **MovieDB)
    return False

if __name__ == '__main__':
    handle_records()






