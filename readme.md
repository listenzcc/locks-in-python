# 用不好互斥锁就不要用

写出安全、高效的异步程序是程序员的基本功。但今天看到一段别人用chatgpt写的程序，其中rlock的使用我横竖看不顺眼。于是我用reentrant lock（rlock）做了一个实验，结果表明，像chatgpt那样简单粗暴的使用rlock，会大大降低异步效率。

究其原因是由于rlock的获取和释放过程是“完全竞争的”，因此容易出现生产者过度生产，而消费者没有机会消费的情况。

- [用不好互斥锁就不要用](#用不好互斥锁就不要用)
  - [Python中的reentrant lock（rlock）](#python中的reentrant-lockrlock)
  - [有无contextlib管理的rlock锁并行效率比较](#有无contextlib管理的rlock锁并行效率比较)
  - [附录：生产和消费的程序样例](#附录生产和消费的程序样例)

---

## Python中的reentrant lock（rlock）

> A reentrant lock is a synchronization primitive that may be acquired multiple times by the same thread. Internally, it uses the concepts of “owning thread” and “recursion level” in addition to the locked/unlocked state used by primitive locks. In the locked state, some thread owns the lock; in the unlocked state, no thread owns it.
>
>
> [threading — Thread-based parallelism](https://docs.python.org/3/library/threading.html)
>

这是reentrant lock（可重入锁）的概念。可重入锁是一种同步原语，允许同一线程多次获取该锁。在内部实现上，可重入锁除了使用基本锁的锁定/解锁状态之外，还使用了“拥有线程”和“递归级别”的概念。当锁定状态时，某个线程拥有该锁；在解锁状态时，没有线程拥有它。

这意味着同一线程可以在已经获取锁的情况下再次获取锁，而不会引发死锁或其他问题。这种特性使得可重入锁在某些场景下非常有用，例如递归函数中需要对共享资源进行加锁的情况。

我尝试在 Python 中使用 reentrant lock，以确保线程安全和避免竞态条件等问题。同时尝试使用上下文管理器来更优雅地管理 reentrant lock，从而提高代码的可读性和简洁性。contextlib 模块提供了一个名为 `@contextmanager` 的装饰器，可以用来定义上下文管理器，使得资源的获取和释放更加简洁明了。通过使用 contextlib 提供的上下文管理器，还可以更方便地管理 reentrant lock，确保在多线程环境中正确地获取和释放锁，避免出现死锁等问题。

令人意外的是，我竟然发现了简单粗暴地使用rlock可能导致严重的异步执行效率问题。本文的代码和结果详见我的代码仓库

[https://github.com/listenzcc/locks-in-python](https://github.com/listenzcc/locks-in-python)

## 有无contextlib管理的rlock锁并行效率比较

实验过程见附录。简而言之，我使用异步的生产者（produce）、消费者（consume）模式构造了异步的并行环境，在该环境中统计了不同rlock使用方式下，模拟任务的等待时间。实验结果表明。

- 不使用contextlib管理rlock时（方法1），模拟任务的平均等待时间（passed字段）为1.46秒，
- 使用contextlib管理rlock时（方法2），模拟任务的平均等待时间（passed字段）为0.12秒。

究其原因，是由于方法1中rlock获取和释放的节奏较为同步，消费者开始执行时，队列长度较短；而在方法2中，由于rlock的获取和释放过程是“完全竞争的”，因此容易出现生产者过度生产，而消费者没有机会消费的情况。

反映在数据中，就出现了消费端进行工作时，它所面对的数据队列特别长，达到了平均51.87个任务。而在contextlib管理rlock时，消费队列的平均长度是3.49。显然，后者更容易发挥异步多线程的优势，生产和消费也显得更加协调。

![Untitled](%E7%94%A8%E4%B8%8D%E5%A5%BD%E4%BA%92%E6%96%A5%E9%94%81%E5%B0%B1%E4%B8%8D%E8%A6%81%E7%94%A8%20c4c7b52ccbdd4d63bf5e1f0e0c408427/Untitled.png)

![Untitled](%E7%94%A8%E4%B8%8D%E5%A5%BD%E4%BA%92%E6%96%A5%E9%94%81%E5%B0%B1%E4%B8%8D%E8%A6%81%E7%94%A8%20c4c7b52ccbdd4d63bf5e1f0e0c408427/Untitled%201.png)

![Untitled](%E7%94%A8%E4%B8%8D%E5%A5%BD%E4%BA%92%E6%96%A5%E9%94%81%E5%B0%B1%E4%B8%8D%E8%A6%81%E7%94%A8%20c4c7b52ccbdd4d63bf5e1f0e0c408427/Untitled%203.png)

## 附录：生产和消费的程序样例

最后附上本文中使用的生产、消费程序样例

```python
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
```
