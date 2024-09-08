import uuid
from typing import Callable
from unittest.mock import MagicMock

import pytest
import requests_mock

from endstone_bstats import MetricsBase
from endstone_bstats._executor import ScheduledThreadPoolExecutor


@pytest.fixture
def metrics(mocker):
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit")
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit_at_fixed_rate")
    m = MetricsBase(
        platform="test_platform",
        server_uuid=uuid.uuid4(),
        service_id=1,
        enabled=True,
        platform_data_appender=mocker.MagicMock(),
        service_data_appender=mocker.MagicMock(),
        task_submitter=None,
        check_service_enabled=mocker.MagicMock(return_value=True),
        error_logger=mocker.MagicMock(),
        info_logger=mocker.MagicMock(),
        log_errors=True,
        log_sent_data=True,
        log_response_status_text=True,
    )
    yield m
    m.shutdown()


def test_add_custom_chart(mocker, metrics):
    chart = mocker.MagicMock()
    metrics.add_custom_chart(chart)
    assert chart in metrics._custom_charts


def test_shutdown(mocker, metrics):
    mocker.patch.object(
        ScheduledThreadPoolExecutor, "shutdown", wraps=metrics._executor.shutdown
    )
    metrics.shutdown()
    metrics._executor.shutdown.assert_called_once()


def test_submit_data(mocker, metrics):
    mocker.patch.object(MetricsBase, "_send_data")
    chart = mocker.MagicMock()
    metrics.add_custom_chart(chart)
    metrics._submit_data()
    data = metrics._send_data.call_args.args[0]
    assert data["service"]["id"] == 1


def test_submit_data_with_exception(mocker, metrics):
    mocker.patch.object(
        MetricsBase, "_send_data", side_effect=Exception("Test exception")
    )
    chart = mocker.MagicMock()
    metrics.add_custom_chart(chart)
    metrics._submit_data()
    metrics._error_logger.assert_called_once()


def test_send_data(mocker, metrics):
    with requests_mock.Mocker() as rm:
        rm.post("https://bStats.org/api/v2/data/test_platform", status_code=201)
        metrics._submit_data()
        assert rm.last_request.body is not None
        assert metrics._info_logger.call_count == 2


def warp_submit(task: Callable, *args, **kwargs):
    task()


def test_start_submitting(mocker, metrics):
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit", wraps=warp_submit)
    metrics._start_submitting()


def test_start_submitting_with_task_submitter(mocker, metrics):
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit", wraps=warp_submit)
    metrics._task_submitter = MagicMock()
    metrics._start_submitting()
    metrics._task_submitter.assert_called_once()


def test_start_submitting_when_disabled(mocker, metrics):
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit", wraps=warp_submit)
    metrics._enabled = False
    mocker.patch.object(MetricsBase, "shutdown", wraps=metrics.shutdown)
    metrics._start_submitting()
    metrics.shutdown.assert_called_once()
