import numpy as np
import json
from config.UrlsConstant import UrlConstant
import talib
from util import RequestUtil

def calculateEMA(period, closeArray, emaArray=[]):
    length = len(closeArray)
    nanCounter = np.count_nonzero(np.isnan(closeArray))
    if not emaArray:
        emaArray.extend(np.tile([np.nan], (nanCounter + period - 1)))
        firstema = np.mean(closeArray[nanCounter:nanCounter + period - 1])
        emaArray.append(firstema)
        for i in range(nanCounter + period, length):
            ema = (2 * closeArray[i] + (period - 1) * emaArray[-1]) / (period + 1)
            emaArray.append(ema)
    return np.array(emaArray)


def calculateMACD(openArray,closeArray, shortPeriod=12, longPeriod=26, signalPeriod=9):
    ema12 = calculateEMA(shortPeriod, closeArray, [])
    ema26 = calculateEMA(longPeriod, closeArray, [])
    diff = ema12 - ema26

    dea = calculateEMA(signalPeriod, diff, [])
    macd = (diff - dea)*2

    fast_values = diff   # 快线
    slow_values = dea    # 慢线
    diff_values = macd   # macd
    # return fast_values, slow_values, diff_values  # 返回所有的快慢线和macd值
    # 获取最新的开盘价和收盘价
    open_price = openArray[len(openArray) - 1]
    close_price = closeArray[len(closeArray) - 1]
    return open_price,close_price,fast_values[-1], slow_values[-1], diff_values[-1]    # 返回最新的快慢线和macd值
    # return round(fast_values[-1],5), round(slow_values[-1],5), round(diff_values[-1],5)

def getMACD():
    data = RequestUtil.sendRequest_GET(UrlConstant.Get_K_Line)
    # 得到收盘价的数组
    closeArray = [float(i[4]) for i in data]
    print("5日移动平均线值：" + talib.SMA(closeArray,timepreriod=5))

    # 得到开盘价的数组
    openArray = [float(i[1]) for i in data]
    # 顺序反转
    closeArray.reverse()
    openArray.reverse()
    return calculateMACD(openArray,closeArray)

