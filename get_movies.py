#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import urllib
from lxml import etree
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#xpath learning: https://www.runoob.com/xpath/xpath-nodes.html; https://www.cnblogs.com/lei0213/p/7506130.html\

file_path = 'H:\movies.txt'

#logiin
def login_and_get(url):
    # proxies = get_proxies_from_site()
    opener = urllib2.build_opener()
    opener.addheaders.append(('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'))
    opener.addheaders.append(('Cookie', 'gr_user_id=556cc5aa-ac91-4177-99a8-87bae5b964a6; _ga=GA1.2.1565543125.1509547123; _vwo_uuid_v2=B6814730F14CEB7E631FAD63B22EA8D4|c9e0dbd021c28e2116d7e5ccd42db87e; __utmv=30149280.6377; douban-fav-remind=1; douban-profile-remind=1; __utmz=30149280.1551784716.55.19.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmz=223695111.1551784716.271.194.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=30149280.1565543125.1509547123.1556159820.1556161913.60; __utma=223695111.1780354380.1494407470.1556159820.1556161913.273; __gads=ID=ef1b2e2072a5259b:T=1556518326:S=ALNI_Maj2FNxW0l2em_vauvp5ooe0iONuQ; ll="118281"; bid=yXGP0aoPz0s; trc_cookie_storage=taboola%2520global%253Auser-id%3D9f0c2f7c-ea39-4973-843b-b3ae006d00ca-tuct3165360; __yadk_uid=6CKSGawCyAtLPFzxS6JRX4D2wEQ1p8AG; viewed="30468550_1905617_1186176_20397334_1201821_25802164_19948593_10678825_24842258_4913064"; push_noty_num=0; push_doumail_num=0; ap_v=0,6.0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1567748022%2C%22https%3A%2F%2Fwww.douban.com%2Fpeople%2Fwaitforwho%2F%22%5D; _pk_id.100001.4cf6=af97bef9087773c3.1494407469.690.1567748765.1567744426.'))
    for _ in range(3):
        try:
            res = opener.open(url)
            return res.read()
        except Exception  as e  :
            print('something must go wrong:%s'%str(e))
            time.sleep(3)
    return None

#find recorded movies
def get_seen_movies():
    with open (file_path,'w') as f:
        f.write("name;intro;url\n")
        for i in range(50):
            url = 'https://movie.douban.com/people/waitforwho/collect?start='+str(i*15)+'&sort=time&rating=all&filter=all&mode=grid'
            data = login_and_get(url)
            if not data:
                continue
            html = etree.HTML(data)
            datas = html.xpath('//div[@class="grid-view"]/div[@class="item"]/div[@class="info"]') #找出所有class="grid-view"下class为"item"下class为"info"下的值
            for data in datas:
                #豆瓣爬出来的text（）都是只含一个值的list形式
                #从刚刚匹配到的内容的头部开始找
                movie_name = data.xpath('ul/li[@class="title"]/a/em/text()')[0].decode('utf-8')
                f.write (movie_name.encode('utf-8') + ';')
                intro = data.xpath('ul/li[@class="intro"]/text()')[0].decode('utf-8')
                f.write(intro.encode('utf-8') + ';')
                url = data.xpath('ul/li[@class="title"]/a/@href')[0]
                f.write (url + '\n')
            print ("OK %d"%i)
            time.sleep(3)

def get(url):
    req=urllib2.Request(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'})
    try:
        res = urllib2.urlopen(req)
        return res.read()
    except urllib2.HTTPError:
        pass
    except Exception as e:
        print ("error:%s" %str(e))
    return None

def get_with_referer(url, ChineseName):
    opener = urllib2.build_opener()
    opener.addheaders.append(('User-Agent',
                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'))
    #获取cookies代替下面的yourcookies
    opener.addheaders.append(('Cookie','YourCookies'))
    #中文转化成urlencode
    movieName = urllib.quote(ChineseName)
    #referer指明从哪个网页转跳过来。部分禁片只能登录后搜索名字才能显示，直接通过链接get会404
    opener.addheaders.append(('Referer',"https://movie.douban.com/subject_search?search_text=%s&cat=1002" %movieName))
    for _ in range(3):
        try:
            res = opener.open(url)
            return res.read()
        except Exception  as e  :
            print('something must go wrong:%s'%str(e))
            time.sleep(3)
    return None

def get_movie(url, ChineseName):
    data = get(url)
    if not data:
        #有些电影必须要登陆后通过搜索才能找到，直接通过链接会显示404
        data = get_with_referer(url, ChineseName)
        if not data:
            return [],[],[],"","1000-01-01"
    html = etree.HTML(data)
    data = html.xpath('//div[@id="info"]')[0]
    #下标从1开始，span[1]代表第一个span

    directors = [ director.strip() for director in data.xpath('span[1]/span[2]/a/text()')]
    actors= [ actor.strip() for actor in data.xpath('//span[@class="actor"]/span[2]/a/text()')]
    types = [ type.strip() for type in data.xpath('//span[@property="v:genre"]/text()') ]
    #获取标签之外的字段，其实属于父标签
    area=''
    for area in html.xpath('//div[@id="info"]/text()'):
        if not area.startswith('\n') and area!= ' / ' and area != ' ':
            area = area.split('/')[0].strip()
            break
    ReleaseTime = data.xpath('//span[@property="v:initialReleaseDate"]/text()')
    if ReleaseTime:
        ReleaseTime = ReleaseTime[0]
        ReleaseTime = ReleaseTime[0:ReleaseTime.find('(')] if ReleaseTime.find('(') != -1 else ReleaseTime
    else:
        ReleaseTime = html.xpath('//div[@id="content"]/h1/span[@class="year"]/text()')
        ReleaseTime = ReleaseTime[0].strip('()') if ReleaseTime else ''
    return directors, actors, types, area, ReleaseTime

if __name__ == '__main__':
    get_seen_movies()
    # directors, actors, types, area, ReleaseTime = get_movie('https://movie.douban.com/subject/4842410/','嗜血法医')
    # print directors, actors, types, area, ReleaseTime
