import ctypes
import win32com.client
from slacker import Slacker
from datetime import datetime

slack = Slacker('my slack id')
cpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
cpCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')

def slog(message):
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    slack.chat.post_message('#stock', strbuf)
    print(strbuf)

def slogname(arr):
    print(arr)    
    messageArr = []
    for code in arr:
        messageArr.append(cpCodeMgr.CodeToName(code))
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + ' '.join(messageArr)
    slack.chat.post_message('#stock', strbuf)

def check_creon_system():
    # 관리자 권한으로 프로세스 실행 여부
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print('check_creon_system() : admin user -> FAILED')
        return False

    # 연결 여부 체크
    if (cpStatus.IsConnect == 0):
        print('check_creon_system() : connect to server -> FAILED')
        return False

    return True


def check_openprice(open, close):
    if close == 0 or open == 0:
        return False
    
    per = ((open - close) / close) * 100.0    
    if abs(per) < 10.0:  # 전일 종가의 -7% ~ 7% 범위안의 시가 여부 체크
        return True

    return False


def check_supportprice(curr, support):
    if curr == 0 or support == 0:
        return False
    
    per = ((support - curr) / curr) * 100.0    
    if abs(per) < 3.0:  # 지지선의 -2% ~ 2% 범위안의 현재가 여부 체크
        return True

    return False