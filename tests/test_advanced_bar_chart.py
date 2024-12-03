from unittest.mock import Mock

from endstone_bstats._charts.advanced_bar_chart import AdvancedBarChart


def test_get_chart_data_none():
    """Test that get_chart_data returns None when the callable returns None."""
    callable_mock = Mock(return_value=None)
    advanced_bar_chart = AdvancedBarChart("chart_id", callable_mock)

    result = advanced_bar_chart.get_chart_data()
    assert result is None


def test_get_chart_data_empty():
    """Test that get_chart_data returns None when the callable returns an empty dictionary."""
    callable_mock = Mock(return_value={})
    advanced_bar_chart = AdvancedBarChart("chart_id", callable_mock)

    result = advanced_bar_chart.get_chart_data()
    assert result is None


def test_get_chart_data_valid():
    """Test that get_chart_data processes and returns valid data correctly."""
    data = {"Bar A": [10, 20], "Bar B": [15, 25], "Bar C": [30]}
    callable_mock = Mock(return_value=data)
    advanced_bar_chart = AdvancedBarChart("chart_id", callable_mock)

    result = advanced_bar_chart.get_chart_data()
    expected_result = {"values": {"Bar A": [10, 20], "Bar B": [15, 25], "Bar C": [30]}}
    assert result == expected_result


def test_get_chart_data_some_empty_values():
    """Test that get_chart_data omits bars with empty lists."""
    data = {"Bar A": [10, 20], "Bar B": [], "Bar C": [30]}
    callable_mock = Mock(return_value=data)
    advanced_bar_chart = AdvancedBarChart("chart_id", callable_mock)

    result = advanced_bar_chart.get_chart_data()
    expected_result = {"values": {"Bar A": [10, 20], "Bar C": [30]}}
    assert result == expected_result


def test_get_chart_data_all_empty_values():
    """Test that get_chart_data returns None when all bars in the callable result have empty lists."""
    data = {"Bar A": [], "Bar B": [], "Bar C": []}
    callable_mock = Mock(return_value=data)
    advanced_bar_chart = AdvancedBarChart("chart_id", callable_mock)

    result = advanced_bar_chart.get_chart_data()
    assert result is None
