# mathematical_functions/equity_valuation.py

def gordon_growth_model(D1: float, r: float, g: float) -> float:
    """
    Calculates the present value of a stock using the Gordon Growth Model (Dividend Discount Model - Constant Growth).
    This model assumes that dividends will grow at a constant rate indefinitely.

    Args:
        D1 (float): The expected dividend per share at the end of the first period (next year's dividend).
        r (float): The investor's required rate of return or discount rate (as a decimal).
                   This is often the cost of equity (Ke) from CAPM.
        g (float): The constant growth rate of dividends (as a decimal).

    Returns:
        float: The calculated intrinsic value (price) of the stock.

    Raises:
        ValueError: If 'r' is not greater than 'g', which would result in an undefined
                    or non-meaningful (infinite or negative) stock price.
                    Also if 'r' is non-positive.

    Assumptions/Limitations:
    - Dividends grow at a constant rate 'g' forever.
    - The growth rate 'g' is less than the required rate of return 'r' (r > g).
    - The required rate of return 'r' is constant.
    - This model is sensitive to inputs, especially (r - g).
    """
    if r <= 0:
        raise ValueError("The required rate of return (r) must be positive.")
    if r <= g:
        raise ValueError("The required rate of return (r) must be strictly greater than the growth rate (g) for a finite and positive stock price.")
    
    stock_price = D1 / (r - g)
    return stock_price