from __future__ import annotations

import os
import platform
import sys
import uuid
import gzip
import io
import tomlkit
from endstone.plugin import Plugin
from pathlib import Path

from endstone_bstats import CustomChart


class Metrics:
    """
    Metrics class for collecting data for plugin authors.

    This class uses bStats to collect some data for plugin authors to help them
    understand the usage of their plugins.

    Check out `https://bStats.org/ <https://bStats.org/>`_ to learn more about bStats!

    Attributes:
        B_STATS_VERSION (int): The version of this bStats class
        URL (str): The URL for submitting data to bStats.
        _log_failed_requests (bool): Flag to log failed requests.
        _log_sent_data (bool): Flag to log sent data.
        _log_response_status_text (bool): Flag to log response status text.
        _server_uuid (UUID): The UUID of the server.
    """

    B_STATS_VERSION = 1
    URL = "https://bStats.org/submitData/server-implementation"

    _log_failed_requests: bool
    _log_sent_data: bool
    _log_response_status_text: bool
    _server_uuid: uuid.UUID

    def __init__(self, plugin: Plugin, plugin_id: int) -> None:
        """
        Initializes the Metrics class with the provided plugin and plugin ID.

        Args:
            plugin (Plugin): The plugin for which stats should be submitted.
            plugin_id (int): The ID of the plugin. It can be found at
                `What is my plugin id? <https://bstats.org/what-is-my-plugin-id>`_.
        """

        self._enabled = False
        self._plugin = plugin
        self._plugin_id = plugin_id
        self._charts: list[CustomChart] = []

        self._load_config()

    @property
    def enabled(self) -> bool:
        """
        Checks if bStats is enabled.

        Returns:
            bool: Whether bStats is enabled or not.
        """
        return self._enabled

    def add_chart(self, chart: CustomChart) -> None:
        """
        Adds a custom chart.

        Args:
            chart (CustomChart): The chart to add.
        """
        self._charts.append(chart)

    @property
    def _server_data(self) -> dict:
        """
        Gets the server-specific data.

        Returns:
            dict: The server-specific data.
        """

        server = self._plugin.server
        data = {
            "serverUUID": str(self._server_uuid),
            "playerAmount": len(server.online_players),
            # TODO: online mode
            "endstoneVersion": server.version,
            "endstoneName": server.name,
            "pythonVersion": f"{sys.version_info.major}.{sys.version_info.minor}",
            "osName": platform.system(),
            "osArch": platform.machine(),
            "osVersion": platform.release(),
            "coreCount": os.cpu_count(),
        }
        return data

    def _load_config(self) -> None:
        # Get the config file
        bstats_folder = Path(self._plugin.data_folder).parent / "bstats"
        config_file = bstats_folder / "config.toml"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = tomlkit.load(f)
        else:
            config = tomlkit.document()

        # Check if the config file exists
        if not "server-uuid" in config:
            config.setdefault("enabled", True)
            config.setdefault("server-uuid", str(uuid.uuid4()))
            config.setdefault("log-failed-requests", False)
            config.setdefault("log-sent-data", False)
            config.setdefault("log-response-status-text", False)

            new_config = tomlkit.document()
            new_config.add(
                tomlkit.comment(
                    "bStats collects some data for plugin authors like how many servers are using their plugins.\n"
                    "To honor their work, you should not disable it.\n"
                    "This has nearly no effect on the server performance!\n"
                    "Check out https://bStats.org/ to learn more :)"
                )
            )

            for key, value in config.items():
                new_config.add(key, value)

            config = new_config
            bstats_folder.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w", encoding="utf-8") as f:
                tomlkit.dump(config, f)

        # Load the data
        self._enabled = config.get("enabled", True)
        self._server_uuid = uuid.UUID(config.get("server-uuid"))
        self._log_failed_requests = config.get("log-failed-requests", False)
        self._log_sent_data = config.get("log-sent-data", False)
        self._log_response_status_text = config.get("log-response-status-text", False)

    @staticmethod
    def compress(data: str) -> bytes:
        """
        Compresses the given string using gzip.

        Args:
            data (str): The string to gzip.

        Returns:
            bytes: The gzipped string.

        Raises:
            IOError: If the compression failed.
        """
        out = io.BytesIO()

        try:
            with gzip.GzipFile(fileobj=out, mode="w") as gz:
                gz.write(data.encode("utf-8"))
        except IOError as e:
            raise IOError("Compression failed") from e

        return out.getvalue()
