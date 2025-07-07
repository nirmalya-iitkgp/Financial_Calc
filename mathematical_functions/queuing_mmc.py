# mathematical_functions/queuing_mmc.py

import math

def _validate_mmc_inputs(lambda_rate: float, mu_rate: float, c: int):
    """
    Helper function to validate common M/M/c queue inputs.
    """
    if not isinstance(lambda_rate, (int, float)) or lambda_rate <= 0:
        raise ValueError("Arrival rate (lambda_rate) must be a positive number.")
    if not isinstance(mu_rate, (int, float)) or mu_rate <= 0:
        raise ValueError("Service rate (mu_rate) per server must be a positive number.")
    if not isinstance(c, int) or c <= 0:
        raise ValueError("Number of servers (c) must be a positive integer.")
    if lambda_rate >= c * mu_rate:
        raise ValueError("System is unstable: Arrival rate (lambda_rate) must be less than (c * mu_rate).")

def calculate_mmc_utilization(lambda_rate: float, mu_rate: float, c: int) -> float:
    """
    Calculates the total server utilization (rho) for an M/M/c queue.

    Args:
        lambda_rate (float): Average arrival rate (customers per unit time). Must be positive.
        mu_rate (float): Average service rate per server (customers per unit time). Must be positive.
        c (int): Number of servers. Must be a positive integer.

    Returns:
        float: The total server utilization (rho).

    Raises:
        ValueError: If inputs are invalid or if the system is unstable.
    """
    _validate_mmc_inputs(lambda_rate, mu_rate, c)
    return lambda_rate / (c * mu_rate)

def _erlang_c_formula(lambda_rate: float, mu_rate: float, c: int) -> float:
    """
    Helper function to calculate the Erlang C formula (probability of waiting) for an M/M/c queue.
    This is critical for M/M/c calculations.

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate per server.
        c (int): Number of servers.

    Returns:
        float: Probability that an arriving customer has to wait (P_wait).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mmc_inputs(lambda_rate, mu_rate, c)
    rho_server = lambda_rate / mu_rate # Utilization per server
    rho_system = lambda_rate / (c * mu_rate) # Overall system utilization

    sum_term = 0.0
    for n in range(c):
        sum_term += ((rho_server**n) / math.factorial(n))

    numerator = ((rho_server**c) / math.factorial(c)) * (1 / (1 - rho_system))
    denominator = sum_term + numerator

    if denominator == 0: # Should ideally not happen with valid inputs but for robustness
        raise ZeroDivisionError("Denominator in Erlang C formula is zero.")

    return numerator / denominator

def calculate_mmc_prob_waiting(lambda_rate: float, mu_rate: float, c: int) -> float:
    """
    Calculates the probability that an arriving customer has to wait in the queue for an M/M/c system.
    This is often referred to as the Erlang C probability.

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate per server.
        c (int): Number of servers.

    Returns:
        float: Probability of waiting (P_wait).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    return _erlang_c_formula(lambda_rate, mu_rate, c)

def calculate_mmc_avg_queue_length(lambda_rate: float, mu_rate: float, c: int) -> float:
    """
    Calculates the average number of customers waiting in the queue for an M/M/c system.

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate per server.
        c (int): Number of servers.

    Returns:
        float: Average number of customers in the queue (Lq).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mmc_inputs(lambda_rate, mu_rate, c)
    p_wait = _erlang_c_formula(lambda_rate, mu_rate, c)
    rho_server = lambda_rate / mu_rate # Utilization per server (lambda/mu)
    return (p_wait * rho_server) / (1 - (lambda_rate / (c * mu_rate)))

def calculate_mmc_avg_waiting_time_queue(lambda_rate: float, mu_rate: float, c: int) -> float:
    """
    Calculates the average time a customer spends waiting in the queue for an M/M/c system.

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate per server.
        c (int): Number of servers.

    Returns:
        float: Average time waiting in the queue (Wq).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mmc_inputs(lambda_rate, mu_rate, c)
    lq = calculate_mmc_avg_queue_length(lambda_rate, mu_rate, c)
    return lq / lambda_rate # Little's Law: Wq = Lq / lambda

def calculate_mmc_avg_system_length(lambda_rate: float, mu_rate: float, c: int) -> float:
    """
    Calculates the average number of customers in the M/M/c system (waiting + being served).

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate per server.
        c (int): Number of servers.

    Returns:
        float: Average number of customers in the system (L).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mmc_inputs(lambda_rate, mu_rate, c)
    lq = calculate_mmc_avg_queue_length(lambda_rate, mu_rate, c)
    return lq + (lambda_rate / mu_rate) # L = Lq + (lambda / mu_server)

def calculate_mmc_avg_system_time(lambda_rate: float, mu_rate: float, c: int) -> float:
    """
    Calculates the average time a customer spends in the M/M/c system (waiting + being served).

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate per server.
        c (int): Number of servers.

    Returns:
        float: Average time in the system (W).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mmc_inputs(lambda_rate, mu_rate, c)
    wq = calculate_mmc_avg_waiting_time_queue(lambda_rate, mu_rate, c)
    return wq + (1 / mu_rate) # W = Wq + E[S]