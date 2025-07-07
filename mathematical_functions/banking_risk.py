# mathematical_functions/banking_risk.py

def calculate_expected_loss(probability_of_default: float, exposure_at_default: float, loss_given_default: float) -> float:
    """
    Calculates the Expected Loss (EL) for a credit exposure.

    Args:
        probability_of_default (float): Probability of Default (PD) as a decimal (e.g., 0.05 for 5%).
                                        Must be between 0 and 1.
        exposure_at_default (float): Exposure at Default (EAD), the outstanding amount at the time of default.
                                     Must be non-negative.
        loss_given_default (float): Loss Given Default (LGD) as a decimal (e.g., 0.40 for 40%).
                                    Must be between 0 and 1.

    Returns:
        float: The Expected Loss.

    Raises:
        ValueError: If inputs are out of valid ranges.
    """
    if not (0 <= probability_of_default <= 1):
        raise ValueError("Probability of Default (PD) must be between 0 and 1.")
    if exposure_at_default < 0:
        raise ValueError("Exposure at Default (EAD) cannot be negative.")
    if not (0 <= loss_given_default <= 1):
        raise ValueError("Loss Given Default (LGD) must be between 0 and 1.")

    expected_loss = probability_of_default * exposure_at_default * loss_given_default
    return expected_loss

def calculate_asset_liability_gap(rate_sensitive_assets: float, rate_sensitive_liabilities: float) -> float:
    """
    Calculates the Asset-Liability Gap (or Interest Rate Sensitivity Gap).
    This measures the difference between rate-sensitive assets and rate-sensitive liabilities
    within a specific time bucket.

    Args:
        rate_sensitive_assets (float): Total value of assets whose interest rates will reprice
                                       or mature within a specified time period.
        rate_sensitive_liabilities (float): Total value of liabilities whose interest rates will reprice
                                            or mature within a specified time period.

    Returns:
        float: The Asset-Liability Gap. A positive gap means assets reprice faster or are larger,
               a negative gap means liabilities reprice faster or are larger.
    """
    asset_liability_gap = rate_sensitive_assets - rate_sensitive_liabilities
    return asset_liability_gap