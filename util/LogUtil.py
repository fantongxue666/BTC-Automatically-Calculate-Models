from flask import json

from util import DateEncoder


def infoAndText(msg,obj):
    try:
        print(msg+"："+json.dumps(obj,cls=DateEncoder.DateEncoder))
    except:
        print(msg+"："+obj)
def info(obj):
    try:
        print(json.dumps(obj,cls=DateEncoder.DateEncoder))
    except:
        print(obj)

