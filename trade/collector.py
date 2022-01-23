import win32com.client
import pandas as pd
from datetime import datetime
from com.utils import *
import time
 
# 크레온 플러스 공통 OBJECT
cpCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
cpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
cpOhlc = win32com.client.Dispatch('CpSysDib.StockChart')

def get_ohlc(code, qty):
    """인자로 받은 종목의 OHLC 가격 정보를 qty 개수만큼 반환한다."""
    cpOhlc.SetInputValue(0, code)           # 종목코드
    cpOhlc.SetInputValue(1, ord('2'))        # 1:기간, 2:개수
    cpOhlc.SetInputValue(4, qty)             # 요청개수
    cpOhlc.SetInputValue(5, [0, 2, 3, 4, 5, 8]) # 0:날짜, 2~5:OHLC
    cpOhlc.SetInputValue(6, ord('D'))        # D:일단위
    cpOhlc.SetInputValue(9, ord('1'))        # 0:무수정주가, 1:수정주가
    cpOhlc.BlockRequest()
    count = cpOhlc.GetHeaderValue(3)   # 3:수신개수
    columns = ['open', 'high', 'low', 'close', 'vol']
    index = []
    rows = []

    for i in range(count): 
        index.append(cpOhlc.GetDataValue(0, i)) 
        rows.append([cpOhlc.GetDataValue(1, i), cpOhlc.GetDataValue(2, i),
            cpOhlc.GetDataValue(3, i), cpOhlc.GetDataValue(4, i), cpOhlc.GetDataValue(5, i)]) 
    df = pd.DataFrame(rows, columns=columns, index=index) 
    return df

def getVolMax(volarr):
    max = 0
    for vol in volarr:
        if max < vol:
            max = vol
    return max

def get_movingaverage(code, window):
    """인자로 받은 종목에 대한 이동평균가격을 반환한다."""
    try:
        time_now = datetime.now()
        str_today = time_now.strftime('%Y%m%d')
        ohlc = get_ohlc(code, window)  # 120 + 16 날짜별 데이터 추출

        if len(ohlc.index) < window:
            return None, None, None, None

        # if str_today == str(ohlc.iloc[0].name):
        #     lastday = ohlc.iloc[1].name
        # else:
        #     lastday = ohlc.iloc[0].name
        lastday = ohlc.iloc[0].name

        closes = ohlc['close'].sort_index()         
        vols = ohlc['vol'].sort_index()

        ma20 = closes.rolling(20).mean()
        ma60 = closes.rolling(60).mean()
        ma120 = closes.rolling(120).mean()
        bf3d_m20 = ma20.loc[ohlc.iloc[3].name]
        bf3d_m60 = ma60.loc[ohlc.iloc[3].name]
        bf3d_m120 = ma120.loc[ohlc.iloc[3].name]
        bf7d_m20 = ma20.loc[ohlc.iloc[7].name]
        bf7d_m60 = ma60.loc[ohlc.iloc[7].name]
        bf7d_m120 = ma120.loc[ohlc.iloc[7].name]
        bf15d_m20 = ma20.loc[ohlc.iloc[15].name]
        bf15d_m60 = ma60.loc[ohlc.iloc[15].name]
        bf15d_m120 = ma120.loc[ohlc.iloc[15].name]
        
        if round(bf3d_m20, 2) > round(bf3d_m60, 2) and round(bf3d_m60, 2) > round(bf3d_m120, 2) \
            and round(bf7d_m20, 2) > round(bf7d_m60, 2) and round(bf7d_m60, 2) > round(bf7d_m120, 2) \
            and round(bf15d_m20, 2) > round(bf15d_m60, 2) and round(bf15d_m60, 2) > round(bf15d_m120, 2):

            vol30arr = vols.tail(30).array      # 최근 30일 거래량의 최대값 추가
            return code, closes[lastday], vols[lastday], getVolMax(vol30arr)
        else:
            return None, None, None, None

    except Exception as ex:
        print(datetime.now().strftime('[%m/%d %H:%M:%S]'), 'get_movingavrg(' + str(window) + ') -> exception! ' + str(ex))
        
        return None

class CMarketTotal():
    def __init__(self):
        self.dataInfo = {}
        self.targetItems = {}
 
        self.targetItems['code'] = []
        self.targetItems['name'] = []
        self.targetItems['lastclose'] = []
        self.targetItems['vol'] = []
        self.targetItems['sprice'] = []
        self.targetItems['lastmaxvol'] = []
 
    def get_target_items(self):
        codeList = cpCodeMgr.GetStockListByMarket(1)  # 거래소
        codeList2 = cpCodeMgr.GetStockListByMarket(2)  # 코스닥
        allcodelist = codeList + codeList2
        #print('전 종목 코드 %d, 거래소 %d, 코스닥 %d' % (len(allcodelist), len(codeList), len(codeList2)))
 
        objMarket = CpMarketEye()
        rqCodeList = []
        for i, code in enumerate(allcodelist):
            rqCodeList.append(code)
            if len(rqCodeList) == 200:
                time.sleep(1)
                objMarket.request(rqCodeList, self.dataInfo)
                rqCodeList = []
                continue
 
        if len(rqCodeList) > 0:
            objMarket.request(rqCodeList, self.dataInfo)

        # print(self.dataInfo)
        for key in self.dataInfo.keys():
            finalcode, close, vol, vol30max = get_movingaverage(key, 136)
            if finalcode:
                self.targetItems['code'].append(finalcode)
                self.targetItems['name'].append(cpCodeMgr.CodeToName(finalcode))
                self.targetItems['lastclose'].append(close)
                self.targetItems['vol'].append(vol)
                self.targetItems['lastmaxvol'].append(vol30max)                

        return self.targetItems
        #slack.chat.post_message('#stock', ' '.join(self.targetItems))

class CpMarketEye:
    def __init__(self):
        self.objRq = win32com.client.Dispatch("CpSysDib.MarketEye")
        self.RpFiledIndex = 0
 
    def request(self, codes, dataInfo):
        # 0: 종목코드 4: 현재가 10:거래량 22 : 전일거래량, 23: 전일종가
        rqField = [0, 4, 10, 22, 23]  # 요청 필드
 
        self.objRq.SetInputValue(0, rqField)  # 요청 필드
        self.objRq.SetInputValue(1, codes)  # 종목코드 or 종목코드 리스트
        self.objRq.BlockRequest()
 
        # 현재가 통신 및 통신 에러 처리
        rqStatus = self.objRq.GetDibStatus()
        if rqStatus != 0:
            return False
 
        cnt = self.objRq.GetHeaderValue(2) # 0 : 필드개수, 1: 필드명배열, 2: 종목개수
        
        for i in range(cnt):
            code = self.objRq.GetDataValue(0, i)  # 코드
            cur_price = self.objRq.GetDataValue(1, i)  # 현재가
            trade_amt = self.objRq.GetDataValue(2, i)  # 거래량
            bf_trade_amt = self.objRq.GetDataValue(3, i)  # 전일 거래량
            bf_price = self.objRq.GetDataValue(4, i)  # 전일 종가

            ## TODO : 전일 or 당일 오전 조회에 따른 판단 분기

            # 1. 전일 종가 대비 11% 이상 급등 
            per = 0
            if bf_price > 0:
                per = ((cur_price - bf_price) / bf_price) * 100.0

            # 2. 전일 거래량 조건
            if trade_amt > 2000000 and per > 11.0:
                dataInfo[code] = (cur_price, trade_amt)
            
        return True

