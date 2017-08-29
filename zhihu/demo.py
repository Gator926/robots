from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from pymysql.err import IntegrityError
import datetime
import pymysql


def my_align(string, length=0):
    if length == 0:
        return string
    slen = len(string)
    re = string
    if isinstance(string, str):
        placeholder = ' '
    else:
        placeholder = u'　'
    while slen < length:
        re += placeholder
        slen += 1
    return re


def conn_db(sentence):
    """
    根据sql语句查询数据
    :param sentence:    待执行的sql语句
    :return:            查询结果
    """
    cur = conn.cursor()
    cur.execute(sentence)
    result = cur.fetchall()
    return result


def store_follower(elements, top, followers, number):
    """
    储存关注者信息
    :param elements:    关注者信息元素
    :param top:         该用户信息
    :param followers:   该用户关注者信息
    :param number:      爬取的用户数
    """
    cur = conn.cursor()                                             # 获取数据库操作游标
    follow_index = 0                                                # 关注者下标
    for index, element in enumerate(elements):
        if element.text != "":                                      # 排除空元素
            follow_list = followers[follow_index].text.split(" ")   # 获取关注改用户的人数
            follow_index += 1
            if int(follow_list[0]) == 0:                            # 该用户无关注者
                status = 1
            else:                                                   # 该用户有关注者
                status = 0
            url = element.get_attribute("href")                     # 获取用户网页地址
            urllist = url.split("/")                                # 将用户地址按"/"进行拆分
            string = element.text
            try:
                cur.execute('insert into zhihu (account, name, url, top, status) VALUES ("' + str(urllist[-1]) + '","' + str(element.text) + '", "' + str(url) + '","' + str(top) + '", "' + str(status) + '")')
                number += 1
                print("No.{number} \t {string: <10} \t数据正确，已捕获 \t {time}".format(number=number, string=string[0:5],
                                                                            time=str(datetime.datetime.now())[
                                                                                 0:-7]))
            except IntegrityError:                                  # 数据元素已经存在
                try:
                    cur.execute('insert into error (url) VALUE ("' + str(url) + '")')
                    print("No.{number} \t {string: <10} \t数据正确，已处理 \t {time}".format(number=number, string=string[0:5],
                                                                                     time=str(datetime.datetime.now())[
                                                                                          0:-7]))
                except IntegrityError:
                    print("No.{number} \t {string: <10} \t数据正确，已存在 \t {time}".format(number=number, string=string[0:5],
                                                                                     time=str(datetime.datetime.now())[
                                                                                          0:-7]))
                except UnicodeEncodeError:
                    print("No." + str(number) + "\t" + "编码错误，已忽略")
                except Exception as E:
                    print(E)
                    print(repr(E))
                    exit()
    conn.commit()
    return number


def get_follower(web_url, number, browser):
    """
    获取关注者信息
    :param web_url:     用户的网页地址
    :param number:      爬取的用户数
    """
    try:
        browser.get(web_url + "/followers")

        url_list = web_url.split("/")                                   # 根据"/"对url进行拆分

        while 1:
            element = browser.find_elements_by_class_name("UserLink-link")
            followers = browser.find_elements_by_xpath("//span[@class='ContentItem-statusItem'][last()]")
            try:
                number = store_follower(element, url_list[-1], followers, number)
                button = browser.find_element_by_xpath("//button[@class='Button PaginationButton PaginationButton-next "
                                                       "Button--plain'][last()]")
                button.click()
            except NoSuchElementException:                              # 类型错误，网页不存在，无关注者,或者无下一页按钮
                cur_update = conn.cursor()                              # 将用户状态改为1
                cur_update.execute("update zhihu set status = 1 where account = '" + str(url_list[-1]) + "'")
                conn.commit()
                break
            except Exception as E:
                print(E)
                print(repr(E))
                exit()
        return number
    except WebDriverException:
        print("网页出现错误，正在重启")
        get_follower(web_url=web_url, number=number)

if __name__ == '__main__':
    conn = pymysql.connect(host='****', user='****', passwd='****', db='****', port=3306,
                           charset='utf8')
    number = 0                      # 统计获取用户的个数
    browser = webdriver.Chrome()    # 初始化浏览器
    browser.implicitly_wait(1)      # 设置隐形等待时间
    while 1:
        url = conn_db("select url from zhihu where status ='0' order by time desc limit 1")
        if len(url) != 0:
            number = get_follower(url[0][0], number, browser)
        else:
            break
    conn.close()
    browser.close()
