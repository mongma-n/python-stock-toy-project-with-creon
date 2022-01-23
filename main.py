import sys
from trade.collector import *
from trade.analyser import *
from com.getprice import *
from datetime import datetime
from com.utils import *
import time

if __name__ == "__main__":
    try:
        # plus 상태 체크
        if check_creon_system == False:
            exit()

        slog('[0] Trader start...')
        
        buyItems = {}
        buyItems["code"] = []
        buyItems["open"] = []
        buyItems["close"] = []
        buyItems["support"] = []
        buyItems["status"] = '0'    # 0 : 초기, 1 : 1차종목추출, 2 : 2차종목추출, 3차 : 분석완료, 00 : 매수
        
        # AM 08:30 ~ 09:00 : Day Collector 1차 매수 종목 추출 (collector start)
        objMarketTotal = CMarketTotal()
        objStockMst = CpStockMst()
        minData = CMinchartData(15)

        #################################################################################
        ### TEST CODE
        #################################################################################

        # AM 08:30 ~ 09:00 : Day Collector 1차 매수 종목 추출 (collector start)
        # AM 08:30 ~ 09:00 : Min Collector 2차 매수 종목 추출 (buyItems 생성)
        objMarketTotal.get_target_items()
        codes = objMarketTotal.targetItems["code"]
        vol = objMarketTotal.targetItems["vol"]
        lastclose = objMarketTotal.targetItems["lastclose"]
        vol30max = objMarketTotal.targetItems["lastmaxvol"]
        for i, code in enumerate(codes):
            if (vol[i] < vol30max[i]):
                continue
            
            minData.MonCode(code)
            buyItems["code"].append(code)
            buyItems["close"].append(lastclose[i])
            buyItems["support"].append(minData.data['LA'])  # 전일 15분봉 기준 지지선
            buyItems["status"] = '1'

        print(buyItems)
        slogname(buyItems["code"])


        # buyItems = {'code': ['A005010', 'A042700', 'A051980'], 'open': [], 'close': [9860, 24250, 1850], 'support': [8335.0, 21812.5, 1467.5], 'status': '1'}
        # slogname(buyItems["code"])
        
        
        # # AM 09:01 ~ 09:05 : 시가 기준 3차 매수 종목 추출
        # bcodes = buyItems["code"]
        # for i, code in enumerate(bcodes):
        #     open, offer, bid = objStockMst.getPrice(code)
        #     buyFlag = check_openprice(open, buyItems["close"][i])

        #     # print(code, open, buyItems["close"][i], buyFlag)
        #     if not buyFlag:
        #         buyItems["code"][i] = None
        #         buyItems["close"][i] = 0
        #         buyItems["support"][i] = 0
        #         buyItems["open"].append(0)
        #     else:
        #         buyItems["open"].append(open)

        #     buyItems["status"] = '2'

        # slogname(buyItems["code"])

        # AM 09:25 ~ 09:31 : 15분봉 기준 Analyser Start (open > 15close, 15close > 30close)
        # for i, code in enumerate(buyItems["code"]):
        #     if code == None:
        #         continue
            
        #     time.sleep(0.2)
        #     temp = minData.requestLastMinData(code)
        #     if temp['T'][0] != 930:
        #         continue

        #     # open < 15close or 15close < 30close 일 경우 제외 
        #     if buyItems["open"][i] < temp['C'][1] or temp['C'][1] < temp['C'][0]:
        #         buyItems["code"][i] = None
        #         buyItems["close"][i] = 0
        #         buyItems["support"][i] = 0
        #         buyItems["open"][i] = 0

        #     buyItems["status"] = '3'
     
        # slogname(buyItems["code"])

        # AM 09:32 ~ 10:30 : 현재가 기준 Trader Start (current > bsupports)


        # for i, code in enumerate(buyItems["code"]):
        #     if code == None:
        #         continue

        #     open, offer, bid = objStockMst.getPrice(code)
        #     if check_supportprice(offer, buyItems["support"][i]):
        #         print('매수!!!')
        #         # print('예약매도 +3.5%')
        #         # print('예약매도 -3%')
        #         break       # 한 종목만 전액 매수 기법...(분할은 추후)

        #################################################################################

        #################################################################################
        ### REAL CODE
        #################################################################################
        # while True:
        #     # t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        #     # t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
        #     t_now = datetime.now()
        #     today = datetime.today().weekday()
        #     t_830 = t_now.replace(hour=8, minute=30, second=0, microsecond=0)
        #     t_900 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        #     t_905 = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        #     t_925 = t_now.replace(hour=9, minute=25, second=0, microsecond=0)
        #     t_932 = t_now.replace(hour=9, minute=32, second=0, microsecond=0)
        #     t_1030 = t_now.replace(hour=10, minute=30, second=0, microsecond=0)
        #     t_exit = t_now.replace(hour=11, minute=00, second=0,microsecond=0)


        #     time.sleep(1)

        #     if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
        #         print('Today is', 'Saturday.' if today == 5 else 'Sunday.')
        #         sys.exit(0)

        #     # AM 08:30 ~ 09:00 : Day Collector 1차 매수 종목 추출 (collector start)
        #     # AM 08:30 ~ 09:00 : Min Collector 2차 매수 종목 추출 (buyItems 생성)
        #     if t_830 < t_now < t_900:
        #         if (buyItems["status"] == '1'):
        #             continue
        #         objMarketTotal.get_target_items()
        #         codes = objMarketTotal.targetItems["code"]
        #         vol = objMarketTotal.targetItems["vol"]
        #         lastclose = objMarketTotal.targetItems["lastclose"]
        #         vol30max = objMarketTotal.targetItems["lastmaxvol"]
        #         for i, code in enumerate(codes):
        #             if (vol[i] < vol30max[i]):
        #                 continue
                    
        #             minData.MonCode(code)
        #             buyItems["code"].append(code)
        #             buyItems["close"].append(lastclose[i])
        #             buyItems["support"].append(minData.data['LA'])  # 전일 15분봉 기준 지지선
        #             buyItems["status"] = '1'

        #         slogname(buyItems["code"])
        #         time.sleep(2)

        #     # AM 09:01 ~ 09:05 : 시가 기준 3차 매수 종목 추출
        #     if t_900 < t_now < t_905 :
        #         if (buyItems["status"] == '2'):
        #             continue
        #         bcodes = buyItems["code"]
        #         for i, code in enumerate(bcodes):
        #             open, offer, bid = objStockMst.getPrice(code)
        #             buyFlag = check_openprice(open, buyItems["close"][i])

        #             # print(code, open, buyItems["close"][i], buyFlag)
        #             if not buyFlag:
        #                 buyItems["code"][i] = None
        #                 buyItems["close"][i] = 0
        #                 buyItems["support"][i] = 0
        #                 buyItems["open"].append(0)
        #             else:
        #                 buyItems["open"].append(open)

        #             buyItems["status"] = '2'

        #         slogname(buyItems["code"])
        #         time.sleep(2)

        #     # AM 09:25 ~ 09:31 : 15분봉 기준 Analyser Start (open > 15close, 15close > 30close)
        #     if t_925 < t_now < t_932 :
        #         if (buyItems["status"] == '3'):
        #             continue
        #         for i, code in enumerate(buyItems["code"]):
        #             if code == None:
        #                 continue
                    
        #             time.sleep(0.3)
        #             temp = minData.requestLastMinData(code)
        #             if temp['T'][0] != 930:
        #                 continue

        #             # open < 15close or 15close < 30close 일 경우 제외 
        #             if buyItems["open"][i] < temp['C'][1] or temp['C'][1] < temp['C'][0]:
        #                 buyItems["code"][i] = None
        #                 buyItems["close"][i] = 0
        #                 buyItems["support"][i] = 0
        #                 buyItems["open"][i] = 0

        #             buyItems["status"] = '3'
            
        #         slogname(buyItems["code"])
        #         time.sleep(2)

        #     # AM 09:32 ~ 10:30 : 현재가 기준 Trader Start (current > bsupports)
        #     # TODO : Realtime 기반으로 변경 필요.
        #     if t_932 < t_now < t_1030:
        #         if (buyItems["status"] == '00'):
        #             slog('[00] Trader exit...')    
        #             sys.exit(0)

        #         for i, code in enumerate(buyItems["code"]):
        #             if code == None:
        #                 continue

        #             time.sleep(0.3)     ## 실시간 API 제한 확인 (15초당 최대 60건, 실시간일 경우 최대 400건)
        #             open, offer, bid = objStockMst.getPrice(code)
        #             if check_supportprice(offer, buyItems["support"][i]):
        #                 slog("{} ({}) Buy !!".format(cpCodeMgr.CodeToName(code), offer))
        #                 buyItems["status"] = '00'
        #                 # print('예약매도 +3.5%')
        #                 # print('예약매도 -3%')
        #                 break       # 한 종목만 전액 매수 기법...(분할은 추후)

        #         # slogname(buyItems["code"])

        #     if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
        #         print('Trader exit...')
        #         sys.exit(0)

    except Exception as ex:
        slog('`main -> exception! ' + str(ex) + '`')    