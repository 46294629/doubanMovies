#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys

from db.mysql import MySQLdb
from get_movies import file_path, get_movie

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

def get_line(file):
    with open(file,'r') as r:
        for data in r.readlines():
            yield data

def add_date_and_mark():
    failed_record_map = {}
    for data in get_line(file_path):
        if data == "name;intro;url;date;mark\n":
            continue
        infos = data.rstrip('\n').split(';')
        date = infos[-2]
        mark = int(infos[-1])
        ChineseName = infos[0].split('/')[0].strip()
        OtherName = infos[0].split('/')[-1].strip()
        if not change_mark_and_date(ChineseName,OtherName,date,mark):
            failed_record_map[ChineseName] = OtherName
    if failed_record_map:
        with open("failed_records.json",'w') as w:
            w.write(json.dumps(failed_record_map))



def handle_records():
    failed_record_map = {}
    for data in get_line(file_path):
        if data == "name;intro;url;date;mark\n":
            continue
        infos = data.rstrip('\n').split(';')
        ChineseName = infos[0].split('/')[0].strip()
        OtherName = infos[0].split('/')[-1].strip()
        mark = infos[-1]
        date = infos[-2]
        url = infos[-3]
        try:
            directors, actors, types, area, ReleaseTime = get_movie(url, ChineseName)
            if area:
                ReleaseTime = checkFormat(ReleaseTime)
                id = query_movie(ChineseName, OtherName, area, ReleaseTime)
                if id != -1:
                    print "movie has been inserted.continue"
                    continue
                insert_movie(ChineseName, OtherName,area, ReleaseTime, date, mark)
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
        with open("failed_records.json",'w') as w:
            w.write(json.dumps(failed_record_map))

def change_mark_and_date(ChineseName,OtherName,RecordDate,Mark):
    db = mysql(**MovieDB)
    sql = 'update movies set RecordDate="%s", Mark=%f where ChineseName="%s" and OtherName="%s"' % (
        RecordDate, Mark, ChineseName, OtherName)
    try:
        db.execute(sql)
    except Exception as e:
        print "change mark and date of movie %s error:%s"%(ChineseName,str(e))
        return False
    return True

def insert_movie(ChineseName,OtherName,area,ReleaseTime,RecordDate,Mark):
    db = mysql(**MovieDB)
    sql = 'insert into Movies (ChineseName, OtherName,area, ReleaseTime, RecordDate, Mark) values ("%s","%s","%s","%s","%s",%f);' %(ChineseName,OtherName,area,ReleaseTime,RecordDate,Mark)
    for _ in range(3):
        try:
            db.execute(sql)
            return True
        except Exception as e:
            print "insert movie %s error:%s" %(ChineseName,str(e))
            db = mysql(True,**MovieDB)
    return False

def query_movie(ChineseName, OtherName, area, ReleaseTime):
    db = mysql(**MovieDB)
    sql = 'select id from Movies where ChineseName="%s" and OtherName="%s" and area="%s" and ReleaseTime="%s"' % (ChineseName, OtherName, area, ReleaseTime)
    for _ in range(3):
        try:
            res = db.query(sql)
            return res[0]['id'] if res else -1
        except Exception as e:
            print "query error:%s" %str(e)
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
            print "insert director error:%s" % str(e)
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
            print "insert actor error:%s" % str(e)
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
            print "insert type error:%s" % str(e)
            db = mysql(True, **MovieDB)
    return False

if __name__ == '__main__':
    #handle_records()
    add_date_and_mark()






