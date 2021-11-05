# coding=gbk
'''
保留金叉和死叉的记录容器
保留最近N次的记录

现象：连续出现的金叉/死叉时间间隔特别短，开盘价几乎相等
目的：计算金叉/死叉出现的趋势，避免高频率且无意义的买/卖
'''

import datetime
import math

from business import CurrentData
import threading
import time

from constant.UrlsConstant import UrlConstant

crossArray = [] # 记录容器

'''
添加出现的金叉/死叉到记录容器中
'''
def addCross(DIF,DEA):
    currentDataObj = {
        "DIF":DIF,"DEA":DEA,"NOW":datetime.datetime.now()
    }
    if(len(crossArray)>=UrlConstant.Cross_Count):
        # 去掉第一个，从后面补充一个
        del crossArray[0]
        crossArray.append(currentDataObj)
    else:
        crossArray.append(currentDataObj)


'''
计算连续N次出现的金叉/死叉的趋势
 假如 N = 2，上一次金叉/死叉的时间点 和 本次金叉/死叉的时间点，如果两个时间点的差值在 某几 个时间单位以内，则说明最近两次金叉/死叉很平滑（连续两次出现的金叉/死叉时间间隔很短，开盘价几乎相等，没有太多的浮动差）
 假如 N = 5，则5个时间点，任意两个时间点的差值一共有4个，4个都计算一下相隔时间，如果4个有3个都很短，那么可以判定为平滑趋势，拒绝操作
'''
def checkCross():
    # 记录容器数量小于N时，禁止买卖
    if(len(crossArray) < UrlConstant.Cross_Count):
        return False
    timeCountArray = []
    errCount = 0
    for i in range(UrlConstant.Cross_Count - 1):
        # 取上一次出现金叉/死叉的时间点
        lastTime = crossArray[i]["NOW"]
        # 取此次出现金叉/死叉的时间点
        thisTime = crossArray[i + 1]["NOW"]
        # 相隔的时间单位个数
        timeCount = (thisTime - lastTime).seconds/UrlConstant.Long_Time
        timeCountArray.append(timeCount)
    for count in timeCountArray:
        if(count < UrlConstant.Cross_TimeLong):
            errCount = errCount + 1
    if(errCount >= math.ceil(UrlConstant.Cross_Count*UrlConstant.Cross_Percent)):
        writeResult2Txt("【时间点：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 由于近几次的金叉/死叉记录出现较频繁，有可能是平滑趋势，系统已自动拒绝操作，具体数值：相连"+str(UrlConstant.Cross_Count)+"个金叉/死叉，共存在"+ str(errCount)+"个时间段没有超过设置的时间单位宽度")
        return False
    else:
        return True

'''
将交易结果写入txt文件中，用于记录
'''
def writeResult2Txt(text):
    with open("../result.txt", "a") as f:#格式化字符串还能这么用！
        f.write(text + "\n")
