import pytest
from endstone_bstats import CustomChart, ChartDataError


class TestCustomChart(CustomChart):
    __test__ = False

    def __init__(self, chart_id, data):
        super().__init__(chart_id)
        self._data = data

    def get_chart_data(self):
        if isinstance(self._data, Exception):
            raise self._data

        return self._data


def test_valid_chart_data():
    chart = TestCustomChart("valid_chart", {"key": "value"})
    expected_result = {"chartId": "valid_chart", "data": {"key": "value"}}
    assert chart._get_request_json_object() == expected_result


def test_empty_chart_id():
    with pytest.raises(ValueError, match="chart_id cannot be None or empty!"):
        TestCustomChart("", {"key": "value"})


def test_chart_data_returns_none():
    chart = TestCustomChart("chart_with_none_data", None)
    assert chart._get_request_json_object() is None


def test_chart_data_exception():
    exception_message = "Data retrieval error"
    chart = TestCustomChart("chart_throws_exception", Exception(exception_message))

    with pytest.raises(
        ChartDataError,
        match="Failed to get data for custom chart with id chart_throws_exception",
    ) as exc_info:
        chart._get_request_json_object()

    assert str(exc_info.value.__cause__) == exception_message
