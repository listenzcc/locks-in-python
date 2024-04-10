"""
File: rotation-lock.py
Author: Chuncheng Zhang
Date: 2024-04-10
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Example of rotation lock in python

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-04-10 ------------------------
# Requirements and constants
import time
import random
import threading
import contextlib

import pandas as pd

from rich import print
from loguru import logger


# %% ---- 2024-04-10 ------------------------
# Function and class
class ProducingAndConsumer(object):
    rlock = threading.RLock()
    buffer = []
    running = True
    uid = 0
    results = []
    use_contextlib = True

    def __init__(self):
        pass

    @contextlib.contextmanager
    def acquire_lock(self):
        try:
            yield self.rlock.acquire()
        finally:
            self.rlock.release()

    @property
    def buffer_size(self):
        return len(self.buffer)

    def _produce_1(self):
        with self.acquire_lock():
            self.__produce()

    def _consume_1(self):
        with self.acquire_lock():
            self.__consume()

    def _produce_2(self):
        self.rlock.acquire()
        self.__produce()
        self.rlock.release()

    def _consume_2(self):
        self.rlock.acquire()
        self.__consume()
        self.rlock.release()

    def __produce(self):
        for _ in range(3):
            e = dict(uid=self.uid, tic=time.time())
            self.buffer.append(e)
            self.uid += 1
            time.sleep(random.random() * 0.1)
            print(f'Insert {e}')

    def __consume(self):
        if self.buffer_size > 0:
            print(f'Dealing buffer size: {self.buffer_size}')
        else:
            return

        buffer_size = self.buffer_size

        while self.buffer_size > 0:
            e = self.buffer.pop(0)
            e['passed'] = time.time() - e['tic']
            e['buffer_size'] = buffer_size
            e['use_contextlib'] = self.use_contextlib
            self.results.append(e)
            print(f'Consumed: {e}')

    def produce_loop(self):
        logger.debug('Produce loop starts')
        while self.running:
            if self.use_contextlib:
                self._produce_1()
            else:
                self._produce_2()
        logger.debug('Produce loop finished')

    def consume_loop(self):
        logger.debug('Consume loop starts')
        while self.running:
            if self.use_contextlib:
                self._consume_1()
            else:
                self._consume_2()
        logger.debug('Consume loop finished')

    def main_loop(self):
        self.running = True
        threading.Thread(target=self.produce_loop, daemon=True).start()
        threading.Thread(target=self.consume_loop, daemon=True).start()


# %% ---- 2024-04-10 ------------------------
# Play ground
if __name__ == '__main__':
    pac = ProducingAndConsumer()

    # --------------------
    # Experiment 1
    pac.use_contextlib = True
    pac.main_loop()
    time.sleep(10)
    pac.running = False
    time.sleep(1)

    # --------------------
    # Experiment 2
    pac.main_loop()
    pac.use_contextlib = False
    time.sleep(10)
    pac.running = False
    time.sleep(1)

    # --------------------
    # Results
    df = pd.DataFrame(pac.results)
    print(df)
    df.to_csv('rotation-lock.csv')

    print('Done.')


# %% ---- 2024-04-10 ------------------------
# Pending


# %% ---- 2024-04-10 ------------------------
# Pending
