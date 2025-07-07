# mathematical_functions/portfolio_management.py

def calculate_capm_return(risk_free_rate: float, market_risk_premium: float, beta: float) -> float:
    """
    Calculates the expected return of an asset or portfolio using the Capital Asset Pricing Model (CAPM).

    The CAPM is a widely used financial model that calculates the expected return on an asset
    or investment based on its systematic risk.

    Formula: Expected Return = Risk-Free Rate + Beta * (Market Risk Premium)

    Args:
        risk_free_rate (float): The rate of return on a risk-free asset (e.g., government bonds)
                                as a decimal (e.g., 0.03 for 3%).
        market_risk_premium (float): The expected return of the market portfolio minus the risk-free rate
                                     (E(Rm) - Rf), as a decimal (e.g., 0.07 for 7%).
        beta (float): The sensitivity of the asset's or portfolio's return to the market's return.
                      A beta of 1 means the asset's price moves with the market.
                      A beta > 1 means it's more volatile than the market.
                      A beta < 1 means it's less volatile than the market.

    Returns:
        float: The expected return of the asset or portfolio as a decimal.

    Assumptions/Limitations:
    - Assumes the CAPM assumptions hold (e.g., investors are rational, frictionless markets,
      homogeneous expectations).
    - Beta is the only measure of systematic risk; it does not account for idiosyncratic (specific) risk.
    - Market risk premium and risk-free rate are assumed to be constant or accurately estimated.
    - Uses historical data for beta, which may not be indicative of future performance.
    """
    expected_return = risk_free_rate + beta * market_risk_premium
    return expected_return

def fama_french_3_factor_expected_return(risk_free_rate: float, market_beta: float, smb_beta: float, hml_beta: float,
                                         market_excess_return: float, smb_return: float, hml_return: float) -> float:
    """
    Calculates the expected return of an asset or portfolio using the Fama-French Three-Factor Model.
    This model extends the CAPM by adding factors for size (SMB) and value (HML) to explain
    asset returns beyond just market risk.

    Formula: Expected Return = Risk-Free Rate + Beta_Market * (Market Excess Return) +
                               Beta_SMB * (SMB Factor Return) + Beta_HML * (HML Factor Return)

    Args:
        risk_free_rate (float): The risk-free rate (as a decimal, e.g., 0.03).
        market_beta (float): Sensitivity (beta) of the asset/portfolio to the market's excess return.
        smb_beta (float): Sensitivity (beta) of the asset/portfolio to the SMB (Small Minus Big) factor.
                          SMB captures the excess return of small-cap companies over large-cap companies.
        hml_beta (float): Sensitivity (beta) of the asset/portfolio to the HML (High Minus Low) factor.
                          HML captures the excess return of high book-to-market (value) companies
                          over low book-to-market (growth) companies.
        market_excess_return (float): Expected excess return of the market portfolio (Rm - Rf) (as a decimal).
        smb_return (float): Expected return of the SMB factor portfolio (as a decimal).
                            (Return of small-cap stocks - Return of large-cap stocks)
        hml_return (float): Expected return of the HML factor portfolio (as a decimal).
                            (Return of high book-to-market stocks - Return of low book-to-market stocks)

    Returns:
        float: The expected return of the asset or portfolio (as a decimal).

    Assumptions/Limitations:
    - Assumes the Fama-French Three-Factor Model accurately describes asset returns.
    - Factor returns and betas are expected values, often derived from historical regressions.
    - Does not account for transaction costs, taxes, or liquidity effects.
    - Model may not fully explain returns in all market conditions or for all asset classes.
    """
    expected_return = risk_free_rate + \
                      market_beta * market_excess_return + \
                      smb_beta * smb_return + \
                      hml_beta * hml_return
    return expected_return

