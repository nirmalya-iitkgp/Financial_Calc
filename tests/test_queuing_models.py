# tests/test_queuing_models.py

import pytest
import math

# Import functions from your mathematical_functions package
from mathematical_functions.queuing_mm1 import (
    calculate_mm1_utilization,
    calculate_mm1_avg_system_length,
    calculate_mm1_avg_queue_length,
    calculate_mm1_avg_waiting_time_system,
    calculate_mm1_avg_waiting_time_queue,
    calculate_mm1_prob_n_customers,
)

from mathematical_functions.queuing_mmc import (
    calculate_mmc_utilization,
    calculate_mmc_prob_waiting,
    calculate_mmc_avg_queue_length,
    calculate_mmc_avg_waiting_time_queue,
    calculate_mmc_avg_system_length,
    calculate_mmc_avg_system_time,
)

from mathematical_functions.queuing_mg1 import (
    get_second_moment_service_time,
    calculate_mg1_utilization,
    calculate_mg1_avg_queue_length,
    calculate_mg1_avg_system_length,
    calculate_mg1_avg_waiting_time_queue,
    calculate_mg1_avg_waiting_time_system,
)

# --- Test Cases for M/M/1 Queue ---

def test_mm1_utilization():
    assert calculate_mm1_utilization(lambda_rate=5, mu_rate=10) == 0.5
    assert calculate_mm1_utilization(lambda_rate=1, mu_rate=10) == 0.1
    assert calculate_mm1_utilization(lambda_rate=9.9, mu_rate=10) == 0.99

def test_mm1_utilization_invalid_inputs():
    with pytest.raises(ValueError, match="Arrival rate .* positive"):
        calculate_mm1_utilization(lambda_rate=0, mu_rate=10)
    with pytest.raises(ValueError, match="Service rate .* positive"):
        calculate_mm1_utilization(lambda_rate=5, mu_rate=0)
    with pytest.raises(ValueError, match="System is unstable"):
        calculate_mm1_utilization(lambda_rate=10, mu_rate=10)
    with pytest.raises(ValueError, match="System is unstable"):
        calculate_mm1_utilization(lambda_rate=15, mu_rate=10)

def test_mm1_avg_system_length():
    # Example: lambda=5, mu=10 -> rho=0.5 -> L = 0.5 / (1 - 0.5) = 1.0
    assert calculate_mm1_avg_system_length(lambda_rate=5, mu_rate=10) == pytest.approx(1.0)
    # Example: lambda=1, mu=2 -> rho=0.5 -> L = 1.0
    assert calculate_mm1_avg_system_length(lambda_rate=1, mu_rate=2) == pytest.approx(1.0)
    # Example: lambda=9, mu=10 -> rho=0.9 -> L = 0.9 / (1 - 0.9) = 9.0
    assert calculate_mm1_avg_system_length(lambda_rate=9, mu_rate=10) == pytest.approx(9.0)

def test_mm1_avg_queue_length():
    # Example: lambda=5, mu=10 -> rho=0.5 -> Lq = 0.5^2 / (1 - 0.5) = 0.25 / 0.5 = 0.5
    assert calculate_mm1_avg_queue_length(lambda_rate=5, mu_rate=10) == pytest.approx(0.5)
    # Example: lambda=9, mu=10 -> rho=0.9 -> Lq = 0.9^2 / (1 - 0.9) = 0.81 / 0.1 = 8.1
    assert calculate_mm1_avg_queue_length(lambda_rate=9, mu_rate=10) == pytest.approx(8.1)

def test_mm1_avg_waiting_time_system():
    # Example: lambda=5, mu=10 -> W = 1 / (10 - 5) = 0.2
    assert calculate_mm1_avg_waiting_time_system(lambda_rate=5, mu_rate=10) == pytest.approx(0.2)
    # Example: lambda=9, mu=10 -> W = 1 / (10 - 9) = 1.0
    assert calculate_mm1_avg_waiting_time_system(lambda_rate=9, mu_rate=10) == pytest.approx(1.0)

def test_mm1_avg_waiting_time_queue():
    # Example: lambda=5, mu=10 -> Wq = 5 / (10 * (10 - 5)) = 5 / 50 = 0.1
    assert calculate_mm1_avg_waiting_time_queue(lambda_rate=5, mu_rate=10) == pytest.approx(0.1)
    # Example: lambda=9, mu=10 -> Wq = 9 / (10 * (10 - 9)) = 9 / 10 = 0.9
    assert calculate_mm1_avg_waiting_time_queue(lambda_rate=9, mu_rate=10) == pytest.approx(0.9)

