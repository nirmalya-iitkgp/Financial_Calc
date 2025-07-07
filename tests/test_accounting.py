# tests/test_accounting.py

import pytest
from mathematical_functions.accounting import (
    calculate_depreciation_straight_line,
    calculate_depreciation_double_declining_balance
)

# --- calculate_depreciation_straight_line tests ---
def test_depreciation_straight_line_basic():
    """Test straight-line depreciation with basic inputs."""
    # Cost = 10000, Salvage = 1000, Useful Life = 5 years
    # Depreciable base = 9000. Annual depreciation = 9000 / 5 = 1800
    assert calculate_depreciation_straight_line(10000, 1000, 5) == pytest.approx(1800.0)

def test_depreciation_straight_line_zero_salvage():
    """Test straight-line depreciation with zero salvage value."""
    # Cost = 10000, Salvage = 0, Useful Life = 5 years
    # Depreciable base = 10000. Annual depreciation = 10000 / 5 = 2000
    assert calculate_depreciation_straight_line(10000, 0, 5) == pytest.approx(2000.0)

def test_depreciation_straight_line_one_year_life():
    """Test straight-line depreciation with a one-year useful life."""
    assert calculate_depreciation_straight_line(1000, 100, 1) == pytest.approx(900.0)

def test_depreciation_straight_line_invalid_cost_zero():
    """Test straight-line depreciation with zero cost."""
    with pytest.raises(ValueError, match="Asset cost must be positive."):
        calculate_depreciation_straight_line(0, 100, 5)

def test_depreciation_straight_line_invalid_cost_negative():
    """Test straight-line depreciation with negative cost."""
    with pytest.raises(ValueError, match="Asset cost must be positive."):
        calculate_depreciation_straight_line(-1000, 100, 5)

def test_depreciation_straight_line_invalid_salvage_negative():
    """Test straight-line depreciation with negative salvage value."""
    with pytest.raises(ValueError, match="Salvage value cannot be negative."):
        calculate_depreciation_straight_line(10000, -100, 5)

def test_depreciation_straight_line_invalid_salvage_gt_cost():
    """Test straight-line depreciation with salvage value greater than cost."""
    with pytest.raises(ValueError, match="Salvage value cannot be greater than the asset cost."):
        calculate_depreciation_straight_line(10000, 11000, 5)

def test_depreciation_straight_line_invalid_useful_life_zero():
    """Test straight-line depreciation with zero useful life."""
    with pytest.raises(ValueError, match="Useful life in years must be a positive integer."):
        calculate_depreciation_straight_line(10000, 1000, 0)

def test_depreciation_straight_line_invalid_useful_life_negative():
    """Test straight-line depreciation with negative useful life."""
    with pytest.raises(ValueError, match="Useful life in years must be a positive integer."):
        calculate_depreciation_straight_line(10000, 1000, -5)

def test_depreciation_straight_line_invalid_useful_life_float():
    """Test straight-line depreciation with float useful life."""
    with pytest.raises(ValueError, match="Useful life in years must be a positive integer."):
        calculate_depreciation_straight_line(10000, 1000, 2.5)

# --- calculate_depreciation_double_declining_balance tests ---
def test_depreciation_ddb_basic_year1():
    """Test DDB depreciation for year 1."""
    # Cost = 10000, Salvage = 1000, Useful Life = 5 years
    # DDB Rate = (1/5) * 2 = 0.40 (40%)
    # Year 1 Dep = 10000 * 0.40 = 4000
    assert calculate_depreciation_double_declining_balance(10000, 1000, 5, 1) == pytest.approx(4000.0)

def test_depreciation_ddb_year2():
    """Test DDB depreciation for year 2."""
    # Cost = 10000, Salvage = 1000, Useful Life = 5 years
    # Year 1 Book Value = 10000 - 4000 = 6000
    # Year 2 Dep = 6000 * 0.40 = 2400
    assert calculate_depreciation_double_declining_balance(10000, 1000, 5, 2) == pytest.approx(2400.0)

def test_depreciation_ddb_year3():
    """Test DDB depreciation for year 3."""
    # Year 2 Book Value = 6000 - 2400 = 3600
    # Year 3 Dep = 3600 * 0.40 = 1440
    assert calculate_depreciation_double_declining_balance(10000, 1000, 5, 3) == pytest.approx(1440.0)

