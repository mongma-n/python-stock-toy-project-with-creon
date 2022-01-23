import threading
import time
import random
 
def DoItThread(str):
    cnt = 0
    while(cnt<10):
        time.sleep(random.randint(0,100)/300.0)
        print(str,cnt)
        cnt+=1
    print("=== ",str,"스레드 종료 ===")
 
th_a = threading.Thread(target = DoItThread, args=("홍길동",))
th_b = threading.Thread(target = DoItThread, args=("강감찬",))
 
print("=== 스레드 가동 ===")
th_a.start()
th_b.start()
 
th_a.join()
th_b.join()
print("테스트 종료")