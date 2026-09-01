from app.risk_engine import assess_risk


def test_uncontrolled_critical_risk():
    result = assess_risk(5, 5)
    assert result.base_score == 25
    assert result.adjusted_score == 25
    assert result.severity == "Critical"


def test_medium_risk():
    result = assess_risk(3, 3)
    assert result.adjusted_score == 9
    assert result.severity == "Medium"


def test_controls_reduce_score():
    result = assess_risk(5, 5, 80)
    assert result.base_score == 25
    assert result.adjusted_score == 5
    assert result.severity == "Medium"


def test_invalid_values():
    for args in [(0, 3), (3, 6), (3, 3, 101)]:
        try:
            assess_risk(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input was accepted")
