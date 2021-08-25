from multiprocessing import Queue, Process, Pipe
import time as tm
import os

"""
the logic of work - two processes are created (the main process and the information provider) so that there is no 
"struggle for resources" between them I created a third auxiliary process, 
which acts as a buffer (all interaction is carried out through it, 
so it must be fast, and it must have means of protection against possible errors due to asynchronous)
"""

class NewProcess:
    """
    creating of the 'second-helper' process for connecting 'third-context' process with 'first-main'
    """
    # todo the same - delay for basic information to appear in the 'third-helper' process

    def __init__(self):
        self.qp = Queue(maxsize=2)
        self.q = Queue(maxsize=2)
        self.proc = Process(target=self.sender1)
        self.proc.start()
        tm.sleep(1)  # todo the same

    def sender1(self):
        info = None
        print('proc - second', os.getpid())

        class NewProcess1:
            def __init__(self):
                """
                creating 'third-context' process (getter information from module as GPS)
                """
                self.q1 = Queue(maxsize=2)
                self.proc = Process(target=self.sender)
                self.proc.start()
                tm.sleep(1)  # todo the same

            def sender(self):
                print('proc - third', os.getpid())
                l = 0
                while True:
                    print(l, ' - third layer')
                    tm.sleep(1)  # todo the same
                    l += 1
                    if self.q1.empty():
                        self.q1.put([l, 23, 54.886958688])

        proc_inner = NewProcess1()
        while True:
            if proc_inner.q1.empty() == False:
                info = proc_inner.q1.get()
                print(info[0], ' - second layer')

            if self.qp.empty() is not True:
                out = self.qp.get()
                if self.q.empty():
                    self.q.put(info)



proc = NewProcess()
print('proc - first-final', os.getpid())
"""
it is the first-main process (this process want get actual information from 'third-context' process)
"""
while True:
    tm.sleep(4)
    if proc.qp.empty():
        proc.qp.put('give')
        tm.sleep(0.1)  # delay for getting information from 'second-helper' process
    if proc.q.empty() is not True:
        print(proc.q.get(), ' - first-final layer <<<---<<<<--------<<<<-------<<<<---')