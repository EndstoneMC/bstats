from unittest.mock import Mock

from endstone_bstats._charts.simple_bar_chart import SimpleBarChart


def test_get_chart_data_none():
    """Test that get_chart_data returns None when the callable returns None."""
    callable_mock = Mock(return_value=None)
    simple_bar_chart = SimpleBarChart("chart_id", callable_mock)

    result = simple_bar_chart.get_chart_data()
    assert result is None


def test_get_chart_data_empty():
    """Test that get_chart_data returns None when the callable returns an empty dictionary."""
    callable_mock = Mock(return_value={})
    simple_bar_chart = SimpleBarChart("chart_id", callable_mock)

    result = simple_bar_chart.get_chart_data()
    assert result is None


def test_get_chart_data_valid():
    """Test that get_chart_data processes and returns valid data correctly."""
    data = {"Bar A": 10, "Bar B": 20, "Bar C": 30}
    callable_mock = Mock(return_value=data)
    simple_bar_chart = SimpleBarChart("chart_id", callable_mock)

    result = simple_bar_chart.get_chart_data()
    expected_result = {"values": {"Bar A": [10], "Bar B": [20], "Bar C": [30]}}
    assert result == expected_result


def test_get_chart_data_some_zero_values():
    """Test that get_chart_data includes zero values wrapped in a list."""
    data = {"Bar A": 10, "Bar B": 0, "Bar C": 30}
    callable_mock = Mock(return_value=data)
    simple_bar_chart = SimpleBarChart("chart_id", callable_mock)

    result = simple_bar_chart.get_chart_data()
    expected_result = {"values": {"Bar A": [10], "Bar B": [0], "Bar C": [30]}}
    assert result == expected_result


def test_get_chart_data_all_zero_values():
    """Test that get_chart_data includes bars with zero values wrapped in a list."""
    data = {"Bar A": 0, "Bar B": 0, "Bar C": 0}
    callable_mock = Mock(return_value=data)
    simple_bar_chart = SimpleBarChart("chart_id", callable_mock)

    result = simple_bar_chart.get_chart_data()
    expected_result = {"values": {"Bar A": [0], "Bar B": [0], "Bar C": [0]}}
    assert result == expected_result
