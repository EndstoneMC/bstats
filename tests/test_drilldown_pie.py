import pytest
from unittest.mock import Mock
from typing import Dict, Optional
from endstone_bstats._charts.drilldown_pie import DrilldownPie


def test_get_chart_data_none():
    """Test that get_chart_data returns None when the callable returns None."""
    callable_mock = Mock(return_value=None)
    drilldown_pie = DrilldownPie("chart_id", callable_mock)

    result = drilldown_pie.get_chart_data()
    assert result is None


def test_get_chart_data_empty():
    """Test that get_chart_data returns None when the callable returns an empty dictionary."""
    callable_mock = Mock(return_value={})
    drilldown_pie = DrilldownPie("chart_id", callable_mock)

    result = drilldown_pie.get_chart_data()
    assert result is None


def test_get_chart_data_valid():
    """Test that get_chart_data processes and returns valid data correctly."""
    data = {
        "Category A": {"Sub A1": 10, "Sub A2": 20},
        "Category B": {"Sub B1": 15, "Sub B2": 25},
        "Category C": {}
    }
    callable_mock = Mock(return_value=data)
    drilldown_pie = DrilldownPie("chart_id", callable_mock)

    result = drilldown_pie.get_chart_data()
    expected_result = {
        "values": {
            "Category A": {"Sub A1": 10, "Sub A2": 20},
            "Category B": {"Sub B1": 15, "Sub B2": 25}
        }
    }
    assert result == expected_result


def test_get_chart_data_some_empty_values():
    """Test that get_chart_data omits empty sub-dictionaries."""
    data = {
        "Category A": {"Sub A1": 10, "Sub A2": 20},
        "Category B": {},
    }
    callable_mock = Mock(return_value=data)
    drilldown_pie = DrilldownPie("chart_id", callable_mock)

    result = drilldown_pie.get_chart_data()
    expected_result = {
        "values": {
            "Category A": {"Sub A1": 10, "Sub A2": 20},
        }
    }
    assert result == expected_result


def test_get_chart_data_all_empty_values():
    """Test that get_chart_data returns None when all sub-dictionaries in the callable result are empty."""
    data = {
        "Category A": {},
        "Category B": {},
        "Category C": {}
    }
    callable_mock = Mock(return_value=data)
    drilldown_pie = DrilldownPie("chart_id", callable_mock)

    result = drilldown_pie.get_chart_data()
    assert result is None
