import pytest
from endstone_bstats import SimplePie, ChartDataError


def test_valid_pie_chart():
    chart = SimplePie("valid_pie_chart", lambda: "42")
    assert chart.get_chart_data() == {"value": "42"}


def test_pie_chart_data_empty_string():
    chart = SimplePie("pie_chart_with_empty_string", lambda: "")
    assert chart.get_chart_data() is None


def test_pie_chart_data_none():
    chart = SimplePie("pie_chart_with_none", lambda: None)
    assert chart.get_chart_data() is None


if __name__ == "__main__":
    pytest.main()
