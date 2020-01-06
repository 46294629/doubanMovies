from lxml import etree
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

with open("test_xpath.html",'r') as r:
    data=r.read()
html = etree.HTML(data)
datas = html.xpath('//div[@class="grid-view"]/div[@class="item"]/div[@class="info"]') #each movie's data is in <div class="item">..</div>. so for each page there are 15 ul
for data in datas:
    movie_name = data.xpath('ul/li[@class="title"]/a/em/text()')[0].decode('utf-8')
    print (movie_name.encode('utf-8'))
    url = data.xpath('ul/li[@class="title"]/a/@href')[0]
    print (url)
    intro = data.xpath('ul/li[@class="intro"]/text()')[0].decode('utf-8')
    print (intro.encode('utf-8'))
    break