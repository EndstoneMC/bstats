import os
import platform
from unittest.mock import MagicMock

import pytest

from endstone_bstats import Metrics
from endstone_bstats._executor import ScheduledThreadPoolExecutor


@pytest.fixture
def plugin(tmp_path):
    p = MagicMock()
    p.data_folder = str(tmp_path)
    p.server.scheduler.run_task = MagicMock()
    p.enabled = True
    p.logger.warning = MagicMock()
    p.logger.info = MagicMock()
    p.server.online_players = ["Player1", "Player2", "Player3"]
    p.description.version = "1.0.0"
    return p


@pytest.fixture
def metrics(mocker, plugin):
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit")
    mocker.patch.object(ScheduledThreadPoolExecutor, "submit_at_fixed_rate")
    m = Metrics(plugin, service_id=1234)
    yield m
    m.shutdown()


def test_init(metrics, plugin):
    assert metrics._plugin == plugin
    assert metrics._metrics_base is not None


def test_add_custom_chart(mocker, metrics):
    chart = mocker.MagicMock()
    metrics.add_custom_chart(chart)
    assert chart in metrics._metrics_base._custom_charts


def test_append_platform_data(metrics):
    platform_data = {}
    metrics.append_platform_data(platform_data)

    assert platform_data["playerAmount"] == 3
    assert platform_data["osName"] == platform.system()
    assert platform_data["osArch"] == platform.machine().lower()
    assert platform_data["osVersion"] == platform.release()
    assert platform_data["coreCount"] == os.cpu_count()


def test_append_service_data(metrics):
    service_data = {}
    metrics.append_service_data(service_data)
    assert service_data["pluginVersion"] == "1.0.0"