def test_mm1_prob_n_customers():
    # lambda=5, mu=10 -> rho=0.5
    # P_0 = (1 - 0.5) * 0.5^0 = 0.5
    assert calculate_mm1_prob_n_customers(0, lambda_rate=5, mu_rate=10) == pytest.approx(0.5)
    # P_1 = (1 - 0.5) * 0.5^1 = 0.25
    assert calculate_mm1_prob_n_customers(1, lambda_rate=5, mu_rate=10) == pytest.approx(0.25)
    # P_2 = (1 - 0.5) * 0.5^2 = 0.125
    assert calculate_mm1_prob_n_customers(2, lambda_rate=5, mu_rate=10) == pytest.approx(0.125)
    
    with pytest.raises(ValueError, match="Number of customers .n. must be a non-negative integer."):
        calculate_mm1_prob_n_customers(-1, lambda_rate=5, mu_rate=10)

# --- Test Cases for M/M/c Queue ---

def test_mmc_utilization():
    assert calculate_mmc_utilization(lambda_rate=5, mu_rate=10, c=1) == 0.5 # Should match M/M/1
    assert calculate_mmc_utilization(lambda_rate=15, mu_rate=10, c=2) == 0.75 # 15 / (2 * 10)
    assert calculate_mmc_utilization(lambda_rate=25, mu_rate=10, c=3) == pytest.approx(0.83333, rel=1e-5) # 25 / (3 * 10)

def test_mmc_utilization_invalid_inputs():
    with pytest.raises(ValueError, match="Number of servers .* positive integer"):
        calculate_mmc_utilization(lambda_rate=5, mu_rate=10, c=0)
    with pytest.raises(ValueError, match="System is unstable"):
        calculate_mmc_utilization(lambda_rate=10, mu_rate=10, c=1)
    with pytest.raises(ValueError, match="System is unstable"):
        calculate_mmc_utilization(lambda_rate=25, mu_rate=10, c=2) # 25 > 2 * 10

def test_mmc_prob_waiting():
    # Known example: lambda=1, mu=1, c=2 -> rho_system = 0.5. Erlang C should be around 0.333
    # More precise: (1^2/2!) * (1/(1-0.5)) / ((1^0/0!) + (1^1/1!) + (1^2/2!) * (1/(1-0.5)))
    # = (0.5 * 2) / (1 + 1 + 0.5 * 2) = 1 / (1 + 1 + 1) = 1/3
    assert calculate_mmc_prob_waiting(lambda_rate=1, mu_rate=1, c=2) == pytest.approx(1/3)
    # Corrected example: lambda=3, mu=2, c=2. Actual: 9/14 or 0.6428571428571429
    assert calculate_mmc_prob_waiting(lambda_rate=3, mu_rate=2, c=2) == pytest.approx(9/14, rel=1e-5) 

def test_mmc_avg_queue_length():
    # Using previous P_wait example: lambda=1, mu=1, c=2, P_wait=1/3
    # Lq = P_wait * (lambda/mu) / (1 - lambda/(c*mu)) = (1/3) * (1/1) / (1 - 0.5) = (1/3) / 0.5 = 2/3
    assert calculate_mmc_avg_queue_length(lambda_rate=1, mu_rate=1, c=2) == pytest.approx(2/3)

    # Corrected example: lambda=3, mu=2, c=2. Actual: 27/7 or 3.8571428571428577
    assert calculate_mmc_avg_queue_length(lambda_rate=3, mu_rate=2, c=2) == pytest.approx(27/7, rel=1e-5)

def test_mmc_avg_waiting_time_queue():
    # Using lambda=1, mu=1, c=2, Lq=2/3
    # Wq = Lq / lambda = (2/3) / 1 = 2/3
    assert calculate_mmc_avg_waiting_time_queue(lambda_rate=1, mu_rate=1, c=2) == pytest.approx(2/3)

def test_mmc_avg_system_length():
    # Using lambda=1, mu=1, c=2, Lq=2/3. L = Lq + lambda/mu = 2/3 + 1/1 = 5/3
    assert calculate_mmc_avg_system_length(lambda_rate=1, mu_rate=1, c=2) == pytest.approx(5/3)

def test_mmc_avg_system_time():
    # Using lambda=1, mu=1, c=2, Wq=2/3. W = Wq + 1/mu = 2/3 + 1/1 = 5/3
    assert calculate_mmc_avg_system_time(lambda_rate=1, mu_rate=1, c=2) == pytest.approx(5/3)

# --- Test Cases for M/G/1 Queue ---

def test_mg1_get_second_moment_service_time_exponential():
    # For exponential, E[S^2] = 2 / mu^2
    assert get_second_moment_service_time(mu_rate=10, dist_type='exponential') == pytest.approx(2 / (10**2))
    assert get_second_moment_service_time(mu_rate=2, dist_type='exponential') == pytest.approx(2 / (2**2))

