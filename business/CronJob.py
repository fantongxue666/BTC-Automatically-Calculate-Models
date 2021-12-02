import uuid
import pymysql
import datetime
import json
import numpy as np
from datetime import datetime
import requests
import base64
import hmac
import os
import hashlib
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

class UrlConstant():
    # ========================== 实盘交易地址 =========================
    # REST
    REST_Address = 'https://www.ouyi.fit'
    # WebSocket公共频道
    WebsocketPub_Address='wss://ws.okex.com:8443/ws/v5/public'
    # WebSocket私有频道
    WebsocketPri_Address='wss://ws.okex.com:8443/ws/v5/private'

    # 定时任务执行单位（秒）
    # [60 180 300 900 1800 3600 7200 14400 21600 43200 86400 604800 2678400 8035200 16070400 31536000]
    # [1min 3min 5min 15min 30min 1hour 2hour 4hour 6hour 12hour 1day 1week 1 month 3 months 6 months and 1 year]
    Long_Time = 2
    # 公共-获取K线数据 Long_Time时间单位
    Get_K_Line = "/api/spot/v3/instruments/BTC-USDT/candles?granularity=3600"


'''
自动交易
flag：true时买入，false时卖出
type：全部/一半
'''
def deal(flag,type):
    # 获取此刻的新的开盘价
    open_price,close_price,fiveday_avg_line,tenday_avg_line,first,second,third = getMACD()
    if(flag == True):
        # 金叉 买进
        sql = "insert into btc_operation values('%s','%s','buyMoney','%s',now(),'创建人')" % (getUUID(),open_price,'买入'+str(type))
        DataBaseHandle().updateDB(sql)
    elif(flag == False):
        # 死叉 卖出
        sql = "insert into btc_operation values('%s','%s','buyMoney','%s',now(),'创建人')" % (getUUID(), open_price,'卖出'+str(type))
        DataBaseHandle().updateDB(sql)

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
            info("【时间点：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前平均线上穿，MACD状态为金叉之后，即将全部买入")
            deal(True,"全部")
        elif(macdValue < 0):
            info("【时间点：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前平均线上穿，MACD状态为死叉之后，即将买入一半")
            deal(True,"一半")
    elif(entityName == "平均线" and entityType == "下穿"):
        if (macdValue > 0):
            info("【时间点：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前平均线下穿，MACD状态为金叉之后，即将卖出一半")
            deal(False, "一半")
        elif (macdValue < 0):
            info("【时间点：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前平均线下穿，MACD状态为死叉之后，即将全部卖出")
            deal(False, "全部")
    elif(entityName == "MACD" and entityType == "金叉"):
        if(avg_status == "上穿"):
            info("【时间点：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD状态为金叉，平均线状态为上穿之后，即将全部买入")
            deal(True,"全部")
        elif(avg_status == "下穿" or avg_status == ""):
            info("【时间点：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD状态为金叉，平均线状态为下穿之后，即将买入一半")
            deal(True,"一半")
    elif(entityName == "MACD" and entityType == "死叉"):
        if (avg_status == "上穿" or avg_status == ""):
            info("【时间点：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD状态为死叉，平均线状态为上穿之后，即将卖出一半")
            deal(False, "一半")
        elif (avg_status == "下穿"):
            info("【时间点：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "】 当前MACD状态为死叉，平均线状态为下穿之后，即将全部卖出")
            deal(False, "全部")

'''
判断走势
'''
def checkDirection(open_price,close_price):
    global lastOpenPrice
    # 打印当前所有状态值
    print("****************************")
    infoAndText("上一次开盘价", str(lastOpenPrice))
    infoAndText("最新开盘价", str(open_price))
    infoAndText("最新收盘价", str(close_price))
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
        sql = "insert into btc_avg values('%s','上穿',now())" % (getUUID())
        DataBaseHandle().updateDB(sql)
        booking("平均线","上穿")
    if (Avg_Avalue > 0 and Avg_Cvalue < 0):
        # 平均线下穿
        sql = "insert into btc_avg values('%s','下穿',now())" % (getUUID())
        DataBaseHandle().updateDB(sql)
        booking("平均线", "下穿")
    # 金叉
    if(Avalue < 0 and Cvalue > 0):
        sql = "insert into btc_x values('%s','金叉',now())" % (getUUID())
        DataBaseHandle().updateDB(sql)
        booking("MACD","金叉")

    # 死叉
    if(Avalue > 0 and Cvalue < 0):
        sql = "insert into btc_x values('%s','死叉',now())" % (getUUID())
        DataBaseHandle().updateDB(sql)
        booking("MACD","死叉")


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
        "DIF":DIF,"DEA":DEA,"NOW":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    avgDataObj = {
        "fiveday_avg_line":fiveday_avg_line,
        "tenday_avg_line":tenday_avg_line,
        "NOW":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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


def calculateMACD(openArray,closeArray,fiveday_avg_line,tenday_avg_line, shortPeriod=12, longPeriod=26, signalPeriod=9):
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
    return open_price,close_price,fiveday_avg_line,tenday_avg_line,fast_values[-1], slow_values[-1], diff_values[-1]    # 返回最新的快慢线和macd值
    # return round(fast_values[-1],5), round(slow_values[-1],5), round(diff_values[-1],5)




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

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)


def getUUID():
    return uuid.uuid1()

def infoAndText(msg,obj):
    try:
        print(msg+"："+json.dumps(obj,cls=DateEncoder.DateEncoder))
    except:
        print(msg+"："+obj)
def info(text):
    print(text)
    sql = "insert into btc_log values('%s','%s',now())" % (getUUID(), text)
    DataBaseHandle().updateDB(sql)

# 组装签名
def getSign(methodType,uri,param,timestamp):
    # 时间戳
    message = ""
    if not param:
        message = timestamp + methodType + uri
    else:
        message = timestamp + methodType + uri + json.dumps(param)
        infoAndText("messge",message)
    if message != "":
        sign = get_sign_HmacSHA256(message,"87E888D8B303D67C0D11FAAFF75C9661")
        infoAndText("生成sign签名",sign)
        return sign
    return None

# 发起GET请求 返回JSON格式的响应
def sendRequest_GET(uri):
    print("==================================== 请求信息 BEGIN =======================================")
    timestamp = str(datetime.utcnow().isoformat())
    headers = {
        'OK-ACCESS-KEY':'ecbd3367-3f5b-4c1c-b18f-6442dbeb3389',
        'OK-ACCESS-SIGN':getSign('POST',uri,None,timestamp),
        'OK-ACCESS-TIMESTAMP':timestamp,
        'OK-ACCESS-PASSPHRASE':'aini12345'
    }
    infoAndText("请求地址",UrlConstant.REST_Address + uri)
    infoAndText("请求头信息",json.dumps(headers))
    response = requests.get(UrlConstant.REST_Address + uri,headers)
    print("===================================== 请求信息 END ========================================")
    return response.json()

# 发起POST请求 返回JSON格式的响应
def sendRequest_POST(uri,param):
    print("==================================== 请求信息 BEGIN =======================================")
    timestamp = str(datetime.utcnow().isoformat())
    headers = {
        'OK-ACCESS-KEY':'ecbd3367-3f5b-4c1c-b18f-6442dbeb3389',
        'OK-ACCESS-SIGN':getSign('POST',uri,param,timestamp),
        'OK-ACCESS-TIMESTAMP':timestamp,
        'OK-ACCESS-PASSPHRASE':'aini12345'
    }
    infoAndText("请求地址",UrlConstant.REST_Address + uri)
    infoAndText("请求参数",json.dumps(param))
    infoAndText("请求头信息",json.dumps(headers))
    response = requests.post(UrlConstant.REST_Address + uri,param,headers)
    print("===================================== 请求信息 END ========================================")
    return response.json()


def getAbsolutePath(fileName):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir_path,fileName)
    return path


