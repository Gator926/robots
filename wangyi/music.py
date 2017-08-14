import pymysql
import urllib.request
from lxml import etree


def openPage(url):
    header = {
        'cookie': 'my cookie',
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    req = urllib.request.Request(url=url, headers=header)
    html = urllib.request.urlopen(req).read()
    html = html.decode('UTF-8')
    print(html)
    html = etree.HTML(html)
    return html


def connDB(type, sentense):
    conn = pymysql.connect(host='localhost', user='root', passwd='1234', db='spider', port=3306, charset='utf8')
    if type == 0:
        cur = conn.cursor()
        cur.execute(sentense)
        conn.commit()
        result = sentense + "执行完毕"
        return result
    else:
        cur = conn.cursor()
        cur.execute(sentense)
        result = cur.fetchall()
        return result

# url = ["http://music.163.com/#/discover/artist/cat?id=1001"]
# html = openPage(url[0])
# print(html.xpath("//ul[@id='initial-selector']/li/a/text()"))

conn = pymysql.connect(host='localhost', user='root', passwd='1234', db='robots', port=3306, charset='utf8')
cur = conn.cursor()

for index in range(91, 900):
    try:
        cur.execute("insert into test (number) value ("+str(index)+")")
    except:
        pass
conn.commit()
