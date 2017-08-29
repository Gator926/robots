from DBUtils.PooledDB import PooledDB
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from pymysql.err import IntegrityError, ProgrammingError
from lxml import etree
import datetime
import pymysql
import time
import socket
import threading
import logging


# def get_url_list(cur, conn):
def get_url_list(pool):
    while 1:
        if len(url_list) > 1:
            time.sleep(5)
        else:
            conn = pool.connection()
            cur = conn.cursor()

            sql = "update test_zhihu set status = 2, machine = '%s' where status = 0 limit 100" %\
                  socket.gethostname()
            cur.execute(sql)
            conn.commit()
            sql = "select url, account from test_zhihu where status = 2 and machine = '%s' limit 100" %\
                  socket.gethostname()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
            conn.close
            if len(result) == 0:
                time.sleep(5)
                print("无新数据需要爬取")
                logging.info("无新数据需要爬取")
            else:
                for each in result:
                    tmp = [each[0], each[1]]
                    url_list.append(tmp)
            time.sleep(5)


# def get_html(cur, conn):
def get_html(pool):
    number = 0
    browser = webdriver.Chrome()  # 初始化浏览器
    browser.implicitly_wait(2)  # 设置隐形等待时间

    while 1:
        if len(url_list) < 1:
            time.sleep(5)
        else:
            each_url = url_list.pop(0)
            top = each_url[1]  # 上一级
            if "followers" in each_url[0]:
                browser.get(each_url[0])
            else:
                browser.get(each_url[0] + "/followers")
            while 1:
                try:
                    browser.find_element_by_class_name("UserLink-link")  # 防止页面未加载完毕
                    # 页面元素
                    element = browser.find_element_by_class_name("List").get_attribute("innerHTML")
                    button = browser.find_element_by_xpath(
                        "//button[@class='Button PaginationButton PaginationButton-next "
                        "Button--plain'][last()]")

                    try:
                        conn = pool.connection()
                        cur = conn.cursor()
                        element = element.replace("'", '"')
                        sql = "insert into test_process (html, top, status) values ('%s', '%s', 0)" \
                              % (element, top)
                        cur.execute(sql)
                        conn.commit()
                        cur.close()
                        conn.close
                    except ProgrammingError:
                        pass

                    button.click()
                    time.sleep(2)

                    conn = pool.connection()  # 更新已爬的页面
                    cur = conn.cursor()
                    sql = "update test_zhihu set url = '%s' where account = '%s'" \
                          % (browser.current_url, top)
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close

                except NoSuchElementException as E:  # 类型错误，网页不存在，无关注者,或者无下一页按钮
                    unknowurl = browser.current_url
                    if "unhuman" in unknowurl:
                        print("爬虫被捕获")
                        exit()
                    else:
                        conn = pool.connection()
                        cur = conn.cursor()

                        sql = "update test_zhihu set status = 1, machine = '%s' where account = '%s'" \
                              % (socket.gethostname(), top)
                        cur.execute(sql)
                        conn.commit()

                        cur.close()
                        conn.close
                        print(top + "\t已爬完\t" + str(datetime.datetime.now()))
                        logging.info(top + "\t已爬完\t" + str(datetime.datetime.now()))
                        logging.error(E)

                        conn = pool.connection()
                        cur = conn.cursor()
                        sql = "select url from test_zhihu where account = '%s'" % top
                        cur.execute(sql)
                        result = cur.fetchall()
                        cur.close()
                        conn.close

                        url_string = result[0]
                        if "page" in url_string:  # 构造原有的url
                            url_string = ""
                            url_string_list = url_string.split('/')
                            for each in url_string_list:
                                url_string += each
                            conn = pool.connection()
                            cur = conn.cursor()
                            sql = "update test_zhihu set url = '%s' where account = '%s'" % (
                                url_string, top)
                            cur.execute(sql)
                            conn.commit()
                            cur.close()
                            conn.close

                        break
                except Exception as E:
                    print(E)
                    logging.error(E)


