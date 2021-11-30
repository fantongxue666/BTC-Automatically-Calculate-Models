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
avgDataList = []
global isDown
global isUp
global buyedPrice
global lastOpenPrice
global global_fiveday_avg_line
global global_tenday_avg_line
global isFiveTenUp
global isFiveTenDown
isDown = False # 是否发生了死叉
isUp = False   # 是否发生了金叉
isFiveTenUp = False # 5日均线是否上穿10日均线
isFiveTenDown = False # 5日均线是否下穿10日均线
buyedPrice = 0 # 上一次购买的价格（以开盘价为基准）
lastOpenPrice = 0

'''
重置所有状态
'''
def resetData():
    global isDown
    global isUp
    global isFiveTenUp
    global isFiveTenDown
    isDown = False
    isUp = False
    isFiveTenUp = False
    isFiveTenDown = False

'''
DIF：快线值
DEA：慢线值
open_price：开盘价
close_price：收盘价
fiveday_avg_line：5日平均线值
tenday_avg_line：10日平均线值
NOW：当前时间
保证currentDataObjList数组中只保存两个对象，两个时刻的数据
第1个，上一个时间单位的数据
第2个，当前时间单位的数据
'''
def addCurrentDataObj(DIF,DEA,open_price,close_price,fiveday_avg_line,tenday_avg_line):
    global global_fiveday_avg_line
    global global_tenday_avg_line
    global isFiveTenUp
    global isFiveTenDown
    global_fiveday_avg_line = float('%.1f' % fiveday_avg_line)
    global_tenday_avg_line = float('%.1f' % tenday_avg_line)
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
        # 如果状态【金叉 + {5日 - 10日 > 0}】 则全部买入  如果二者只满足其一，则买入一半
        if((isUp == True and isDown == False) and isFiveTenUp == True and isFiveTenDown == False):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD形式为金叉，MA平均线也走上，自动交易【全部买入】"
            writeResult2Txt(resultText)
            deal(True,"全部")
        # elif((isUp == False and isUp == True)  and isFiveTenUp == True and isFiveTenDown == False):
        #     resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD形式为死叉，但MA平均线走上，自动交易【买入一半】"
        #     writeResult2Txt(resultText)
        #     deal(True, "一半")
        # 如果状态【死叉 + {5日 - 10日 < 0}】 则全部卖出  如果二者只满足其一，则卖出一半
        elif ((isDown == True and isUp == False) and isFiveTenUp == False and isFiveTenDown == True):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD形式为死叉，MA平均线也走下，自动交易【卖出全部】"
            writeResult2Txt(resultText)
            deal(False, "全部")
        # elif ((isDown == False and isUp == True) and isFiveTenUp == False and isFiveTenDown == True):
        #     resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD形式为金叉，但MA平均线走下，自动交易【卖出一半】"
        #     writeResult2Txt(resultText)
        #     deal(False, "一半")
        else:
            print("不做处理")

    else:
        currentDataObjList.append(currentDataObj)
    if(len(avgDataList)>=2):
        del avgDataList[0]
        avgDataList.append(avgDataObj)
    else:
        avgDataList.append(avgDataObj)

'''
自动交易
flag：true时买入，false时卖出
type：全部/一半
'''
def deal(flag,type):
    # 获取此刻的新的开盘价
    open_price, close_price, first, second, third = ComputeMACD.getMACD()
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
    # 购买后重置所有状态
    resetData()

'''
判断走势
'''
def checkDirection(open_price,close_price):
    global isDown
    global isUp
    global isFiveTenUp
    global isFiveTenDown
    global lastOpenPrice
    # LogUtil.infoAndText("当前时间单位数据",json.dumps(currentDataObjList))
    # 打印当前所有状态值
    print("****************************")
    LogUtil.infoAndText("上一次开盘价", str(lastOpenPrice))
    LogUtil.infoAndText("最新开盘价", str(open_price))
    LogUtil.infoAndText("最新收盘价", str(close_price))
    print("是否发生金叉：" + str(isUp))
    print("是否发生死叉：" + str(isDown))
    print("5日平均线值：" + str(global_fiveday_avg_line))
    print("10日平均线值：" + str(global_tenday_avg_line))
    print("5日平均线是否上穿10日平均线：" + str(isFiveTenUp))
    print("5日平均线是否下穿10日平均线：" + str(isFiveTenDown))
    print("****************************")
    lastOpenPrice = open_price
    # 上一个单位的快线值 - 慢线值
    Avalue = int(currentDataObjList[0]['DIF']) - int(currentDataObjList[0]['DEA'])
    # 当前单位的快线值 - 慢线值
    Cvalue = int(currentDataObjList[1]['DIF']) - int(currentDataObjList[1]['DEA'])

    Avg_Avalue = int(avgDataList[0]['fiveday_avg_line']) - int(avgDataList[0]['tenday_avg_line'])
    Avg_Cvalue = int(avgDataList[1]['fiveday_avg_line']) - int(avgDataList[1]['tenday_avg_line'])
    if(Avg_Avalue < 0 and Avg_Cvalue > 0):
        isFiveTenUp = True
        isFiveTenDown = False
    if (Avg_Avalue > 0 and Avg_Cvalue < 0):
        isFiveTenUp = False
        isFiveTenDown = True


    # 金叉
    if(Avalue < 0 and Cvalue > 0):
        isUp = True
        isDown = False
        if ((isUp == True and isDown == False) and isFiveTenUp == True and isFiveTenDown == False):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD形式为金叉，MA平均线也走上，自动交易【全部买入】"
            writeResult2Txt(resultText)
            deal(True, "全部")
        # elif ((isUp == True and isDown == False) and isFiveTenUp == False and isFiveTenDown == True):
        #     resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD形式为金叉，但MA平均线走下，自动交易【卖出一半】"
        #     writeResult2Txt(resultText)
        #     deal(False, "一半")

    # 死叉
    if(Avalue > 0 and Cvalue < 0):
        isUp = False
        isDown = True
        # if((isUp == False and isDown == True) and isFiveTenUp == True and isFiveTenDown == False):
        #     resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD形式为死叉，但MA平均线走上，自动交易【买入一半】"
        #     writeResult2Txt(resultText)
        #     deal(True, "一半")
        if((isUp == False and isDown == True) and isFiveTenUp == False and isFiveTenDown == True):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD形式为死叉，MA平均线也走下，自动交易【卖出全部】"
            writeResult2Txt(resultText)
            deal(False, "全部")

'''
将交易结果写入txt文件中，用于记录
'''
def writeResult2Txt(text):
    with open("../result.txt", "a") as f:#格式化字符串还能这么用！
        f.write(text + "\n")
