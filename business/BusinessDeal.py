# coding=gbk

'''
<<<<<<<<<<<< ���������������������� >>>>>>>>>>>>>>>>
1��TODO ʣ���ʲ�������� XXX��Ԫ ����ֹ����
2��TODO ����ʱ��Ҫ�������������Ƿ��Ѿ����������棬���ƿ�ʼ�½�����Ҫ��ּ�������ķ���
3�������������ֹ����
    �����������һ��ʱ�䵥λ�첽ִ�д˽��׷���������ǰ�����Ƿ������ʱ�䵥λ���Ѿ����������п��𣬼����½����ȷ�ʽ������ǰʱ�䵥λ�Ŀ��̼� - �ϸ�ʱ�䵥λ�Ŀ��̼ۣ�/ �ϸ�ʱ�䵥λ�Ŀ��̼�
    ����������������������ֹ�������Ѿ�������̫�ࣩ
        - �Ҽ�60000��Ԫ���ң��½�����0.05%��
        - �Ҽ�50000��Ԫ���ң��½�����0.04%��
        - �ȵȸ������
4������Ѿ�������10%�� URLsConstant�н������� �������Զ�����
'''
import datetime

from constant.UrlsConstant import UrlConstant
from util import UUIDUtil
from business import CurrentData
from compute import ComputeMACD, ComputeCross
from constant.DataBaseHandle import DataBaseHandle

'''
��鵥λʱ���ڿ��̼۵��½������Ƿ񳬹���Ԥ����ֵ
'''
def checkDeadLine(lastOpenPrice,openPrice):
    cvalue = int(openPrice) - int(lastOpenPrice)
    # �������0��˵����Ȼ�����棬���ǿ��̼�ȴ�����ˣ����ų����ֿ�����
    if(cvalue >= 0):
        print("cvalue����0��˵����Ȼ�����棬���ǿ��̼�ȴ������")
        return False
    else:
        down_percent = (-cvalue)/int(lastOpenPrice)
        print("��������ʱ����һ�ο��̼ۣ�"+str(lastOpenPrice)+" ���ο��̼ۣ�"+str(openPrice))
        print("�½�������"+ str(down_percent*100) + "%")
        if(int(lastOpenPrice) < 65000 and int(lastOpenPrice) > 55000):
            if(down_percent > 0.0005):
                return False
        elif(int(lastOpenPrice) < 55000 and int(lastOpenPrice) > 45000):
            if (down_percent > 0.0004):
                return False
        return True

'''
�Զ�����
'''
def deal(flag,lastOpenPrice):
    # ��ȡ�˿̵��µĿ��̼�
    open_price, close_price, first, second, third = ComputeMACD.getMACD()
    if(flag == True):
        # ��� ���
        if(ComputeCross.checkCross()):
            resultText = "��ʱ��㣺" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "�� ���뽻�׽ӿڡ�������" + str(open_price) + "�Ŀ��̼۽���������"
            CurrentData.writeResult2Txt(resultText)
            sql = "insert into btc_operation values('%s','%s','buyMoney','����',now(),'������')" % (UUIDUtil.getUUID(),open_price)
            DataBaseHandle().updateDB(sql)
    elif(flag == False):
        # ���� ����
        if(ComputeCross.checkCross()):
            if(checkDeadLine(lastOpenPrice,open_price) == False):
                CurrentData.writeResult2Txt("��ʱ��㣺" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "��������ʧ�ܡ���λʱ�����½�����̫���Ѿ�����Ԥ����ֵ���������ܿ���ϵͳ���Զ���ֹ����")
            else:
                resultText = "��ʱ��㣺" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "�� ���뽻�׽ӿڡ�������" + str(open_price) + "�Ŀ��̼۽���������"
                CurrentData.writeResult2Txt(resultText)
                sql = "insert into btc_operation values('%s','%s','buyMoney','����',now(),'������')" % (UUIDUtil.getUUID(), open_price)
                DataBaseHandle().updateDB(sql)

'''
���������10%���Զ�����
'''
def sale(open_price):
    # ��ѯ���һ������ʱ�Ŀ��̼ۺ�ʵ��֧�����
    sql = "select id,currentPrice,buyMoney from btc_operation where operateName = '����' ORDER BY operateTime desc limit 1"
    data = DataBaseHandle().selectDB(sql)
    if(len(data) == 0):
        return None

    id = data[0][0]
    currentPrice = data[0][1]
    buyMoney = data[0][2]

    # ��������
    if(currentPrice <= open_price):
        return None
    percent = format((currentPrice - open_price)/currentPrice, '.2f')
    if(percent < UrlConstant.Loss_Percent):
        CurrentData.writeResult2Txt("��ʱ��㣺" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "�� �����һ�ι���Ŀ����ʣ����������" + str(percent * 100) + "%")
    else:
        CurrentData.writeResult2Txt("��ʱ��㣺" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "�� �����һ�ι���Ŀ����ʣ����������" + str(percent * 100) + "%������Լ��������"+ str(UrlConstant.Loss_Percent)+"�������Զ����������������ʧ��")
        # �Զ�����
        deal(False,open_price)