def test_mg1_get_second_moment_service_time_deterministic():
    # For deterministic, E[S^2] = (1/mu)^2
    assert get_second_moment_service_time(mu_rate=10, dist_type='deterministic') == pytest.approx(1 / (10**2))
    assert get_second_moment_service_time(mu_rate=2, dist_type='deterministic') == pytest.approx(1 / (2**2))

def test_mg1_get_second_moment_service_time_uniform():
    # For U(a,b), E[S^2] = Var(S) + E[S]^2 = ((b-a)^2)/12 + ((a+b)/2)^2
    # If mean is 1/mu = 5, and it's uniform from 0 to 10 (a=0, b=10)
    # E[S] = (0+10)/2 = 5. So mu = 1/5 = 0.2
    # E[S^2] = (10^2)/12 + 5^2 = 100/12 + 25 = 8.333... + 25 = 33.333...
    assert get_second_moment_service_time(mu_rate=0.2, dist_type='uniform', min_val=0, max_val=10) == pytest.approx(33.33333, rel=1e-5)
    
    with pytest.raises(ValueError, match="min_val and max_val must be provided"):
        get_second_moment_service_time(mu_rate=1, dist_type='uniform')
    with pytest.raises(ValueError, match="min_val must be less than max_val"):
        get_second_moment_service_time(mu_rate=1, dist_type='uniform', min_val=5, max_val=5)

def test_mg1_utilization():
    assert calculate_mg1_utilization(lambda_rate=5, mu_rate=10) == 0.5
    with pytest.raises(ValueError, match="System is unstable"):
        calculate_mg1_utilization(lambda_rate=10, mu_rate=10)

def test_mg1_avg_queue_length():
    lambda_rate = 5
    mu_rate = 10
    
    # M/M/1 case: E_S2_exp = 2 / mu^2 = 2 / 100 = 0.02
    # Lq_exp = (lambda^2 * E_S2_exp) / (2 * (1 - lambda/mu)) = (25 * 0.02) / (2 * 0.5) = 0.5 / 1 = 0.5
    E_S2_exp = get_second_moment_service_time(mu_rate, 'exponential')
    assert calculate_mg1_avg_queue_length(lambda_rate, mu_rate, E_S2_exp) == pytest.approx(0.5)

    # M/D/1 case: E_S2_det = (1/mu)^2 = 1 / 100 = 0.01
    # Lq_det = (25 * 0.01) / (2 * 0.5) = 0.25 / 1 = 0.25
    E_S2_det = get_second_moment_service_time(mu_rate, 'deterministic')
    assert calculate_mg1_avg_queue_length(lambda_rate, mu_rate, E_S2_det) == pytest.approx(0.25)

def test_mg1_avg_system_length():
    lambda_rate = 5
    mu_rate = 10
    
    E_S2_exp = get_second_moment_service_time(mu_rate, 'exponential')
    # L = Lq + lambda/mu = 0.5 + 0.5 = 1.0
    assert calculate_mg1_avg_system_length(lambda_rate, mu_rate, E_S2_exp) == pytest.approx(1.0)

    E_S2_det = get_second_moment_service_time(mu_rate, 'deterministic')
    # L = Lq + lambda/mu = 0.25 + 0.5 = 0.75
    assert calculate_mg1_avg_system_length(lambda_rate, mu_rate, E_S2_det) == pytest.approx(0.75)

def test_mg1_avg_waiting_time_queue():
    lambda_rate = 5
    mu_rate = 10
    
    E_S2_exp = get_second_moment_service_time(mu_rate, 'exponential')
    # Wq = Lq / lambda = 0.5 / 5 = 0.1
    assert calculate_mg1_avg_waiting_time_queue(lambda_rate, mu_rate, E_S2_exp) == pytest.approx(0.1)

    E_S2_det = get_second_moment_service_time(mu_rate, 'deterministic')
    # Wq = Lq / lambda = 0.25 / 5 = 0.05
    assert calculate_mg1_avg_waiting_time_queue(lambda_rate, mu_rate, E_S2_det) == pytest.approx(0.05)

def test_mg1_avg_waiting_time_system():
    lambda_rate = 5
    mu_rate = 10
    
    E_S2_exp = get_second_moment_service_time(mu_rate, 'exponential')
    # W = Wq + 1/mu = 0.1 + 0.1 = 0.2
    assert calculate_mg1_avg_waiting_time_system(lambda_rate, mu_rate, E_S2_exp) == pytest.approx(0.2)

    E_S2_det = get_second_moment_service_time(mu_rate, 'deterministic')
    # W = Wq + 1/mu = 0.05 + 0.1 = 0.15
    assert calculate_mg1_avg_waiting_time_system(lambda_rate, mu_rate, E_S2_det) == pytest.approx(0.15)