from apscheduler.schedulers.blocking import BlockingScheduler

from compute import ComputeMACD
from business import CurrentData
from constant.UrlsConstant import UrlConstant

sched = BlockingScheduler()

@sched.scheduled_job('interval', id='my_job_id', seconds=UrlConstant.Long_Time)
def job_function():
    open_price,close_price,first,second,third = ComputeMACD.getMACD()
    CurrentData.addCurrentDataObj(first, second, open_price, close_price)
# 开始
sched.start()


