# coding=gbk

'''
<<<<<<<<<<<< 设置买入条件和卖出条件 >>>>>>>>>>>>>>>>
1，TODO 剩余资产如果低于 XXX美元 ，禁止买入
2，TODO 买入时，要检查其他情况（是否已经出现了死叉，趋势开始下降），要充分减少买入的风险
3，如下情况，禁止卖出
    发生死叉后，下一个时间单位异步执行此交易方法，交易前，看是否在这个时间单位里已经抗完了所有亏损，计算下降幅度方式：（当前时间单位的开盘价 - 上个时间单位的开盘价）/ 上个时间单位的开盘价
    以下情况可以售卖，否则禁止售卖（已经亏损了太多）
        - 币价60000美元左右，下降幅度0.05%内
        - 币价50000美元左右，下降幅度0.04%内
        - 等等各种情况
4，TODO 如果已经亏损了10%，则自动卖出
'''
import datetime

from business import CurrentData
from compute import ComputeMACD, ComputeCross

'''
检查单位时间内开盘价的下降幅度是否超过了预期阈值
'''
def checkDeadLine(lastOpenPrice,openPrice):
    cvalue = int(openPrice) - int(lastOpenPrice)
    # 如果大于0，说明虽然是死叉，但是开盘价却升高了，不排除这种可能性
    if(cvalue >= 0):
        print("cvalue大于0，说明虽然是死叉，但是开盘价却升高了")
        return False
    else:
        down_percent = (-cvalue)/int(lastOpenPrice)
        print("卖出交易时，上一次开盘价："+str(lastOpenPrice)+" 本次开盘价："+str(openPrice))
        print("下降比例："+ str(down_percent*100) + "%")
        if(int(lastOpenPrice) < 65000 and int(lastOpenPrice) > 55000):
            if(down_percent > 0.0005):
                return False
        elif(int(lastOpenPrice) < 55000 and int(lastOpenPrice) > 45000):
            if (down_percent > 0.0004):
                return False
        return True

'''
自动交易
'''
def deal(flag,lastOpenPrice):
    # 获取此刻的新的开盘价
    open_price, close_price, first, second, third = ComputeMACD.getMACD()
    if(flag == True):
        # 金叉 买进
        if(ComputeCross.checkCross()):
            resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 接入交易接口。。。以" + str(open_price) + "的开盘价进行了买入"
            CurrentData.writeResult2Txt(resultText)
    elif(flag == False):
        # 死叉 卖出
        if(ComputeCross.checkCross()):
            if(checkDeadLine(lastOpenPrice,open_price) == False):
                CurrentData.writeResult2Txt("【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】【交易失败】单位时间内下降幅度太大，已经超过预期阈值，卖出可能亏损，系统已自动禁止交易")
            else:
                resultText = "【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 接入交易接口。。。以" + str(open_price) + "的开盘价进行了卖出"
                CurrentData.writeResult2Txt(resultText)
    pass
