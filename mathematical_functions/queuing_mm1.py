# mathematical_functions/queuing_mm1.py

import math

def _validate_mm1_inputs(lambda_rate: float, mu_rate: float):
    """
    Helper function to validate common M/M/1 queue inputs.
    """
    if not isinstance(lambda_rate, (int, float)) or lambda_rate <= 0:
        raise ValueError("Arrival rate (lambda_rate) must be a positive number.")
    if not isinstance(mu_rate, (int, float)) or mu_rate <= 0:
        raise ValueError("Service rate (mu_rate) must be a positive number.")
    if lambda_rate >= mu_rate:
        raise ValueError("System is unstable: Arrival rate (lambda_rate) must be less than service rate (mu_rate).")

def calculate_mm1_utilization(lambda_rate: float, mu_rate: float) -> float:
    """
    Calculates the server utilization (rho) for an M/M/1 queue.

    Args:
        lambda_rate (float): Average arrival rate (customers per unit time). Must be positive.
        mu_rate (float): Average service rate (customers per unit time). Must be positive.

    Returns:
        float: The server utilization (rho).

    Raises:
        ValueError: If lambda_rate or mu_rate are invalid, or if the system is unstable.
    """
    _validate_mm1_inputs(lambda_rate, mu_rate)
    return lambda_rate / mu_rate

def calculate_mm1_avg_system_length(lambda_rate: float, mu_rate: float) -> float:
    """
    Calculates the average number of customers in the M/M/1 system (waiting + being served).

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate.

    Returns:
        float: Average number of customers in the system (L).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mm1_inputs(lambda_rate, mu_rate)
    rho = calculate_mm1_utilization(lambda_rate, mu_rate)
    return rho / (1 - rho)

def calculate_mm1_avg_queue_length(lambda_rate: float, mu_rate: float) -> float:
    """
    Calculates the average number of customers waiting in the queue for an M/M/1 system.

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate.

    Returns:
        float: Average number of customers in the queue (Lq).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mm1_inputs(lambda_rate, mu_rate)
    rho = calculate_mm1_utilization(lambda_rate, mu_rate)
    return (rho**2) / (1 - rho)

def calculate_mm1_avg_waiting_time_system(lambda_rate: float, mu_rate: float) -> float:
    """
    Calculates the average time a customer spends in the M/M/1 system (waiting + being served).

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate.

    Returns:
        float: Average time in the system (W).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mm1_inputs(lambda_rate, mu_rate)
    return 1 / (mu_rate - lambda_rate)

def calculate_mm1_avg_waiting_time_queue(lambda_rate: float, mu_rate: float) -> float:
    """
    Calculates the average time a customer spends waiting in the queue for an M/M/1 system.

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate.

    Returns:
        float: Average time waiting in the queue (Wq).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mm1_inputs(lambda_rate, mu_rate)
    return lambda_rate / (mu_rate * (mu_rate - lambda_rate))

def calculate_mm1_prob_n_customers(n: int, lambda_rate: float, mu_rate: float) -> float:
    """
    Calculates the probability of having 'n' customers in the M/M/1 system.

    Args:
        n (int): The number of customers in the system (n >= 0).
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate.

    Returns:
        float: The probability P_n.

    Raises:
        ValueError: If n is negative, or if inputs are invalid or the system is unstable.
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Number of customers (n) must be a non-negative integer.")
    _validate_mm1_inputs(lambda_rate, mu_rate)
    rho = calculate_mm1_utilization(lambda_rate, mu_rate)
    return (1 - rho) * (rho**n)