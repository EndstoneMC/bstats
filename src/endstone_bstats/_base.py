import gzip
import json
import random
import uuid
from io import BytesIO
from typing import Any, Callable, Dict, Optional, Set

import requests

from endstone_bstats._executor import ScheduledThreadPoolExecutor


class MetricsBase:
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
        enabled: bool,
        platform_data_appender: Callable[[Dict[str, Any]], Dict[str, Any]],
        service_data_appender: Callable[[Dict[str, Any]], Dict[str, Any]],
        task_submitter: Optional[Callable[[Callable[[], None]], None]],
        check_service_enabled: Callable[[], bool],
        error_logger: Callable[[str, Exception], None],
        info_logger: Callable[[str], None],
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
            enabled (bool): Whether or not data sending is enabled.
            platform_data_appender (Callable[[Dict[str, Any]], Dict[str, Any]]): A consumer to append platform-specific data.
            service_data_appender (Callable[[Dict[str, Any]], Dict[str, Any]]): A consumer to append service-specific data.
            task_submitter (Optional[Callable[[Callable[[], None]], None]]): A consumer to handle the submit task.
            check_service_enabled (Callable[[], bool]): A supplier to check if the service is still enabled.
            error_logger (Callable[[str, Exception], None]): A consumer for error logging.
            info_logger (Callable[[str], None]): A consumer for info logging.
            log_errors (bool): Whether or not errors should be logged.
            log_sent_data (bool): Whether or not the sent data should be logged.
            log_response_status_text (bool): Whether or not the response status text should be logged.
        """
        self._platform = platform
        self._server_uuid = server_uuid
        self._service_id = service_id
        self._enabled = enabled
        self._platform_data_appender = platform_data_appender
        self._service_data_appender = service_data_appender
        self._task_submitter = task_submitter
        self._check_service_enabled = check_service_enabled
        self._error_logger = error_logger
        self._info_logger = info_logger
        self._log_errors = log_errors
        self._log_sent_data = log_sent_data
        self._log_response_status_text = log_response_status_text
        self._custom_charts: Set = set()
        self._executor = ScheduledThreadPoolExecutor(max_workers=1)

        if self._enabled:
            self._start_submitting()

    def add_custom_chart(self, chart: Any):
        """
        Adds a custom chart.

        Args:
            chart: The custom chart to add.
        """
        self._custom_charts.add(chart)

    def shutdown(self):
        """Shuts down the scheduler."""
        self._executor.shutdown()

    def _start_submitting(self):
        """
        Starts the submitting process with initial and periodic delays.
        """

        def submit_task():
            if not self._enabled or not self._check_service_enabled():
                self.shutdown()
                return

            if self._task_submitter is not None:
                self._task_submitter(self._submit_data)
            else:
                self._submit_data()

        initial_delay = int((3 + random.random() * 3) * 60)
        second_delay = int((random.random() * 30) * 60)

        self._executor.submit(submit_task, initial_delay)
        self._executor.submit_at_fixed_rate(
            submit_task, initial_delay + second_delay, 60 * 30
        )

    def _submit_data(self):
        """
        Constructs the JSON data and sends it to bStats.
        """

        base_json = self._platform_data_appender({})
        service_json = self._service_data_appender({})

        chart_data = []
        for chart in self._custom_charts:
            chart_data.append(
                chart.get_request_json_object(self._error_logger, self._log_errors)
            )

        service_json["id"] = self._service_id
        service_json["customCharts"] = chart_data
        base_json["service"] = service_json
        base_json["serverUUID"] = str(self._server_uuid)
        # base_json["metricsVersion"] = self.METRICS_VERSION

        try:
            self._send_data(base_json)
        except Exception as e:
            if self._log_errors:
                self._error_logger("Could not submit bStats metrics data", e)

    def _send_data(self, data: Dict[str, Any]):
        """
        Sends the JSON data to bStats.

        Args:
            data: The JSON data to send.
        """
        if self._log_sent_data:
            self._info_logger(f"Sent bStats metrics data: {data}")

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
            self._info_logger(
                f"Sent data to bStats and received response: {response.text}"
            )

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
