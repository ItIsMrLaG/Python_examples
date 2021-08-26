from multiprocessing import Queue, Process, Pipe
import time
import os

"""
the logic of work - two processes are created (the main process and the information provider) so that there is no 
"struggle for resources" between them I created a third auxiliary process, 
which acts as a buffer (all interaction is carried out through it, 
so it must be fast, and it must have means of protection against possible errors due to asynchronous)
"""

class Informator:
    """
    class for creating another process for reading information from it
    *should be used with Intermediary
    """

    def __init__(self, func):
        """
        @param func: <type>: function - informator-function
        """
        self.func = func
        self.q = Queue(maxsize=2)
        self.proc = Process(target=self.func, args=(self.wrapper,))
        self.proc.start()

    def wrapper(self, information):
        """
        @param information: <type>: anything - information for sending in the main process
        """
        if self.q.empty() is True:
            self.q.put(information)

    def reader(self):
        if self.q.empty() is True:
            return self.q.get()


class Messenger:
    def __init__(self, func):
        """
        @param func: <type>: function - sent-function

        ############### EXAMPLE ###################
        def sender(func):
            while True:
                info = func()
                print(info)

        send = Messenger(sender)
        while True:
            info_give = "hello mr.lag"
            send.send(info_give)

        """
        self.func = func
        self.q = Queue(maxsize=2)
        self.proc = Process(target=self.func, args=(self.wrapper,))
        self.proc.start()

    def wrapper(self):
        if self.q.empty() is not True:
            return self.q.get()

    def send(self, information):
        if self.q.empty() is True:
            self.q.put(information)


class Intermediary:
    """
    creating of the 'second-helper' process for connecting 'third-context' process with 'first-main'

    ############### EXAMPLE ####################
    -------------> INFORM FUNC <-------------------
    def Func1(func):                            # 'in this argument would be given Informator.wrarpper'
        print(os.getpid(), ' - Function')
        l = 0
        while True:
            print(l, ' - func')
            time.sleep(0.1)
            l += 1
            func(l)                              #  'required template for the send function'

    -------------> MAIN PROCESS <-----------------------
    test = Intermediary(Func1, 1)                #  'initialization'
    print(os.getpid(), ' - Main')
    while True:                                  #  'main loop'
        time.sleep(2)
        print(test.reader(), ' - final info')    #  'reading info from informator-function  '
    """

    def __init__(self, func, delay):
        """
        @param func: <type>: function - informator-function
        @param delay: <type>: int - delay before processes initialization
        """
        self.all_funcs = func
        self.keys = []
        self.info_q = Queue(maxsize=2)         # queue for signal 'give'
        self.main_q = Queue(maxsize=2)         # queue for received info
        self.proc = Process(target=self.creator, args=(func,))
        self.proc.start()
        time.sleep(delay)

    def creator(self, func):
        print(os.getpid(), ' - Intermediary')

        info = None
        module = Informator(func)

        while True:

            if self.info_q.empty() is not True:  # sender in the main process
                out = self.info_q.get()
                if self.main_q.empty():
                    self.main_q.put(info)

            if module.q.empty() is not True:     # reader from Inforamator
                info = module.q.get()

    def reader(self):
        if self.info_q.empty() is True:
            self.info_q.put('give')
            time.sleep(0.1)
        if self.main_q.empty() is not True:
            return self.main_q.get()
        else:
            return 'ERROR'
