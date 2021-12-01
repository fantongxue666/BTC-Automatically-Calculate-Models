import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(BASE_DIR))

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

