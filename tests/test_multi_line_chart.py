from unittest.mock import Mock

from endstone_bstats._charts.multi_line_chart import MultiLineChart


def test_get_chart_data_none():
    """Test that get_chart_data returns None when the callable returns None."""
    callable_mock = Mock(return_value=None)
    multi_line_chart = MultiLineChart("chart_id", callable_mock)

    result = multi_line_chart.get_chart_data()
    assert result is None


def test_get_chart_data_empty():
    """Test that get_chart_data returns None when the callable returns an empty dictionary."""
    callable_mock = Mock(return_value={})
    multi_line_chart = MultiLineChart("chart_id", callable_mock)

    result = multi_line_chart.get_chart_data()
    assert result is None


def test_get_chart_data_valid():
    """Test that get_chart_data processes and returns valid data correctly."""
    data = {"Line A": 10, "Line B": 20, "Line C": 30}
    callable_mock = Mock(return_value=data)
    multi_line_chart = MultiLineChart("chart_id", callable_mock)

    result = multi_line_chart.get_chart_data()
    expected_result = {"values": {"Line A": 10, "Line B": 20, "Line C": 30}}
    assert result == expected_result


def test_get_chart_data_some_zero_values():
    """Test that get_chart_data omits keys with zero values."""
    data = {"Line A": 10, "Line B": 0, "Line C": 30}
    callable_mock = Mock(return_value=data)
    multi_line_chart = MultiLineChart("chart_id", callable_mock)

    result = multi_line_chart.get_chart_data()
    expected_result = {"values": {"Line A": 10, "Line C": 30}}
    assert result == expected_result


def test_get_chart_data_all_zero_values():
    """Test that get_chart_data returns None when all values in the callable result are zero."""
    data = {"Line A": 0, "Line B": 0, "Line C": 0}
    callable_mock = Mock(return_value=data)
    multi_line_chart = MultiLineChart("chart_id", callable_mock)

    result = multi_line_chart.get_chart_data()
    assert result is None
