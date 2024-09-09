import pytest

from endstone_bstats import Metrics
from endstone_bstats._executor import ScheduledThreadPoolExecutor


@pytest.fixture
def plugin(tmp_path, mocker):
    p = mocker.MagicMock()
    p.data_folder = str(tmp_path)
    p.server.scheduler.run_task = mocker.MagicMock()
    p.enabled = True
    p.logger.warning = mocker.MagicMock()
    p.logger.info = mocker.MagicMock()
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


def test_enabled(metrics):
    assert metrics.enabled


def test_service_enabled(metrics, plugin):
    assert metrics.service_enabled == plugin.enabled


@pytest.mark.parametrize(
    "os_name, release, version, os_name_expected, os_version_expected",
    [
        (
            "Windows",
            "10",
            "10.0.19041",
            "Windows 10",
            "10.0.19041",
        ),
        (
            "Linux",
            "5.4.0-42-generic",
            "#46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020",
            "Linux",
            "5.4.0-42-generic",
        ),
    ],
)
def test_append_platform_data(
    metrics, mocker, os_name, release, version, os_name_expected, os_version_expected
):
    platform_data = {}

    mocker.patch("os.cpu_count", return_value=4)
    mocker.patch("platform.system", return_value=os_name)
    mocker.patch("platform.release", return_value=release)
    mocker.patch("platform.version", return_value=version)
    mocker.patch("platform.machine", return_value="AMD64")

    metrics.append_platform_data(platform_data)

    assert platform_data["playerAmount"] == 3
    assert platform_data["osName"] == os_name_expected
    assert platform_data["osVersion"] == os_version_expected
    assert platform_data["osArch"] == "amd64"
    assert platform_data["coreCount"] == 4


def test_append_service_data(metrics, plugin):
    service_data = {}
    metrics.append_service_data(service_data)
    assert service_data["pluginVersion"] == plugin.description.version


def test_submit_task(mocker, metrics, plugin):
    task = mocker.MagicMock()
    metrics.submit_task(task)
    plugin.server.scheduler.run_task.assert_called_once_with(plugin, task)


def test_log_info(metrics, plugin):
    message = "Test info message"
    metrics.log_info(message)
    plugin.logger.info.assert_called_once_with(message)


def test_log_error(metrics, plugin):
    message = "Test error message"
    exception = Exception("Test exception")
    metrics.log_error(message, exception)
    plugin.logger.warning.assert_called_once_with(f"{message}: {exception}")


def test_get_python_version(mocker, metrics):
    mocker.patch("platform.python_implementation", return_value="CPython")
    mocker.patch("platform.python_version_tuple", return_value=(3, 12, 4))
    version_data = metrics._get_python_version()
    assert version_data == {"CPython 3.12": {"CPython 3.12.4": 1}}
