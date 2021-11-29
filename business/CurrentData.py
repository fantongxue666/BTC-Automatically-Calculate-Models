import datetime
import json
import threading
import time

from util import UUIDUtil
from config.UrlsConstant import UrlConstant
from compute import ComputeMACD
from util import LogUtil
from config.DataBaseHandle import DataBaseHandle

currentDataObjList = []
global isDown
global isUp
global buyedPrice
global lastOpenPrice
global x_count # 出现金叉/死叉的次数
x_count = 0
isDown = False # 是否发生了金叉
isUp = False   # 是否发生了死叉
buyedPrice = 0 # 上一次购买的价格（以开盘价为基准）
lastOpenPrice = 0
'''
DIF：快线值
DEA：慢线值
open_price：开盘价
close_price：收盘价
NOW：当前时间
保证currentDataObjList数组中只保存两个对象，两个时刻的数据
第1个，上一个时间单位的数据
第2个，当前时间单位的数据
'''
def addCurrentDataObj(DIF,DEA,open_price,close_price):
    currentDataObj = {
        "DIF":DIF,"DEA":DEA,"NOW":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if(len(currentDataObjList)>=2):
        # 去掉第一个，从后面补充一个
        del currentDataObjList[0]
        currentDataObjList.append(currentDataObj)
        checkDirection(open_price,close_price)
    else:
        currentDataObjList.append(currentDataObj)

'''
子线程执行，睡眠三个时间单位，结束之后将发生金叉/死叉的状态重置
'''
def reset():
    global isDown
    global isUp
    time.sleep(UrlConstant.Long_Time * 3)
    isDown = False
    isUp = False

'''
自动交易
'''
def deal(flag,lastOpenPrice):
    # 获取此刻的新的开盘价
    open_price, close_price, first, second, third = ComputeMACD.getMACD()
    if(flag == True):
        # 金叉 买进
        resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 接入交易接口。。。以" + str(open_price) + "的开盘价进行了买入"
        writeResult2Txt(resultText)
        sql = "insert into btc_operation values('%s','%s','buyMoney','买入',now(),'创建人')" % (UUIDUtil.getUUID(),open_price)
        DataBaseHandle().updateDB(sql)
    elif(flag == False):
        # 死叉 卖出
        resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 接入交易接口。。。以" + str(open_price) + "的开盘价进行了卖出"
        writeResult2Txt(resultText)
        sql = "insert into btc_operation values('%s','%s','buyMoney','卖出',now(),'创建人')" % (UUIDUtil.getUUID(), open_price)
        DataBaseHandle().updateDB(sql)



'''
自动买入或抛出
'''
def autoByOrSale(open_price,operation):
    # 买之前先判断上次买入的价格，和此次要卖出的价格
    global buyedPrice
    if(operation == "BUY"):
        # 买入
        buyedPrice = open_price
        deal(True, open_price)
    elif(operation == "SALE"):
        # 卖出
        deal(False, open_price)
    else:
        print("operation参数有误，不做任何处理")
'''
判断走势
'''
def checkDirection(open_price,close_price):
    global x_count
    global isDown
    global isUp
    global lastOpenPrice
    LogUtil.infoAndText("当前时间单位数据",json.dumps(currentDataObjList))
    LogUtil.infoAndText("上一次开盘价", str(lastOpenPrice))
    LogUtil.infoAndText("最新开盘价",str(open_price))
    LogUtil.infoAndText("最新收盘价",str(close_price))
    lastOpenPrice = open_price
    # 上一个单位的快线值 - 慢线值
    Avalue = int(currentDataObjList[0]['DIF']) - int(currentDataObjList[0]['DEA'])
    # 当前单位的快线值 - 慢线值
    Cvalue = int(currentDataObjList[1]['DIF']) - int(currentDataObjList[1]['DEA'])


    # 金叉
    if(Avalue < 0 and Cvalue > 0):
        # 添加金叉到金叉/死叉记录容器中
        print("isUp",isUp)
        if(isUp == False):
                resultText = "【时间点："+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"】 MACD走势为金叉！"
                sql = "insert into btc_x values('%s','金叉',now())" % (UUIDUtil.getUUID())
                DataBaseHandle().updateDB(sql)
                writeResult2Txt(resultText)
                # 自动购买
                autoByOrSale(open_price,"BUY")
                isUp = True
                isDown = False
                t = threading.Thread(target=reset)
                t.start()
    # 死叉
    if(Avalue > 0 and Cvalue < 0):
        # 添加死叉到金叉死叉记录容器中
        print("isDown",isDown)
        if(isDown == False):
            resultText = "【时间点："+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"】 MACD走势为死叉！"
            writeResult2Txt(resultText)
            sql = "insert into btc_x values('%s','死叉',now())" % (UUIDUtil.getUUID())
            DataBaseHandle().updateDB(sql)
            # 自动卖出
            autoByOrSale(open_price,"SALE")
            isUp = False
            isDown = True
            t = threading.Thread(target=reset)
            t.start()




'''
将交易结果写入txt文件中，用于记录
'''
def writeResult2Txt(text):
    with open("../result.txt", "a") as f:#格式化字符串还能这么用！
        f.write(text + "\n")
