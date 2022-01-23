import win32com.client
import time
from com.utils import *
import numpy as np
 
# 분차트 관리 클래스
class CMinchartData:
    def __init__(self, interval):
        # interval : 분차트 주기
        self.interval = interval
        self.objCur = {}
        self.data = {}
        self.code = ''
        self.LASTTIME = 1530
 
        # 오늘 날짜
        now = time.localtime()
        self.todayDate = now.tm_year * 10000 + now.tm_mon * 100 + now.tm_mday
 
    def MonCode(self, code):
        self.data = {}
        self.code = code
 
        self.data['O'] = []
        self.data['C'] = []
        self.data['H'] = []
        self.data['L'] = []
        self.data['D'] = []
        self.data['T'] = []
        self.data['LA'] = 0
 
        # 차트 기본 통신
        self.rqChartMinData(code, self.interval)
 
    # 분차트 - 코드, 주기, 개수
    def rqChartMinData(self, code, interval):
        objRq = win32com.client.Dispatch("CpSysDib.StockChart")
 
        objRq.SetInputValue(0, code)  # 종목 코드
        objRq.SetInputValue(1, ord('2'))  # 개수로 조회
        objRq.SetInputValue(4, 26)  # 통신 개수 - 26 : 전일
        objRq.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 날짜,시간, 시가,고가,저가,종가,거래량
        objRq.SetInputValue(6, ord('m'))  # '차트 주가 - 분 데이터
        objRq.SetInputValue(7, interval)  # 차트 주기
        objRq.SetInputValue(9, ord('1'))  # 9 - 수정주가(char)
 
        objRq.BlockRequest()
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        # print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()
 
        len = objRq.GetHeaderValue(3)
 
        for i in range(len):
            day = objRq.GetDataValue(0, i)
            time = objRq.GetDataValue(1, i)
            open = objRq.GetDataValue(2, i)
            high = objRq.GetDataValue(3, i)
            low = objRq.GetDataValue(4, i)
            close = objRq.GetDataValue(5, i)
 
            self.data['D'].append(day)
            self.data['T'].append(time)
            self.data['O'].append(open)
            self.data['H'].append(high)
            self.data['L'].append(low)
            self.data['C'].append(close)

        self.getLowAvg()
    
    def requestLastMinData(self, code):
        objRq = win32com.client.Dispatch("CpSysDib.StockChart")
 
        objRq.SetInputValue(0, code)  # 종목 코드
        objRq.SetInputValue(1, ord('2'))  # 개수로 조회
        objRq.SetInputValue(4, 2)  # 통신 개수 - 2 : 이전 15분봉 2건
        objRq.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 날짜,시간, 시가,고가,저가,종가,거래량
        objRq.SetInputValue(6, ord('m'))  # '차트 주가 - 분 데이터
        objRq.SetInputValue(7, self.interval)  # 차트 주기
        objRq.SetInputValue(9, ord('1'))  # 9 - 수정주가(char)
 
        objRq.BlockRequest()
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        # print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()
 
        mintemp = {}
        mintemp['D'] = []
        mintemp['T'] = []
        mintemp['O'] = []
        mintemp['H'] = []
        mintemp['L'] = []
        mintemp['C'] = []
        len = objRq.GetHeaderValue(3)
 
        for i in range(len):
            day = objRq.GetDataValue(0, i)
            time = objRq.GetDataValue(1, i)
            open = objRq.GetDataValue(2, i)
            high = objRq.GetDataValue(3, i)
            low = objRq.GetDataValue(4, i)
            close = objRq.GetDataValue(5, i)

            mintemp['D'].append(day)
            mintemp['T'].append(time)
            mintemp['O'].append(open)
            mintemp['H'].append(high)
            mintemp['L'].append(low)
            mintemp['C'].append(close)

        return mintemp

    def getLowAvg(self):
        self.data['L'].sort()
        nLen = len(self.data['T'])
        arr = []
        for i in range(nLen):
            if i > 3:
                break
            arr.append(self.data['L'][i])
        
        a = np.array(arr)
        self.data['LA'] = np.mean(a)
    