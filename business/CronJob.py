import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(BASE_DIR))

from apscheduler.schedulers.blocking import BlockingScheduler
from compute import ComputeMACD
from business import CurrentData
from config.UrlsConstant import UrlConstant

sched = BlockingScheduler()

@sched.scheduled_job('interval', id='my_job_id', seconds=UrlConstant.Long_Time)
def job_function():
    # 计算MACD值，得到开盘价，收盘价等值
    open_price,close_price,fiveday_avg_line,tenday_avg_line,first,second,third = ComputeMACD.getMACD()
    # 监控金叉/死叉的发生时机，自动进行买入和卖出
    CurrentData.addCurrentDataObj(first, second,third, open_price, close_price,fiveday_avg_line,tenday_avg_line)

# 开始
sched.start()


