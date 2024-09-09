import logging
import uuid
from typing import Callable

import pytest
import requests_mock

from endstone_bstats import CustomChart, MetricsBase
from endstone_bstats._executor import ScheduledThreadPoolExecutor


class TestMetricsBase(MetricsBase):
    __test__ = False

    @property
    def enabled(self) -> bool:
        return True

    @property
    def service_enabled(self) -> bool:
        return True


class TestCustomChart(CustomChart):
    __test__ = False

    def get_chart_data(self):
        raise Exception("Test exception")


@pytest.fixture
def metrics(mocker):
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit")
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit_at_fixed_rate")

    m = TestMetricsBase(
        platform="test_platform",
        server_uuid=uuid.uuid4(),
        service_id=1,
        log_errors=True,
        log_sent_data=True,
        log_response_status_text=True,
    )
    yield m
    m.shutdown()


def test_add_custom_chart(metrics):
    chart = TestCustomChart("custom_chart")
    metrics.add_custom_chart(chart)
    assert chart in metrics._custom_charts


def test_shutdown(mocker, metrics):
    mocker.patch.object(
        ScheduledThreadPoolExecutor, "shutdown", wraps=metrics._executor.shutdown
    )
    metrics.shutdown()
    metrics._executor.shutdown.assert_called_once()


def test_send_data(mocker, metrics):
    mocker.patch("logging.info")
    with requests_mock.Mocker() as rm:
        rm.post("https://bStats.org/api/v2/data/test_platform", status_code=201)
        metrics._submit_data()
        assert rm.last_request.body is not None
        assert logging.info.call_count == 2


def test_submit_data(mocker, metrics):
    mocker.patch.object(MetricsBase, "_send_data")
    mocker.patch.object(
        CustomChart, "_get_request_json_object", side_effect=Exception("Test exception")
    )
    chart = mocker.MagicMock()
    metrics.add_custom_chart(chart)
    metrics._submit_data()
    data = metrics._send_data.call_args.args[0]
    assert data["service"]["id"] == 1


def test_submit_data_with_exception(mocker, metrics):
    mocker.patch.object(
        MetricsBase, "_send_data", side_effect=Exception("Test exception")
    )
    mocker.patch("logging.warning")
    chart = TestCustomChart("custom_chart")
    metrics.add_custom_chart(chart)
    metrics._submit_data()
    assert logging.warning.call_count == 2


def warp_submit(task: Callable, *args, **kwargs):
    task()


def test_start_submitting(mocker, metrics):
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit", wraps=warp_submit)
    mocker.patch.object(MetricsBase, "_submit_data")
    metrics._start_submitting()
    metrics._submit_data.assert_called_once()


def test_start_submitting_when_disabled(mocker, metrics):
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit", wraps=warp_submit)
    mocker.patch.object(
        TestMetricsBase, "enabled", new_callable=mocker.PropertyMock(return_value=False)
    )
    mocker.patch.object(MetricsBase, "_submit_data")
    mocker.patch.object(MetricsBase, "shutdown", wraps=metrics.shutdown)
    metrics._start_submitting()
    metrics.shutdown.assert_called_once()
    metrics._submit_data.assert_not_called()
