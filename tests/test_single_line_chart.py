from endstone_bstats import SingleLineChart


def test_valid_single_line_chart():
    chart = SingleLineChart("valid_single_line_chart", lambda: 42)
    assert chart.get_chart_data() == {"value": 42}


def test_single_line_chart_data_zero():
    chart = SingleLineChart("single_line_chart_with_none", lambda: 0)
    assert chart.get_chart_data() is None
