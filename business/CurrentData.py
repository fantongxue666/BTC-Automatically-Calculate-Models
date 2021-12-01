import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(BASE_DIR))

import datetime
from util import UUIDUtil
from compute import ComputeMACD
from util import LogUtil
from config.DataBaseHandle import DataBaseHandle

currentDataObjList = []
avgDataList = []
global buyedPrice
global macdValue
global lastOpenPrice
buyedPrice = 0 # 上一次购买的价格（以开盘价为基准）
lastOpenPrice = 0
macdValue = 0

'''
DIF：快线值
DEA：慢线值
MACD：macd值
open_price：开盘价
close_price：收盘价
fiveday_avg_line：5日平均线值
tenday_avg_line：10日平均线值
NOW：当前时间
保证currentDataObjList数组中只保存两个对象，两个时刻的数据
第1个，上一个时间单位的数据
第2个，当前时间单位的数据
'''
def addCurrentDataObj(DIF,DEA,MACD,open_price,close_price,fiveday_avg_line,tenday_avg_line):
    global macdValue
    global global_fiveday_avg_line
    global global_tenday_avg_line
    global isFiveTenUp
    global isFiveTenDown
    global_fiveday_avg_line = float('%.1f' % fiveday_avg_line)
    global_tenday_avg_line = float('%.1f' % tenday_avg_line)
    macdValue = MACD
    currentDataObj = {
        "DIF":DIF,"DEA":DEA,"NOW":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    avgDataObj = {
        "fiveday_avg_line":fiveday_avg_line,
        "tenday_avg_line":tenday_avg_line,
        "NOW":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if(len(currentDataObjList)>=2):
        # 去掉第一个，从后面补充一个
        del currentDataObjList[0]
        currentDataObjList.append(currentDataObj)
        # 更新金叉/死叉的状态
        checkDirection(open_price,close_price)
    else:
        currentDataObjList.append(currentDataObj)
    if(len(avgDataList)>=2):
        del avgDataList[0]
        avgDataList.append(avgDataObj)
    else:
        avgDataList.append(avgDataObj)

'''
判断走势
'''
def checkDirection(open_price,close_price):
    global lastOpenPrice
    # 打印当前所有状态值
    print("****************************")
    LogUtil.infoAndText("上一次开盘价", str(lastOpenPrice))
    LogUtil.infoAndText("最新开盘价", str(open_price))
    LogUtil.infoAndText("最新收盘价", str(close_price))
    print("5日平均线值：" + str(global_fiveday_avg_line))
    print("10日平均线值：" + str(global_tenday_avg_line))
    print("****************************")
    lastOpenPrice = open_price
    # 上一个单位的快线值 - 慢线值
    Avalue = int(currentDataObjList[0]['DIF']) - int(currentDataObjList[0]['DEA'])
    # 当前单位的快线值 - 慢线值
    Cvalue = int(currentDataObjList[1]['DIF']) - int(currentDataObjList[1]['DEA'])

    Avg_Avalue = int(avgDataList[0]['fiveday_avg_line']) - int(avgDataList[0]['tenday_avg_line'])
    Avg_Cvalue = int(avgDataList[1]['fiveday_avg_line']) - int(avgDataList[1]['tenday_avg_line'])
    if(Avg_Avalue < 0 and Avg_Cvalue > 0):
        # 平均线上穿
        sql = "insert into btc_avg values('%s','上穿',now())" % (UUIDUtil.getUUID())
        DataBaseHandle().updateDB(sql)
        booking("平均线","上穿")
    if (Avg_Avalue > 0 and Avg_Cvalue < 0):
        # 平均线下穿
        sql = "insert into btc_avg values('%s','下穿',now())" % (UUIDUtil.getUUID())
        DataBaseHandle().updateDB(sql)
        booking("平均线", "下穿")
    # 金叉
    if(Avalue < 0 and Cvalue > 0):
        sql = "insert into btc_x values('%s','金叉',now())" % (UUIDUtil.getUUID())
        DataBaseHandle().updateDB(sql)
        booking("MACD","金叉")

    # 死叉
    if(Avalue > 0 and Cvalue < 0):
        sql = "insert into btc_x values('%s','死叉',now())" % (UUIDUtil.getUUID())
        DataBaseHandle().updateDB(sql)
        booking("MACD","死叉")

'''
查询状态，根据不同情况进行交易
交易开关
entityName 实体对象，是MACD还是平均线
entityType 实体类型，是上穿/金叉还是下穿/死叉
'''
def booking(entityName,entityType):
    global macdValue
    # 查看平均线的情况
    sql = "select * from btc_avg order by avgTime desc limit 10"
    data = DataBaseHandle().selectDB(sql)
    avg_status = None
    if (len(data) > 0):
        avg_status = data[0][1]
    else:
        avg_status = ""
    if(entityName == "平均线" and entityType == "上穿"):
        if(macdValue > 0):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前平均线上穿，MACD状态为金叉之后，即将全部买入"
            writeResult2Txt(resultText)
            deal(True,"全部")
        elif(macdValue < 0):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前平均线上穿，MACD状态为死叉之后，即将买入一半"
            writeResult2Txt(resultText)
            deal(True,"一半")
    elif(entityName == "平均线" and entityType == "下穿"):
        if (macdValue > 0):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前平均线下穿，MACD状态为金叉之后，即将卖出一半"
            writeResult2Txt(resultText)
            deal(False, "一半")
        elif (macdValue < 0):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前平均线下穿，MACD状态为死叉之后，即将全部卖出"
            writeResult2Txt(resultText)
            deal(False, "全部")
    elif(entityName == "MACD" and entityType == "金叉"):
        if(avg_status == "上穿"):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD状态为金叉，平均线状态为上穿之后，即将全部买入"
            writeResult2Txt(resultText)
            deal(True,"全部")
        elif(avg_status == "下穿" or avg_status == ""):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD状态为金叉，平均线状态为下穿之后，即将买入一半"
            writeResult2Txt(resultText)
            deal(True,"一半")
    elif(entityName == "MACD" and entityType == "死叉"):
        if (avg_status == "上穿" or avg_status == ""):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD状态为死叉，平均线状态为上穿之后，即将卖出一半"
            writeResult2Txt(resultText)
            deal(False, "一半")
        elif (avg_status == "下穿"):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD状态为死叉，平均线状态为下穿之后，即将全部卖出"
            writeResult2Txt(resultText)
            deal(False, "全部")


'''
自动交易
flag：true时买入，false时卖出
type：全部/一半
'''
def deal(flag,type):
    # 获取此刻的新的开盘价
    open_price,close_price,fiveday_avg_line,tenday_avg_line,first,second,third = ComputeMACD.getMACD()
    if(flag == True):
        # 金叉 买进
        resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 接入交易接口，以" + str(open_price) + "的开盘价买入" + str(type)
        writeResult2Txt(resultText)
        # sql = "insert into btc_operation values('%s','%s','buyMoney','买入',now(),'创建人')" % (UUIDUtil.getUUID(),open_price)
        # DataBaseHandle().updateDB(sql)
    elif(flag == False):
        # 死叉 卖出
        resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 接入交易接口，以" + str(open_price) + "的开盘价卖出" + str(type)
        writeResult2Txt(resultText)
        # sql = "insert into btc_operation values('%s','%s','buyMoney','卖出',now(),'创建人')" % (UUIDUtil.getUUID(), open_price)
        # DataBaseHandle().updateDB(sql)


'''
将交易结果写入txt文件中，用于记录
'''
def writeResult2Txt(text):
    with open("../result.txt", "a") as f:#格式化字符串还能这么用！
        f.write(text + "\n")
