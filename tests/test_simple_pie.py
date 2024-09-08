import pytest
from endstone_bstats import SimplePie, ChartDataError


def test_valid_simple_pie():
    chart = SimplePie("valid_simple_pie", lambda: "42")
    assert chart.get_chart_data() == {"value": "42"}


def test_simple_pie_data_empty_string():
    chart = SimplePie("simple_pie_with_empty_string", lambda: "")
    assert chart.get_chart_data() is None


def test_simple_pie_data_none():
    chart = SimplePie("simple_pie_with_none", lambda: None)
    assert chart.get_chart_data() is None


if __name__ == "__main__":
    pytest.main()
