from apscheduler.schedulers.blocking import BlockingScheduler

from compute import ComputeMACD
from business import CurrentData, BusinessDeal
from constant.UrlsConstant import UrlConstant

sched = BlockingScheduler()

@sched.scheduled_job('interval', id='my_job_id', seconds=UrlConstant.Long_Time)
def job_function():
    # 计算MACD值，得到开盘价，收盘价等值
    open_price,close_price,first,second,third = ComputeMACD.getMACD()
    # 如果上次的买入亏损达到10%，自动卖出
    BusinessDeal.sale(open_price)
    # 监控金叉/死叉的发生时机，自动进行买入和卖出
    CurrentData.addCurrentDataObj(first, second, open_price, close_price)

# 开始
sched.start()