def test_depreciation_ddb_year4_switch_to_straight_line_implicit():
    """Test DDB depreciation for year 4, where implicit switch to SL might occur."""
    # Year 3 Book Value = 3600 - 1440 = 2160
    # Year 4 DDB Dep = 2160 * 0.40 = 864
    # Remaining book value = 2160 - 864 = 1296
    # Salvage value = 1000
    # Current DDB calculation method clips at salvage value, effectively switching.
    # The current logic will calculate 864, but if remaining_book_value < salvage, it will cap it.
    # For year 4, 2160 (current BV) - 1000 (salvage) = 1160 depreciable base remaining for 2 years.
    # Straight-line for remaining 2 years: 1160 / 2 = 580.
    # Since 864 > 580, the code correctly limits it to 2160 - 1000 = 1160 if this were the last year,
    # or the max of straight line vs DDB if actual switch logic were there.
    # The provided function's logic is simpler: "Ensure book value does not go below salvage value"
    # This means if DDB calc makes it go below salvage, it takes only what's needed to reach salvage.
    # Year 4: BV = 2160. DDB calc = 864. New BV = 2160-864 = 1296 ( > 1000 salvage) -> takes 864.
    assert calculate_depreciation_double_declining_balance(10000, 1000, 5, 4) == pytest.approx(864.0)

def test_depreciation_ddb_year5_salvage_limit():
    """Test DDB depreciation for year 5, hitting salvage value."""
    # Year 4 Book Value = 2160 - 864 = 1296
    # Year 5 DDB Dep = 1296 * 0.40 = 518.4
    # But new BV = 1296 - 518.4 = 777.6, which is < 1000 salvage.
    # So, depreciation should be limited to 1296 - 1000 = 296
    assert calculate_depreciation_double_declining_balance(10000, 1000, 5, 5) == pytest.approx(296.0)

def test_depreciation_ddb_beyond_useful_life():
    """Test DDB depreciation beyond useful life."""
    assert calculate_depreciation_double_declining_balance(10000, 1000, 5, 6) == pytest.approx(0.0)

def test_depreciation_ddb_zero_salvage():
    """Test DDB depreciation with zero salvage value."""
    # Cost = 1000, Salvage = 0, Useful Life = 2 years
    # DDB Rate = (1/2) * 2 = 1.00 (100%)
    # Year 1 Dep = 1000 * 1.00 = 1000
    assert calculate_depreciation_double_declining_balance(1000, 0, 2, 1) == pytest.approx(1000.0)
    # Year 2 Dep: Book value = 0. So 0.
    assert calculate_depreciation_double_declining_balance(1000, 0, 2, 2) == pytest.approx(0.0)

def test_depreciation_ddb_invalid_cost():
    """Test DDB depreciation with invalid cost."""
    with pytest.raises(ValueError, match="Asset cost must be positive."):
        calculate_depreciation_double_declining_balance(0, 100, 5, 1)

def test_depreciation_ddb_invalid_salvage_negative():
    """Test DDB depreciation with negative salvage value."""
    with pytest.raises(ValueError, match="Salvage value cannot be negative."):
        calculate_depreciation_double_declining_balance(10000, -100, 5, 1)

def test_depreciation_ddb_invalid_salvage_gt_cost():
    """Test DDB depreciation with salvage value greater than cost."""
    with pytest.raises(ValueError, match="Salvage value cannot be greater than the asset cost."):
        calculate_depreciation_double_declining_balance(10000, 11000, 5, 1)

def test_depreciation_ddb_invalid_useful_life():
    """Test DDB depreciation with invalid useful life."""
    with pytest.raises(ValueError, match="Useful life in years must be a positive integer."):
        calculate_depreciation_double_declining_balance(10000, 1000, 0, 1)
    with pytest.raises(ValueError, match="Useful life in years must be a positive integer."):
        calculate_depreciation_double_declining_balance(10000, 1000, 2.5, 1)

def test_depreciation_ddb_invalid_current_year():
    """Test DDB depreciation with invalid current year."""
    with pytest.raises(ValueError, match="Current year must be a positive integer and not exceed useful_life_years."):
        calculate_depreciation_double_declining_balance(10000, 1000, 5, 0)
    with pytest.raises(ValueError, match="Current year must be a positive integer and not exceed useful_life_years."):
        calculate_depreciation_double_declining_balance(10000, 1000, 5, -1)