# def get_fellower(cur, conn):
def get_fellower(pool):
    while 1:
        if len(follower_list) > 1:
            time.sleep(5)
        else:  # 查询数据
            conn = pool.connection()
            cur = conn.cursor()

            sql = "update test_process set status = 2, machine = '%s' where status = 0 limit 100" % \
                  socket.gethostname()
            cur.execute(sql)
            conn.commit()
            sql = "select id, html, top from test_process where status = 2 and machine = '%s' limit " \
                  "100" % socket.gethostname()
            cur.execute(sql)
            result = list(cur.fetchall())

            cur.close()
            conn.close
        for each in result:
            element = each[1]
            id = each[0]
            top = each[2]

            # logging.info("开始爬取" + element)

            html = etree.HTML(element)  # 将str转换成html代码
            follower_name = html.xpath("//a[@class='UserLink-link']/text()")  # 获取用户昵称
            # 关注者url
            url = html.xpath("//div[@class='UserItem-title']//a[@class='UserLink-link']/@href")
            #关注者的关注人数
            follower_following = html.xpath("//span[@class='ContentItem-statusItem'][last()]")

            for index, content in enumerate(follower_name):  # 获取用户被关注人数
                account_list = url[index].split("/")  # 根据url获取用户账号
                follower_number = follower_following[index].text.split(" ")
                if int(follower_number[0]) == 0:
                    status = 1
                else:
                    status = 0

                conn = pool.connection()
                cur = conn.cursor()
                try:
                    sql = "insert into test_zhihu (account, name, url, top, status) VALUES (" \
                          "'%s', '%s', '%s', '%s', %d)" % (account_list[-1], content,
                          "https://www.zhihu.com" + url[index], top, status)
                    cur.execute(sql)
                    conn.commit()
                    if len(account_list[-1]) < 10:
                        account_list += " " * (10 - len(account_list))
                    print(account_list[-1][0:10] + "\t数据正确\t" + str(datetime.datetime.now())[0:18])
                    logging.info(account_list[-1][0:10] + "\t数据正确\t" +
                                 str(datetime.datetime.now())[0:18])
                except IntegrityError:
                    if len(account_list[-1]) < 10:
                        account_list += " " * (10 - len(account_list))
                    print(account_list[-1][0:10] + "\t数据存在\t" + str(datetime.datetime.now())[0:18])
                    logging.info(account_list[-1][0:10] + "\t数据存在\t" +
                                 str(datetime.datetime.now())[0:18])
                sql = "delete from test_process where id = %d" % id
                cur.execute(sql)
                conn.commit()

                cur.close()
                conn.close



if __name__ == '__main__':
    url_list = []
    follower_list = []
    thread_list = []

    connKwargs = {'charset': 'utf8'}  # 设置字符集
    pool = PooledDB(pymysql, 5, host='****', user='****', passwd='****',
                    db='****', port=3306, maxshared=10, blocking=True, **connKwargs)
    filename = "robots.log"
    logging.basicConfig(filename=filename, level=logging.DEBUG)
    # conn = pool.connection()
    # cur = conn.cursor()

    # t1 = threading.Thread(target=get_url_list, args=(cur, conn, ))  # 启动线程
    # t2 = threading.Thread(target=get_html, args=(cur, conn, ))  # 启动线程
    # t3 = threading.Thread(target=get_fellower, args=(cur, conn, ))  # 启动线程
    t1 = threading.Thread(target=get_url_list, args=(pool, ))  # 启动线程
    t2 = threading.Thread(target=get_html, args=(pool, ))  # 启动线程
    t3 = threading.Thread(target=get_fellower, args=(pool, ))  # 启动线程

    thread_list.append(t1)
    thread_list.append(t2)
    thread_list.append(t3)

    t1.setDaemon(True)
    t2.setDaemon(True)
    t3.setDaemon(True)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    # cur.close()
    # conn.close()
