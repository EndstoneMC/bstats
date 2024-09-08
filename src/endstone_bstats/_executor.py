import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import schedule


class ScheduledThreadPoolExecutor:
    def __init__(self, max_workers: int):
        self.scheduler = schedule.Scheduler()
        self.shutdown_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.executor.submit(self.run)

    def run(self) -> None:
        while not self.shutdown_event.is_set():
            self.scheduler.run_pending()
            time.sleep(0.1)

    def shutdown(self) -> None:
        self.shutdown_event.set()
        self.executor.shutdown(wait=True, cancel_futures=True)
        self.scheduler.clear()

    def submit(self, task: Callable, delay_secs: int, *args, **kwargs) -> None:
        self.submit_at_fixed_rate(task, delay_secs, 0, *args, **kwargs)

    def submit_at_fixed_rate(
        self, task: Callable, initial_delay_secs: int, period_secs: int, *args, **kwargs
    ) -> None:
        def initial_run():
            task(*args, **kwargs)
            if period_secs > 0:
                self.scheduler.every(period_secs).seconds.do(task, *args, **kwargs)
            return schedule.CancelJob

        if initial_delay_secs > 0:
            self.scheduler.every(initial_delay_secs).seconds.do(initial_run)
        else:
            initial_run()
