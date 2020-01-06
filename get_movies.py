#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import  Options
from selenium.webdriver.support.wait import WebDriverWait
from lxml import etree
import time
import sys
import utils
reload(sys)
sys.setdefaultencoding('utf-8')
#xpath learning: https://www.runoob.com/xpath/xpath-nodes.html; https://www.cnblogs.com/lei0213/p/7506130.html\

file_path = 'movies.txt'
username = 'xxxxxx'
password = 'xxxxxx'
User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'

def login_get_cookies():
    cookies = utils.load_cookies()
    if cookies:
        session = requests.Session()
        session.headers['User-Agent'] = User_Agent
        session.cookies = requests.utils.cookiejar_from_dict(cookies)
        return session,cookies
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(executable_path='./chromedriver_win32/chromedriver.exe')
    url = 'https://accounts.douban.com/passport/login'
    while 1:
        driver.get(url)
        link = driver.find_element_by_xpath("//ul[@class='tab-start']/li[@class='account-tab-account']")
        link.click()

        name_input = driver.find_element_by_xpath("//div[@class='account-form-field']/input[@id='username']")
        pass_input = driver.find_element_by_xpath("//div[@class='account-form-field']/input[@id='password']")
        remember_input = driver.find_element_by_xpath("//div[@class='account-form-ft']/p[@class='account-form-remember']/input[@id='account-form-remember']")
        login_botton = driver.find_element_by_xpath("//div[@class='account-form-field-submit ']/a[@class='btn btn-account']")
        name_input.clear()
        name_input.send_keys(username)
        pass_input.clear()
        pass_input.send_keys(password)
        remember_input.click()
        login_botton.click()

        start_ts = time.time()
        print("start..",start_ts)

        try:
            WebDriverWait(driver,15).until_not(lambda x:x.find_element_by_xpath("//div[@class='account-form-field-submit ']/a[@class='btn btn-account btn-active']").is_displayed())
            WebDriverWait(driver, 15).until_not(lambda x: x.find_element_by_xpath("//div[@class='account-form-field-submit ']/a[@class='btn btn-account']").is_displayed()) #wait until login
        except:
            import tracback
            print(tracback.format_exc())
            utils.save_html('exc_inex.html',driver.page_source)
            import os
            os._exit(-1)

        print ('end..',time.time()-start_ts)
        driver.save_screenshot('submit.png')
        utils.save_html('index.html',driver.page_source)

        if u'douban' in driver.page_source:
            selenium_cookies = driver.get_cookies()
            print ("selenium_cookies:",selenium_cookies)
            driver.close()
            break
        else:
            driver.close()

    #handle cookies
    session = requests.Session()
    session.headers['User-Agent'] = User_Agent
    for i in selenium_cookies:
        requests.utils.add_dict_to_cookiejar(session.cookies, {i['name']: i['value']})
    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    utils.save_cookies(cookies)
    return session,cookies

#find recorded movies
def get_seen_movies():
    session, _ = login_get_cookies()
    with open (file_path,'w') as f:
        f.write("name;intro;url;date;mark\n")
        for i in range(55):
            url = 'https://movie.douban.com/people/xxxxx/collect?start='+str(i*15)+'&sort=time&rating=all&filter=all&mode=grid'
            data = session.get(url)
            if not data:
                continue
            html = etree.HTML(data.text)
            datas = html.xpath('//div[@class="grid-view"]/div[@class="item"]/div[@class="info"]') #找出所有class="grid-view"下class为"item"下class为"info"下的值
            for data in datas:
                #豆瓣爬出来的text（）都是只含一个值的list形式
                #从刚刚匹配到的内容的头部开始找
                movie_name = data.xpath('ul/li[@class="title"]/a/em/text()')[0].decode('utf-8')
                f.write (movie_name.encode('utf-8') + ';')
                intro = data.xpath('ul/li[@class="intro"]/text()')[0].decode('utf-8')
                f.write(intro.encode('utf-8') + ';')
                url = data.xpath('ul/li[@class="title"]/a/@href')[0]
                f.write (url + ';')
                date = data.xpath('ul/li/span[@class="date"]/text()')[0]
                f.write(date+';')
                mark = data.xpath('ul/li[3]/span/@class')[0]
                if mark.startswith("rating"):
                    mark = mark[6]
                else:
                    mark = '0'
                f.write(mark + '\n')
            print ("OK %d"%i)
            time.sleep(3)

def get(url):
    req=urllib2.Request(url,headers={'User-Agent':User_Agent})
    try:
        res = urllib2.urlopen(req)
        return res.read()
    except urllib2.HTTPError:
        pass
    except Exception as e:
        print ("get movie error:%s" %str(e))
    return None

def get_with_referer(url, ChineseName):
    #中文转化成urlencode 设置编码
    movieName = urllib.quote(ChineseName)
    #referer指明从哪个网页转跳过来。部分禁片只能登录后搜索名字才能显示，直接通过链接get会404
    session, _ = login_get_cookies()
    session.headers['Referer'] = "https://movie.douban.com/subject_search?search_text=%s&cat=1002" %movieName
    for _ in range(3):
        try:
            data = session.get(url)
            return data.text
        except Exception  as e  :
            print('get movie with referer:%s'%str(e))
            time.sleep(3)
    return None

def get_movie(url, ChineseName):
    print "get ",ChineseName
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

