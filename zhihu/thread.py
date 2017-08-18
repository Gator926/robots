import threading
import time


def push():
    for i in range(1, 200000):
        print("push")
        # time.sleep(0.5)


def pop():
    for i in range(1, 100000):
        print("pop")
        # time.sleep(2)

if __name__ == '__main__':
    threads = []
    t1 = threading.Thread(target=push)
    t2 = threading.Thread(target=pop)

    threads.append(t1)
    threads.append(t2)

    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()

    t1.join()
    t2.join()