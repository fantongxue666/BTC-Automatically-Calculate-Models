import json
import time
from datetime import datetime
import requests

from constant.UrlsConstant import UrlConstant
from util import LogUtil, EncryptDecryptUtil

# 组装签名
def getSign(methodType,uri,param,timestamp):
    # 时间戳
    message = ""
    if not param:
        message = timestamp + methodType + uri
    else:
        message = timestamp + methodType + uri + json.dumps(param)
        LogUtil.infoAndText("messge",message)
    if message != "":
        sign = EncryptDecryptUtil.get_sign_HmacSHA256(message,"87E888D8B303D67C0D11FAAFF75C9661")
        LogUtil.infoAndText("生成sign签名",sign)
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
    LogUtil.infoAndText("请求地址",UrlConstant.REST_Address + uri)
    LogUtil.infoAndText("请求头信息",json.dumps(headers))
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
    LogUtil.infoAndText("请求地址",UrlConstant.REST_Address + uri)
    LogUtil.infoAndText("请求参数",json.dumps(param))
    LogUtil.infoAndText("请求头信息",json.dumps(headers))
    response = requests.post(UrlConstant.REST_Address + uri,param,headers)
    print("===================================== 请求信息 END ========================================")
    return response.json()
