import os
import platform
import sys
from pathlib import Path
from typing import Any, Callable, Dict

from endstone.plugin import Plugin

from endstone_bstats._base import MetricsBase
from endstone_bstats._config import MetricsConfig


class Metrics(MetricsBase):
    def __init__(self, plugin: Plugin, service_id: int) -> None:
        """
        Creates a new Metrics instance.

        Args:
            plugin (Plugin): Your plugin instance.
            service_id (int): The id of the service.
                              It can be found at https://bstats.org/what-is-my-plugin-id
        """

        self._plugin = plugin

        # Get the config file
        bstats_folder = Path(plugin.data_folder).parent / "bstats"
        config_file = bstats_folder / "config.toml"
        self._config = MetricsConfig(config_file, True)

        super().__init__(
            platform="bukkit",
            server_uuid=self._config.server_uuid,
            service_id=service_id,
            log_errors=self._config.log_errors_enabled,
            log_sent_data=self._config.log_sent_data_enabled,
            log_response_status_text=self._config.log_response_status_text_enabled,
        )

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    @property
    def service_enabled(self) -> bool:
        return self._plugin.enabled

    def append_platform_data(self, platform_data: Dict[str, Any]) -> None:
        """
        Appends platform-specific data to the provided dict.

        Args:
            platform_data (Dict[str, Any]): The dict to append data to.
        """
        # TODO: implement the following
        platform_data["playerAmount"] = len(self._plugin.server.online_players)
        # platform_data["onlineMode"] = 1 if Bukkit.get_online_mode() else 0
        platform_data["endstoneVersion"] = self._plugin.server.version
        platform_data["minecraftVersion"] = self._plugin.server.minecraft_version
        platform_data["pythonVersion"] = (
            f"{sys.version_info.major}.{sys.version_info.minor}"
        )
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

    def submit_task(self, task: Callable[[], None]) -> None:
        self._plugin.server.scheduler.run_task(self._plugin, task)

    def log_info(self, message: str) -> None:
        self._plugin.logger.info(message)

    def log_error(self, message: str, exception: Exception) -> None:
        self._plugin.logger.warning(f"{message}: {exception}")
