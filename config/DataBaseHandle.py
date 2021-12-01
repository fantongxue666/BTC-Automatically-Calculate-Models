import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(BASE_DIR))

import pymysql
class DataBaseHandle(object):
    # 相当于java的构造方法，初始化数据库信息并创建数据库连接
    def __init__(self):
        self.host = '127.0.0.1'
        self.username = 'root'
        self.password = '1234'
        self.database = 'btc'
        self.db = pymysql.connect(host=self.host, user=self.username, passwd=self.password, database=self.database)

    # 增删改
    def updateDB(self,sql):
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            print("数据库增删改发生错误")
        finally:
            cursor.close()

    # 查询
    def selectDB(self,sql):
        cursor = self.db.cursor()
        temp = None
        try:
            cursor.execute(sql)
            temp = cursor.fetchall() # 返回所有记录列表
        except:
            print("查询发生错误")
        finally:
            self.db.close()
        return temp
