import gzip
import json
import logging
import random
import uuid
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Callable, Dict, Set, final

import requests

from endstone_bstats._executor import ScheduledThreadPoolExecutor


class MetricsBase(ABC):
    """
    The MetricsBase class to handle sending metrics to bStats.

    Attributes:
        METRICS_VERSION (str): The version of the Metrics class.
        REPORT_URL (str): The URL to which data is reported.
    """

    METRICS_VERSION = "3.0.3"
    REPORT_URL = "https://bStats.org/api/v2/data/{platform}"

    def __init__(
        self,
        platform: str,
        server_uuid: uuid.UUID,
        service_id: int,
        log_errors: bool,
        log_sent_data: bool,
        log_response_status_text: bool,
    ):
        """
        Initializes the MetricsBase instance.

        Args:
            platform (str): The platform of the service.
            server_uuid (uuid.UUID): The server UUID.
            service_id (int): The service ID.
            log_errors (bool): Whether errors should be logged.
            log_sent_data (bool): Whether the data sent should be logged.
            log_response_status_text (bool): Whether the response status text should be logged.
        """
        self._platform = platform
        self._server_uuid = server_uuid
        self._service_id = service_id
        self._log_errors = log_errors
        self._log_sent_data = log_sent_data
        self._log_response_status_text = log_response_status_text
        self._custom_charts: Set = set()
        self._executor = ScheduledThreadPoolExecutor(max_workers=1)

        if self.enabled:
            self._start_submitting()

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """
        Whether data sending is enabled.
        """

    @property
    @abstractmethod
    def service_enabled(self) -> bool:
        """
        Whether the service is enabled.
        """

    def append_platform_data(self, data: Dict[str, Any]) -> None:
        """
        Append platform-specific data.

        Args:
            data (Dict[str, Any]): The data to append platform-specific values to.
        """
        pass

    def append_service_data(self, data: Dict[str, Any]) -> None:
        """
        Append service-specific data.

        Args:
            data (Dict[str, Any]): The data to append service-specific values to.
        """
        pass

    def submit_task(self, task: Callable[[], None]) -> None:
        """
        Submit the given task

        Args:
            task (Callable[[], None]): The task to be submitted.
        """
        task()

    def log_info(self, message: str) -> None:
        """
        Logs info message.

        Args:
            message (str): The info message.
        """
        logging.info(message)

    def log_error(self, message: str, exception: Exception) -> None:
        """
        Logs error message.

        Args:
            message (str): The error message.
            exception (Exception): The exception that occurred.
        """
        logging.warning(message, exc_info=exception)

    @final
    def add_custom_chart(self, chart: Any):
        """
        Adds a custom chart.

        Args:
            chart: The custom chart to add.
        """
        self._custom_charts.add(chart)

    @final
    def shutdown(self):
        """Shuts down the scheduler."""
        self._executor.shutdown()

    @final
    def _start_submitting(self):
        """
        Starts the submitting process with initial and periodic delays.
        """

        def submit_task():
            if not self.enabled or not self.service_enabled:
                self.shutdown()
                return

            self.submit_task(self._submit_data)

        initial_delay = int((3 + random.random() * 3) * 60)
        second_delay = int((random.random() * 30) * 60)

        self._executor.submit(submit_task, initial_delay)
        self._executor.submit_at_fixed_rate(
            submit_task, initial_delay + second_delay, 60 * 30
        )

    @final
    def _submit_data(self):
        """
        Constructs the JSON data and sends it to bStats.
        """

        platform_data = {}
        self.append_platform_data(platform_data)

        service_data = {}
        self.append_service_data(service_data)

        chart_data = []
        for chart in self._custom_charts:
            try:
                chart_json = chart._get_request_json_object()
                if chart_json is not None:
                    chart_data.append(chart_json)
            except Exception as e:
                if self._log_errors:
                    self.log_error(
                        f"Failed to get data for custom chart with id {chart.chart_id}",
                        e,
                    )

        service_data["id"] = self._service_id
        service_data["customCharts"] = chart_data
        platform_data["service"] = service_data
        platform_data["serverUUID"] = str(self._server_uuid)

        try:
            self._send_data(platform_data)
        except Exception as e:
            if self._log_errors:
                self.log_error("Could not submit bStats metrics data", e)

    @final
    def _send_data(self, data: Dict[str, Any]):
        """
        Sends the JSON data to bStats.

        Args:
            data: The JSON data to send.
        """
        if self._log_sent_data:
            self.log_info(f"Sent bStats metrics data: {data}")

        url = self.REPORT_URL.format(platform=self._platform)
        compressed_data = self._compress(data)

        headers = {
            "Accept": "application/json",
            "Connection": "close",
            "Content-Encoding": "gzip",
            "Content-Length": str(len(compressed_data)),
            "Content-Type": "application/json",
            "User-Agent": "Metrics-Service/1",
        }

        response = requests.post(url, headers=headers, data=compressed_data)
        response.raise_for_status()

        if self._log_response_status_text:
            self.log_info(f"Sent data to bStats and received response: {response.text}")

    @staticmethod
    def _compress(data: Dict[str, Any]) -> bytes:
        """
        Compresses the given data using gzip.

        Args:
            data (dict): The data to be compressed.

        Returns:
            bytes: The compressed data.
        """
        bio = BytesIO()
        with gzip.GzipFile(fileobj=bio, mode="wb") as gzip_file:
            gzip_file.write(json.dumps(data).encode("utf-8"))

        return bio.getvalue()
