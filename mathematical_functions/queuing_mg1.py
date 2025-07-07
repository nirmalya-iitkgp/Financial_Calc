# mathematical_functions/queuing_mg1.py

import math

def _validate_mg1_inputs(lambda_rate: float, mu_rate: float):
    """
    Helper function to validate common M/G/1 queue inputs.
    """
    if not isinstance(lambda_rate, (int, float)) or lambda_rate <= 0:
        raise ValueError("Arrival rate (lambda_rate) must be a positive number.")
    if not isinstance(mu_rate, (int, float)) or mu_rate <= 0:
        raise ValueError("Service rate (mu_rate) must be a positive number.")
    if lambda_rate >= mu_rate:
        raise ValueError("System is unstable: Arrival rate (lambda_rate) must be less than service rate (mu_rate).")

def get_second_moment_service_time(
    mu_rate: float, 
    dist_type: str, 
    std_dev: float = None, 
    min_val: float = None, 
    max_val: float = None
) -> float:
    """
    Helper function to get the second moment of service time (E[S^2]) based on distribution type.
    
    Args:
        mu_rate (float): Average service rate (1 / E[S]).
        dist_type (str): Type of service time distribution ('exponential', 'deterministic', 'uniform').
                         For 'general', you'd provide E_S2 directly.
        std_dev (float, optional): Standard deviation of service time for distributions that use it (e.g., normal).
                                   Required for 'normal'.
        min_val (float, optional): Minimum value for 'uniform' distribution.
        max_val (float, optional): Maximum value for 'uniform' distribution.

    Returns:
        float: The second moment of the service time distribution (E[S^2]).

    Raises:
        ValueError: If unsupported distribution type or insufficient parameters.
    """
    if mu_rate <= 0:
        raise ValueError("Service rate (mu_rate) must be positive.")

    E_S = 1 / mu_rate # Expected service time

    if dist_type.lower() == 'exponential':
        # For exponential distribution, Var(S) = (1/mu)^2, so E[S^2] = Var(S) + E[S]^2
        return (1 / mu_rate)**2 + E_S**2
    elif dist_type.lower() == 'deterministic': # M/D/1 case
        # For deterministic, Var(S) = 0, so E[S^2] = E[S]^2
        return E_S**2
    elif dist_type.lower() == 'uniform':
        if min_val is None or max_val is None:
            raise ValueError("For 'uniform' distribution, min_val and max_val must be provided.")
        if min_val >= max_val:
            raise ValueError("min_val must be less than max_val for uniform distribution.")
        # For uniform distribution U(a,b), E[S] = (a+b)/2, Var(S) = (b-a)^2/12
        # So, E[S^2] = Var(S) + E[S]^2
        a = min_val
        b = max_val
        return ((b - a)**2 / 12) + (((a + b) / 2)**2)
    # Add other distributions as needed (e.g., normal, gamma)
    else:
        raise ValueError(f"Unsupported or incomplete service time distribution type: '{dist_type}'. "
                         "Provide E_S2 directly for general distributions.")


def calculate_mg1_utilization(lambda_rate: float, mu_rate: float) -> float:
    """
    Calculates the server utilization (rho) for an M/G/1 queue.

    Args:
        lambda_rate (float): Average arrival rate (customers per unit time). Must be positive.
        mu_rate (float): Average service rate (customers per unit time). Must be positive.

    Returns:
        float: The server utilization (rho).

    Raises:
        ValueError: If lambda_rate or mu_rate are invalid, or if the system is unstable.
    """
    _validate_mg1_inputs(lambda_rate, mu_rate)
    return lambda_rate / mu_rate

def calculate_mg1_avg_queue_length(lambda_rate: float, mu_rate: float, E_S2: float) -> float:
    """
    Calculates the average number of customers waiting in the queue for an M/G/1 system
    using the Pollaczek-Khinchine formula.

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate.
        E_S2 (float): The second moment of the service time distribution (E[S^2]).

    Returns:
        float: Average number of customers in the queue (Lq).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mg1_inputs(lambda_rate, mu_rate)
    if not isinstance(E_S2, (int, float)) or E_S2 <= 0:
        raise ValueError("Second moment of service time (E_S2) must be a positive number.")

    rho = calculate_mg1_utilization(lambda_rate, mu_rate)
    
    # Pollaczek-Khinchine formula
    numerator = (lambda_rate**2) * E_S2
    denominator = 2 * (1 - rho)
    
    if denominator == 0:
        raise ZeroDivisionError("Denominator in Pollaczek-Khinchine formula is zero (system might be unstable or rho is 1).")
        
    return numerator / denominator

def calculate_mg1_avg_system_length(lambda_rate: float, mu_rate: float, E_S2: float) -> float:
    """
    Calculates the average number of customers in the M/G/1 system (waiting + being served).

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate.
        E_S2 (float): The second moment of the service time distribution (E[S^2]).

    Returns:
        float: Average number of customers in the system (L).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mg1_inputs(lambda_rate, mu_rate)
    lq = calculate_mg1_avg_queue_length(lambda_rate, mu_rate, E_S2)
    return lq + (lambda_rate / mu_rate) # L = Lq + rho (or Lq + lambda * E[S])

def calculate_mg1_avg_waiting_time_queue(lambda_rate: float, mu_rate: float, E_S2: float) -> float:
    """
    Calculates the average time a customer spends waiting in the queue for an M/G/1 system.

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate.
        E_S2 (float): The second moment of the service time distribution (E[S^2]).

    Returns:
        float: Average time waiting in the queue (Wq).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mg1_inputs(lambda_rate, mu_rate)
    lq = calculate_mg1_avg_queue_length(lambda_rate, mu_rate, E_S2)
    return lq / lambda_rate # Little's Law: Wq = Lq / lambda

def calculate_mg1_avg_waiting_time_system(lambda_rate: float, mu_rate: float, E_S2: float) -> float:
    """
    Calculates the average time a customer spends in the M/G/1 system (waiting + being served).

    Args:
        lambda_rate (float): Average arrival rate.
        mu_rate (float): Average service rate.
        E_S2 (float): The second moment of the service time distribution (E[S^2]).

    Returns:
        float: Average time in the system (W).

    Raises:
        ValueError: If inputs are invalid or the system is unstable.
    """
    _validate_mg1_inputs(lambda_rate, mu_rate)
    wq = calculate_mg1_avg_waiting_time_queue(lambda_rate, mu_rate, E_S2)
    return wq + (1 / mu_rate) # W = Wq + E[S]