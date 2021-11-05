import datetime
import json
import threading
import time

from business import BusinessDeal
from compute import ComputeCross
from constant.UrlsConstant import UrlConstant
from util import LogUtil

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
保证currentDataObjList数组中只保存三个对象，三个时刻的数据
第一个：上上一个时间单位的数据
第二个，上一个时间单位的数据
第三个，当前时间单位的数据
'''
def addCurrentDataObj(DIF,DEA,open_price,close_price):
    currentDataObj = {
        "DIF":DIF,"DEA":DEA,"NOW":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if(len(currentDataObjList)>=3):
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
自动买入或抛出
'''
def autoByOrSale(open_price,operation,delay):
    time.sleep(delay)
    # 买之前先判断上次买入的价格，和此次要卖出的价格
    global buyedPrice
    if(operation == "BUY"):
        # 买入
        buyedPrice = open_price
        BusinessDeal.deal(True, open_price)
    elif(operation == "SALE"):
        # 卖出
        BusinessDeal.deal(False, open_price)
    else:
        print("operation参数有误，不做任何处理")
'''
判断走势
DIF线和DEA线在零轴之下形成金叉：市场此时仍然是空头主导，所以说虽然形成了金叉，但是由于“格局作用”市场还是偏弱的甚至有可能创出新低。在这个时候去参与还是谨慎为主，仓位控制在30%以下。
DIF线和DEA线在零轴之上形成金叉：这时候市场的趋势性行情基本确立，表明多头迹象明显，之前仓位较轻，现在可以考虑加仓。
DIF线和DEA线在零轴之下形成死叉：这时候的市场主要是空头在主导，市场偏弱，必须要马上止损或是空仓了结，观望为主。
DIF线和DEA线在零轴之上形成死叉：虽然此时是多方力量在主导，但是多头有走弱的迹象，可以考虑获利减仓一部分，落袋为安，防止风险失控。
其实除了以上比较典型的情况之外，DIF线和DEA线上穿和下穿零轴也是有多空交替和转换的迹象，我们操作中可以适当的根据多空交易转化来控制仓位和风险。
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
    # 上上一个单位的快线值 - 慢线值
    Avalue = int(currentDataObjList[0]['DIF']) - int(currentDataObjList[0]['DEA'])
    # 上一个单位的快线值 - 慢线值
    Bvalue = int(currentDataObjList[1]['DIF']) - int(currentDataObjList[1]['DEA'])
    # 当前单位的快线值 - 慢线值
    Cvalue = int(currentDataObjList[2]['DIF']) - int(currentDataObjList[2]['DEA'])

    # 金叉
    if(Avalue < 0 and Cvalue > 0):
        # 添加金叉到金叉/死叉记录容器中
        ComputeCross.addCross(currentDataObjList[1]['DIF'],currentDataObjList[1]['DEA'])
        print("isUp",isUp)
        if(isUp == False):
                resultText = "【时间点："+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"】 MACD走势为金叉，有价格上升的趋势，等待"+str(UrlConstant.Long_Time)+"秒之后自动交易！"
                writeResult2Txt(resultText)
                # 下一个时间单位进行交易 异步执行，延迟一个时间单位执行
                t = threading.Thread(target=autoByOrSale, args=(open_price,"BUY",UrlConstant.Long_Time))
                t.start()
                isUp = True
                isDown = False
                t = threading.Thread(target=reset)
                t.start()
    # 死叉
    if(Avalue > 0 and Cvalue < 0):
        # 添加死叉到金叉死叉记录容器中
        ComputeCross.addCross(currentDataObjList[1]['DIF'], currentDataObjList[1]['DEA'])
        print("isDown",isDown)
        if(isDown == False):
            resultText = "【时间点："+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"】 MACD走势为死叉，有价格下降的趋势，等待"+str(UrlConstant.Long_Time)+"秒之后自动交易！"
            writeResult2Txt(resultText)
            # 下一个时间单位进行交易 异步执行，延迟一个时间单位执行
            t = threading.Thread(target=autoByOrSale, args=(open_price, "SALE", UrlConstant.Long_Time))
            t.start()
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
