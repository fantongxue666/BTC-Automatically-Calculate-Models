import json

from flask import Flask, request

from constant.DataBaseHandle import DataBaseHandle
from util import DateEncoder, LogUtil, EncryptDecryptUtil

app = Flask(__name__)
'''
/login              登录
/register           注册 本系统不支持注册
'''

# 登录
@app.route('/login',methods = ['POST'])
def login():
    # 获取账号密码
    userName = request.form.get("userName")
    passWord = EncryptDecryptUtil.encryptMd5(request.form.get("passWord"))
    # 查询用户
    sql = "select * from btc_user where userName = '%s' and password = '%s'" % (userName,passWord)
    data = DataBaseHandle().selectDB(sql)
    LogUtil.infoAndText("查询结果",data)
    size = len(data)
    if size>0:
        return "1"
    else:
        return "0"


# 注册
@app.route('/register',methods = ['POST'])
def register():
    password = EncryptDecryptUtil.encryptMd5("admin")
    LogUtil.info(password)
    sql = "insert into btc_user values('8asdfyas0dfy','admin','%s',now())" % (password)
    LogUtil.info(sql)
    DataBaseHandle().updateDB(sql)
    return "test"

if __name__ == '__main__':
    app.run()

