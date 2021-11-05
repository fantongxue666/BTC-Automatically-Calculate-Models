# coding=gbk
'''
������������ļ�¼����
�������N�εļ�¼

�����������ֵĽ��/����ʱ�����ر�̣����̼ۼ������
Ŀ�ģ�������/������ֵ����ƣ������Ƶ�������������/��
'''

import datetime
import math

from business import CurrentData
import threading
import time

from constant.UrlsConstant import UrlConstant

crossArray = [] # ��¼����

'''
��ӳ��ֵĽ��/���浽��¼������
'''
def addCross(DIF,DEA):
    currentDataObj = {
        "DIF":DIF,"DEA":DEA,"NOW":datetime.datetime.now()
    }
    if(len(crossArray)>=UrlConstant.Cross_Count):
        # ȥ����һ�����Ӻ��油��һ��
        del crossArray[0]
        crossArray.append(currentDataObj)
    else:
        crossArray.append(currentDataObj)


'''
��������N�γ��ֵĽ��/���������
 ���� N = 2����һ�ν��/�����ʱ��� �� ���ν��/�����ʱ��㣬�������ʱ���Ĳ�ֵ�� ĳ�� ��ʱ�䵥λ���ڣ���˵��������ν��/�����ƽ�����������γ��ֵĽ��/����ʱ�����̣ܶ����̼ۼ�����ȣ�û��̫��ĸ����
 ���� N = 5����5��ʱ��㣬��������ʱ���Ĳ�ֵһ����4����4��������һ�����ʱ�䣬���4����3�����̣ܶ���ô�����ж�Ϊƽ�����ƣ��ܾ�����
'''
def checkCross():
    # ��¼��������С��Nʱ����ֹ����
    if(len(crossArray) < UrlConstant.Cross_Count):
        return False
    timeCountArray = []
    errCount = 0
    for i in range(UrlConstant.Cross_Count - 1):
        # ȡ��һ�γ��ֽ��/�����ʱ���
        lastTime = crossArray[i]["NOW"]
        # ȡ�˴γ��ֽ��/�����ʱ���
        thisTime = crossArray[i + 1]["NOW"]
        # �����ʱ�䵥λ����
        timeCount = (thisTime - lastTime).seconds/UrlConstant.Long_Time
        timeCountArray.append(timeCount)
    for count in timeCountArray:
        if(count < UrlConstant.Cross_TimeLong):
            errCount = errCount + 1
    if(errCount >= math.ceil(UrlConstant.Cross_Count*UrlConstant.Cross_Percent)):
        writeResult2Txt("��ʱ��㣺" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "�� ���ڽ����εĽ��/�����¼���ֽ�Ƶ�����п�����ƽ�����ƣ�ϵͳ���Զ��ܾ�������������ֵ������"+str(UrlConstant.Cross_Count)+"�����/���棬������"+ str(errCount)+"��ʱ���û�г������õ�ʱ�䵥λ���")
        return False
    else:
        return True

'''
�����׽��д��txt�ļ��У����ڼ�¼
'''
def writeResult2Txt(text):
    with open("../result.txt", "a") as f:#��ʽ���ַ���������ô�ã�
        f.write(text + "\n")
