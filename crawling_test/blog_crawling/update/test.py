import time
import os
from multiprocessing import Pool


# def work_func(x):
#     print("value %s is in PID : %s" % (x, os.getpid()))
#     time.sleep(1)
#     return x**5


# def main():
#     start = int(time.time())
#     num_cores = os.cpu_count()  # 각자 컴퓨터에 있는 코어의 갯수를 불러온다.

#     pool = Pool(num_cores)
#     print(pool.map(work_func, range(1, 13)))
#     print("***run time(sec) :", int(time.time()) - start)

#     pool.colse()  # 더이상 추가 작업이 들어가지 않는다.
#     pool.join()  # 모든 프로세스가 종료되기를 기다리는것


# if __name__ == "__main__":
#     main()
from multiprocessing import Pool


def worker(x):
    return x * x


if __name__ == '__main__':
    num_processors = 10
    p = Pool(processes=num_processors)
    output = p.map(worker, [i for i in range(0, 10)])
    print(output)
