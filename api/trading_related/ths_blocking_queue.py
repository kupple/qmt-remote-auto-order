from typing import Any, Callable, Optional
import threading

class NonBlockingQueue:
    def __init__(self):
        """初始化非阻塞队列"""
        self.items = []
        self.lock = threading.Lock()
        self.not_empty = threading.Event()
        self._running = True

    def enqueue(self, item: Any) -> None:
        """将元素添加到队尾并唤醒等待的线程"""
        with self.lock:
            self.items.append(item)
            self.not_empty.set()  # 唤醒可能正在等待的线程

    def dequeue(self, timeout: Optional[float] = None) -> Any:
        """从队首移除元素并返回，支持超时机制"""
        # 等待直到队列非空或超时
        if not self.not_empty.wait(timeout):
            raise TimeoutError("dequeue operation timed out")
        
        with self.lock:
            if not self.items:  # 再次检查队列是否为空（可能被其他线程抢先）
                self.not_empty.clear()
                raise IndexError("dequeue from empty queue")
            
            item = self.items.pop(0)
            if not self.items:  # 如果队列为空，清除事件
                self.not_empty.clear()
            return item

    def front(self) -> Any:
        """查看队首元素"""
        with self.lock:
            if not self.items:
                raise IndexError("front from empty queue")
            return self.items[0]

    def is_empty(self) -> bool:
        """判断队列是否为空"""
        with self.lock:
            return len(self.items) == 0

    def size(self) -> int:
        """返回队列的大小"""
        with self.lock:
            return len(self.items)

    def start_consumer(self, callback: Callable[[Any], None]) -> threading.Thread:
        """启动一个消费者线程，持续处理队列中的元素"""
        def consumer_loop():
            while self._running:
                try:
                    item = self.dequeue(timeout=1.0)  # 每1秒检查一次
                    callback(item)
                except TimeoutError:
                    continue  # 继续循环，不做任何处理
                except Exception as e:
                    print(f"Error processing item: {e}")
        
        thread = threading.Thread(target=consumer_loop, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        """停止消费者线程"""
        self._running = False

    def __str__(self) -> str:
        """返回队列的字符串表示"""
        with self.lock:
            return str(self.items)