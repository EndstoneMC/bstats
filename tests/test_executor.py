import pytest
import threading
import time
from datetime import datetime
from endstone_bstats._executor import ScheduledThreadPoolExecutor


@pytest.fixture
def executor():
    exec = ScheduledThreadPoolExecutor(max_workers=2)
    yield exec
    exec.shutdown()


def test_initial_submission(executor):
    executed = threading.Event()

    def task():
        executed.set()

    executor.submit(task, delay_secs=1)
    time.sleep(2)
    assert executed.is_set()


def test_fixed_rate_submission(executor):
    execution_times = []

    def task():
        execution_times.append(datetime.now())

    executor.submit_at_fixed_rate(task, initial_delay_secs=1, period_secs=2)

    time.sleep(7)  # Let the task run a few times.
    assert len(execution_times) >= 3


def test_shutdown(executor):
    executed = threading.Event()

    def task():
        executed.set()

    executor.submit(task, delay_secs=1)
    executor.shutdown()
    assert executor.shutdown_event.is_set()


def test_submit_args(executor):
    result = []

    def append_with_args(value):
        result.append(value)

    executor.submit(append_with_args, delay_secs=1, value=42)
    time.sleep(2)
    assert result == [42]


def test_repeated_task_execution(executor):
    lock = threading.Lock()
    count = 0

    def increment():
        nonlocal count
        with lock:
            count += 1

    executor.submit_at_fixed_rate(increment, initial_delay_secs=0, period_secs=1)
    time.sleep(5)

    # At least 4 successful increments are expected because of 4 seconds delay after initial execution.
    with lock:
        assert count >= 4