# md5鍔犲瘑锛堢敤鎴峰瘑鐮侊級
def encryptMd5(message):
    hl = hashlib.md5()
    hl.update(message.encode(encoding='utf-8'))
    return hl.hexdigest()

# 浣跨敤HmacSHA256绠楁硶鍝堝笇(鍝堝笇绉橀挜涓簊ecret)锛屽啀瀵筯ash鍊间娇鐢˙ase64鍔犲瘑寰楀埌鏈€缁堢殑绛惧悕鍊約ign
def get_sign_HmacSHA256(message, secret):
    secrets = secret.encode('utf-8')
    messageNew = message.encode('utf-8')
    sign = base64.b64encode(hmac.new(secrets, messageNew, digestmod=hashlib.sha256).digest())
    sign = str(sign, 'utf-8')
    print(sign)
    return sign


def getMACD():
    data = sendRequest_GET(UrlConstant.Get_K_Line)
    # 得到收盘价的数组
    closeArray = [float(i[4]) for i in data]
    avgValue = 0
    for i in range(5):
        avgValue += closeArray[i]
    fiveday_avg_line = avgValue/5
    avgValue = 0
    for i in range(10):
        avgValue += closeArray[i]
    tenday_avg_line = avgValue / 10
    # 得到开盘价的数组
    openArray = [float(i[1]) for i in data]
    # 顺序反转
    closeArray.reverse()
    openArray.reverse()
    return calculateMACD(openArray,closeArray,fiveday_avg_line,tenday_avg_line)


@sched.scheduled_job('interval', id='my_job_id', seconds=UrlConstant.Long_Time)
def job_function():
    # 计算MACD值，得到开盘价，收盘价等值
    open_price,close_price,fiveday_avg_line,tenday_avg_line,first,second,third = getMACD()
    # 监控金叉/死叉的发生时机，自动进行买入和卖出
    addCurrentDataObj(first, second,third, open_price, close_price,fiveday_avg_line,tenday_avg_line)

# 开始
sched.start()







