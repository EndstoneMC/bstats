import os
import platform
from functools import partial
from pathlib import Path
from typing import Any, Dict

from endstone.plugin import Plugin

from endstone_bstats._base import MetricsBase
from endstone_bstats._charts.custom_chart import CustomChart
from endstone_bstats._config import MetricsConfig


class Metrics:
    def __init__(self, plugin: Plugin, service_id: int):
        """
        Creates a new Metrics instance.

        Args:
            plugin (Plugin): Your plugin instance.
            service_id (int): The id of the service.
                              It can be found at https://bstats.org/what-is-my-plugin-id
        """
        self._plugin = plugin

        # Get the config file
        bstats_folder = Path(plugin.data_folder).parent / "bStats"
        config_file = bstats_folder / "config.toml"
        config = MetricsConfig(config_file, True)

        self._metrics_base = MetricsBase(
            platform="server-implementation",
            server_uuid=config.server_uuid,
            service_id=service_id,
            enabled=config.enabled,
            platform_data_appender=self.append_platform_data,
            service_data_appender=self.append_service_data,
            task_submitter=lambda task: partial(
                plugin.server.scheduler.run_task, plugin, task
            ),
            check_service_enabled=lambda: plugin.enabled,
            error_logger=lambda msg, e: plugin.logger.warning(f"{msg}: {e}"),
            info_logger=plugin.logger.info,
            log_errors=config.log_errors_enabled,
            log_sent_data=config.log_sent_data_enabled,
            log_response_status_text=config.log_response_status_text_enabled,
        )

    def shutdown(self):
        """Shuts down the underlying scheduler service."""
        self._metrics_base.shutdown()

    def add_custom_chart(self, chart: CustomChart):
        """
        Adds a custom chart.

        Args:
            chart (CustomChart): The chart to add.
        """
        self._metrics_base.add_custom_chart(chart)

    def append_platform_data(self, platform_data: Dict[str, Any]) -> None:
        """
        Appends platform-specific data to the provided dict.

        Args:
            platform_data (Dict[str, Any]): The dict to append data to.
        """
        # TODO: implement the following
        platform_data["playerAmount"] = len(self._plugin.server.online_players)
        # platform_data["onlineMode"] = 1 if Bukkit.get_online_mode() else 0

        platform_data["osName"] = platform.system()
        platform_data["osArch"] = platform.machine().lower()
        platform_data["osVersion"] = platform.release()
        platform_data["coreCount"] = os.cpu_count()

    def append_service_data(self, service_data: Dict[str, Any]):
        """
        Appends service-specific data to the provided dict.

        Args:
            service_data (Dict[str, Any]): The dict to append data to.
        """
        service_data["pluginVersion"] = self._plugin.description.version
