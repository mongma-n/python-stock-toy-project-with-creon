import sys
from trade.collector import *
from trade.analyser import *
from com.getprice import *
from datetime import datetime
from com.utils import *
import time

import threading
from testprice import *



def worker(msg):
    print("{} is start : {}".format(threading.currentThread().getName(), msg))
    objStockCur1 = CpStockCur()
    objStockCur2 = CpStockCur()
    objStockCur3 = CpStockCur()
    
    objStockCur1.Subscribe("A003540") # 대신증권
    objStockCur2.Subscribe("A000660") # 하이닉스
    objStockCur3.Subscribe("A005930") # 삼성전자

    print("-------------------")
    print("실시간 현재가 요청 시작")
    print("{} is end".format(threading.currentThread().getName()))


def main():
    msg = "hello"
    th = threading.Thread(target=worker, name="[Daemon]", args=(msg,))
    th.setDaemon(True)
    th.start()
    th.join()

    print("Main Thread End")


if __name__ == "__main__":
    # plus 상태 체크
    if check_creon_system == False:
        exit()

    main()


