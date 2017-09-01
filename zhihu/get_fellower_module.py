import pymysql
import socket

conn = pymysql.connect(host='localhost', user='root', passwd='zhangPEI926！@', db='robots',
                       port=3306, charset='utf8')
cur = conn.cursor()
sql = "update test_process set status = 2, machine = '%s' where status = 0 limit 100" % \
      socket.gethostname()
cur.execute(sql)
conn.commit()
sql = "select id, html, top from test_process where status = 2 and machine = '%s' limit " \
                  "100" % socket.gethostname()