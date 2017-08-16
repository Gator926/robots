from selenium import webdriver
import datetime
import pymysql

conn = pymysql.connect(host='localhost', user='root', passwd='1234', db='robots', port=3306, charset='utf8')

def connDB(type, sentense):
    print(sentense)
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


def eachDB(elements, top, followers):
    cur = conn.cursor()
    follow_index = 0
    for index, element in enumerate(elements):
        if element.text != "":                                                                        # 排除空元素

            follow_list = followers[follow_index].text.split(" ")
            follow_index = follow_index + 1
            if int(follow_list[0]) == 0:
                status = 1
            else:
                status = 0
            url = element.get_attribute("href")
            urllist = url.split("/")
            try:
                # dumplicate = connDB(1, "select id from zhihu WHERE account='"+str(urllist[-1])+"'")
                # if len(dumplicate) == 0:
                cur.execute('insert into zhihu (account, name, url, top, status) VALUES ("' + str(urllist[-1]) + '","' + str(element.text) + '", "' + str(url) + '","' + str(top) + '", "'+str(status)+'")')
                print(str(element.text)[0:3] + "\t\t 数据正确，已捕获 \t\t" + str(datetime.datetime.now()))
                # else:
                #     print(str(element.text) + ">>>已存在")
            except Exception as E:
                # connDB(0, 'insert into error (url) VALUE ("'+str(url)+'")')
                try:
                    cur.execute('insert into error (url) VALUE ("'+str(url)+'")')
                    print(str(element.text)[0:3] + "\t\t 发生错误，已处理 \t\t" + str(datetime.datetime.now()))
                except:
                    print(str(element.text)[0:3] + "\t\t 发生错误，未处理 \t\t" + str(datetime.datetime.now()))
    conn.commit()

def get_follower(url):
    browser = webdriver.Chrome()
    browser.implicitly_wait(1)
    browser.get(url + "/followers")

    urllist = url.split("/")

    while 1:
        # time.sleep(1)
        element = browser.find_elements_by_class_name("UserLink-link")
        followers = browser.find_elements_by_xpath("//span[@class='ContentItem-statusItem'][last()]")
        eachDB(element, urllist[-1], followers)
        try:
            button = browser.find_element_by_xpath(
                "//button[@class='Button PaginationButton PaginationButton-next Button--plain'][last()]")
            button.click()
        except:
            print("循环完毕")
            connDB(0, "update zhihu set status = 1 where account = '"+str(urllist[-1])+"'")
            browser.close()
            break


if __name__ == '__main__':
    # while True:
    #     url = connDB(1, "select url from zhihu WHERE status = 0 limit 1")
    #     if len(url) != 0:
    #         get_follower(url[0][0])
    #     else:
    #         break

    url = connDB(1, "select url from zhihu WHERE status = 0 limit 1")
    get_follower(url[0][0])