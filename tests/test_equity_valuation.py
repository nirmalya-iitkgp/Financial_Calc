# tests/test_equity_valuation.py

import pytest
from mathematical_functions.equity_valuation import gordon_growth_model

# --- gordon_growth_model tests ---
def test_gordon_growth_model_basic():
    """Test basic Gordon Growth Model calculation."""
    # D1 = $2, r = 10%, g = 5%
    # Price = 2 / (0.10 - 0.05) = 2 / 0.05 = 40
    assert gordon_growth_model(2, 0.10, 0.05) == pytest.approx(40.0)

def test_gordon_growth_model_different_values():
    """Test Gordon Growth Model with different inputs."""
    # D1 = $1.50, r = 8%, g = 3%
    # Price = 1.50 / (0.08 - 0.03) = 1.50 / 0.05 = 30
    assert gordon_growth_model(1.50, 0.08, 0.03) == pytest.approx(30.0)

def test_gordon_growth_model_zero_growth():
    """Test Gordon Growth Model with zero growth rate (simplifies to perpetuity)."""
    # D1 = $1, r = 10%, g = 0%
    # Price = 1 / (0.10 - 0) = 10
    assert gordon_growth_model(1, 0.10, 0.0) == pytest.approx(10.0)

def test_gordon_growth_model_zero_dividend():
    """Test Gordon Growth Model with zero expected dividend (price should be zero)."""
    assert gordon_growth_model(0, 0.10, 0.05) == pytest.approx(0.0)

def test_gordon_growth_model_invalid_r_le_g():
    """Test Gordon Growth Model where required rate <= growth rate."""
    # r = g
    with pytest.raises(ValueError, match="The required rate of return \(r\) must be strictly greater than the growth rate \(g\).*"):
        gordon_growth_model(2, 0.05, 0.05)
    # r < g
    with pytest.raises(ValueError, match="The required rate of return \(r\) must be strictly greater than the growth rate \(g\).*"):
        gordon_growth_model(2, 0.04, 0.05)

def test_gordon_growth_model_invalid_r_non_positive():
    """Test Gordon Growth Model with non-positive required rate of return."""
    with pytest.raises(ValueError, match="The required rate of return \(r\) must be positive."):
        gordon_growth_model(2, 0.0, 0.01)
    with pytest.raises(ValueError, match="The required rate of return \(r\) must be positive."):
        gordon_growth_model(2, -0.05, -0.10) # Even if r > g in negative domain, r must be positive