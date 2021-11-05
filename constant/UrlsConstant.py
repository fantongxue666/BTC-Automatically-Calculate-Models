
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
    Long_Time = 60
    # 保留金叉和死叉的记录容器 保留最近N次的记录
    Cross_Count = 5
    # 两个时间点的差值在N个时间单位以内
    Cross_TimeLong = 6
    # 记录容器N次的记录，有N-1个时间段，这里是所有时间段中在 Cross_TimeLong 个时间段以内的时间段数量的占比
    Cross_Percent = 0.6
    # 如果已经亏损了10%，则自动卖出，规避价格猛降的风险
    Loss_Percent = 0.1
    # 公共-获取K线数据 Long_Time时间单位
    Get_K_Line = "/api/spot/v3/instruments/BTC-USDT/candles?granularity=" + str(Long_Time)