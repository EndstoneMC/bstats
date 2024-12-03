from __future__ import annotations

from typing import Callable, Dict

from endstone_bstats._charts.custom_chart import CustomChart


class SimpleBarChart(CustomChart):
    def __init__(
            self, chart_id: str, get_values: Callable[[], Dict[str, int] | None]
    ) -> None:
        """
        Class constructor.

        Args:
            chart_id (str): The id of the chart.
            get_values (Callable[[], Dict[str, int] | None]): The callable which is used to request the chart data.
        """
        super().__init__(chart_id)
        self.get_values = get_values

    def get_chart_data(self) -> dict | None:
        """
        Gets the data for the simple bar chart.

        Returns:
            dict | None: A dictionary with the chart data.
        """
        map_values = self.get_values()
        if not map_values:
            return None

        values = {key: [value] for key, value in map_values.items()}

        return {"values": values}