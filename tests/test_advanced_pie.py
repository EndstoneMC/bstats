import pytest

from endstone_bstats import AdvancedPie


def test_valid_advanced_pie():
    chart = AdvancedPie("valid_advanced_pie", lambda: {"key1": 10, "key2": 5})
    assert chart.get_chart_data() == {"values": {"key1": 10, "key2": 5}}


def test_advanced_pie_chart_data_empty_dict():
    chart = AdvancedPie("advanced_pie_chart_with_empty_dict", lambda: {})
    assert chart.get_chart_data() is None


def test_advanced_pie_chart_data_none():
    chart = AdvancedPie("advanced_pie_chart_with_none", lambda: None)
    assert chart.get_chart_data() is None


def test_advanced_pie_chart_data_all_zero_values():
    chart = AdvancedPie(
        "advanced_pie_chart_with_all_zero_values", lambda: {"key1": 0, "key2": 0}
    )
    assert chart.get_chart_data() is None


def test_advanced_pie_chart_data_mixed_values():
    chart = AdvancedPie(
        "advanced_pie_chart_with_mixed_values",
        lambda: {"key1": 0, "key2": 10, "key3": 0},
    )
    assert chart.get_chart_data() == {"values": {"key2": 10}}


if __name__ == "__main__":
    pytest.main()
