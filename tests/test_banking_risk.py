# tests/test_banking_risk.py

import pytest
from mathematical_functions.banking_risk import (
    calculate_expected_loss,
    calculate_asset_liability_gap
)

# --- calculate_expected_loss tests ---
def test_expected_loss_basic():
    """Test Expected Loss calculation with basic values."""
    # PD = 2%, EAD = $100,000, LGD = 40%
    # EL = 0.02 * 100000 * 0.40 = 800
    assert calculate_expected_loss(0.02, 100000, 0.40) == pytest.approx(800.0)

def test_expected_loss_zero_pd():
    """Test Expected Loss with zero Probability of Default."""
    assert calculate_expected_loss(0.0, 100000, 0.40) == pytest.approx(0.0)

def test_expected_loss_zero_ead():
    """Test Expected Loss with zero Exposure at Default."""
    assert calculate_expected_loss(0.02, 0, 0.40) == pytest.approx(0.0)

def test_expected_loss_zero_lgd():
    """Test Expected Loss with zero Loss Given Default."""
    assert calculate_expected_loss(0.02, 100000, 0.0) == pytest.approx(0.0)

def test_expected_loss_full_lgd():
    """Test Expected Loss with 100% Loss Given Default."""
    assert calculate_expected_loss(0.02, 100000, 1.0) == pytest.approx(2000.0)

def test_expected_loss_invalid_pd_below_range():
    """Test Expected Loss with PD below 0."""
    with pytest.raises(ValueError, match="Probability of Default \(PD\) must be between 0 and 1."):
        calculate_expected_loss(-0.01, 100000, 0.40)

def test_expected_loss_invalid_pd_above_range():
    """Test Expected Loss with PD above 1."""
    with pytest.raises(ValueError, match="Probability of Default \(PD\) must be between 0 and 1."):
        calculate_expected_loss(1.1, 100000, 0.40)

def test_expected_loss_invalid_ead_negative():
    """Test Expected Loss with negative EAD."""
    with pytest.raises(ValueError, match="Exposure at Default \(EAD\) cannot be negative."):
        calculate_expected_loss(0.02, -100, 0.40)

def test_expected_loss_invalid_lgd_below_range():
    """Test Expected Loss with LGD below 0."""
    with pytest.raises(ValueError, match="Loss Given Default \(LGD\) must be between 0 and 1."):
        calculate_expected_loss(0.02, 100000, -0.1)

def test_expected_loss_invalid_lgd_above_range():
    """Test Expected Loss with LGD above 1."""
    with pytest.raises(ValueError, match="Loss Given Default \(LGD\) must be between 0 and 1."):
        calculate_expected_loss(0.02, 100000, 1.1)

# --- calculate_asset_liability_gap tests ---
def test_asset_liability_gap_positive():
    """Test Asset-Liability Gap with positive result (assets > liabilities)."""
    assert calculate_asset_liability_gap(1000000, 800000) == pytest.approx(200000.0)

def test_asset_liability_gap_negative():
    """Test Asset-Liability Gap with negative result (assets < liabilities)."""
    assert calculate_asset_liability_gap(800000, 1000000) == pytest.approx(-200000.0)

def test_asset_liability_gap_zero():
    """Test Asset-Liability Gap when assets equal liabilities."""
    assert calculate_asset_liability_gap(500000, 500000) == pytest.approx(0.0)

def test_asset_liability_gap_zero_values():
    """Test Asset-Liability Gap with zero values."""
    assert calculate_asset_liability_gap(0, 0) == pytest.approx(0.0)

def test_asset_liability_gap_negative_inputs():
    """Test Asset-Liability Gap with negative inputs (valid if represents negative balances)."""
    # E.g., Negative assets could mean very specific accounting, but mathematically valid for subtraction
    assert calculate_asset_liability_gap(-100000, -50000) == pytest.approx(-50000.0)