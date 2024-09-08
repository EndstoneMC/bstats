from endstone_bstats._charts import CustomChart
from typing import Callable


class SimplePie(CustomChart):
    def __init__(self, chart_id: str, get_value: Callable[[], str | None]):
        """
        Class constructor.

        Args:
            chart_id (str): The id of the chart.
            get_value (Callable[[], str | None]): The callable which is used to request the chart data.
        """
        super().__init__(chart_id)
        self.get_value = get_value

    def get_chart_data(self) -> dict | None:
        """
        Gets the data for the simple pie chart.

        Returns:
            dict | None: A dictionary with the chart data.
        """
        data = {}
        value = self.get_value()
        if not value:
            return None  # skip the chart

        data["value"] = value
        return data