def fama_french_5_factor_expected_return(risk_free_rate: float, market_beta: float, smb_beta: float, hml_beta: float,
                                         rmw_beta: float, cma_beta: float,
                                         market_excess_return: float, smb_return: float, hml_return: float,
                                         rmw_return: float, cma_return: float) -> float:
    """
    Calculates the expected return of an asset or portfolio using the Fama-French Five-Factor Model.
    This model extends the three-factor model by adding factors for profitability (RMW) and investment (CMA).

    Formula: Expected Return = Risk-Free Rate + Beta_Market * (Market Excess Return) +
                               Beta_SMB * (SMB Factor Return) + Beta_HML * (HML Factor Return) +
                               Beta_RMW * (RMW Factor Return) + Beta_CMA * (CMA Factor Return)

    Args:
        risk_free_rate (float): The risk-free rate (as a decimal).
        market_beta (float): Sensitivity (beta) to the market's excess return.
        smb_beta (float): Sensitivity (beta) to the SMB (Small Minus Big) factor.
        hml_beta (float): Sensitivity (beta) to the HML (High Minus Low) factor.
        rmw_beta (float): Sensitivity (beta) to the RMW (Robust Minus Weak) profitability factor.
                          RMW captures the excess return of companies with high operating profitability
                          over those with low operating profitability.
        cma_beta (float): Sensitivity (beta) to the CMA (Conservative Minus Aggressive) investment factor.
                          CMA captures the excess return of companies that invest conservatively
                          over those that invest aggressively.
        market_excess_return (float): Expected excess return of the market portfolio (as a decimal).
        smb_return (float): Expected return of the SMB factor portfolio (as a decimal).
        hml_return (float): Expected return of the HML factor portfolio (as a decimal).
        rmw_return (float): Expected return of the RMW factor portfolio (as a decimal).
        cma_return (float): Expected return of the CMA factor portfolio (as a decimal).

    Returns:
        float: The expected return of the asset or portfolio (as a decimal).

    Assumptions/Limitations:
    - Assumes the Fama-French Five-Factor Model accurately describes asset returns.
    - Factor returns and betas are expected values, often derived from historical regressions.
    - Does not account for transaction costs, taxes, or liquidity effects.
    - Model complexity may lead to overfitting or challenges in data availability for all factors.
    """
    expected_return = risk_free_rate + \
                      market_beta * market_excess_return + \
                      smb_beta * smb_return + \
                      hml_beta * hml_return + \
                      rmw_beta * rmw_return + \
                      cma_beta * cma_return
    return expected_return

def calculate_sharpe_ratio(portfolio_return: float, risk_free_rate: float, portfolio_standard_deviation: float) -> float:
    """
    Calculates the Sharpe Ratio of a portfolio.

    The Sharpe Ratio measures the excess return (or risk premium) per unit of total risk
    (standard deviation) in an investment asset or a portfolio. A higher Sharpe Ratio
    indicates a better risk-adjusted return.

    Formula: Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio Standard Deviation

    Args:
        portfolio_return (float): The total return of the portfolio as a decimal (e.g., 0.10 for 10%).
        risk_free_rate (float): The risk-free rate of return as a decimal (e.g., 0.03 for 3%).
        portfolio_standard_deviation (float): The standard deviation of the portfolio's returns
                                              as a decimal (e.g., 0.15 for 15%).
                                              Must be a positive value.

    Returns:
        float: The calculated Sharpe Ratio.

    Raises:
        ValueError: If `portfolio_standard_deviation` is zero or negative, as this would
                    result in division by zero or a mathematically meaningless result.

    Assumptions/Limitations:
    - Assumes returns are normally distributed (or at least symmetric). Skewness or kurtosis
      in returns can make the Sharpe Ratio less reliable.
    - Uses historical standard deviation as a proxy for future risk, which may not hold true.
    - Does not differentiate between upside and downside volatility (all volatility is treated as risk).
    - Requires consistency in the time period for all inputs (e.g., all annual returns and
      annual standard deviation, or all monthly).
    - The risk-free rate should match the frequency of the portfolio return and standard deviation.
    """
    if portfolio_standard_deviation <= 0:
        raise ValueError("Portfolio standard deviation must be positive to calculate Sharpe Ratio.")

    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_standard_deviation
    return sharpe_ratio