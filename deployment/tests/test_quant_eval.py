"""
Unit Tests for Quantitative Evaluation Functions

Tests individual functions in isolation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant_eval import (
    parse_goal,
    download_yahoo_data,
    compute_covariance,
    validate_tickers_with_patterns
)


def test_parse_goal_basic():
    """Test basic goal parsing"""

    goal = "I have $10,000 and want to save $100,000 in 20 years"
    params = parse_goal(goal)

    assert params['starting_wealth'] == 10000, f"Expected 10000, got {params['starting_wealth']}"
    assert params['target_wealth'] == 100000, f"Expected 100000, got {params['target_wealth']}"
    assert params['timeline_years'] == 20, f"Expected 20, got {params['timeline_years']}"

    print(f"✓ Basic goal parsing works: {params}")


def test_parse_goal_with_contributions():
    """Test goal parsing with monthly contributions"""

    goal = "Starting with $5,000, I want to reach $50,000 in 10 years by investing $200/month"
    params = parse_goal(goal)

    assert params['starting_wealth'] == 5000
    assert params['target_wealth'] == 50000
    assert params['timeline_years'] == 10
    assert params['monthly_contribution'] == 200

    print(f"✓ Goal parsing with contributions: {params}")


def test_parse_goal_thousands_notation():
    """Test parsing with 'k' notation"""

    goal = "I have $50k and want to save $200k in 15 years"
    params = parse_goal(goal)

    assert params['starting_wealth'] == 50000
    assert params['target_wealth'] == 200000
    assert params['timeline_years'] == 15

    print(f"✓ Thousands notation parsing: {params}")


def test_download_yahoo_data():
    """Test Yahoo Finance data download"""

    tickers = ["VTI", "BND"]
    returns = download_yahoo_data(tickers, years=2)

    assert len(returns.columns) == 2
    assert "VTI" in returns.columns
    assert "BND" in returns.columns
    assert len(returns) > 0  # Should have data

    print(f"✓ Downloaded {len(returns)} months of data for {tickers}")


def test_leveraged_etf_detection():
    """Test pattern matching for leveraged ETFs"""

    # Should detect leveraged
    concerns = validate_tickers_with_patterns(["TQQQ", "VTI", "SQQQ"])
    assert len(concerns) == 2, f"Expected 2 concerns, got {len(concerns)}"
    assert any("TQQQ" in c for c in concerns)
    assert any("SQQQ" in c for c in concerns)

    # Should not flag normal tickers
    concerns = validate_tickers_with_patterns(["VTI", "BND", "VNQ"])
    assert len(concerns) == 0, f"Expected no concerns, got {concerns}"

    print(f"✓ Leveraged ETF detection works")


def test_covariance_computation():
    """Test covariance matrix computation"""

    import pandas as pd
    import numpy as np

    # Create sample returns
    np.random.seed(42)
    returns = pd.DataFrame({
        'A': np.random.normal(0.01, 0.05, 100),
        'B': np.random.normal(0.01, 0.05, 100)
    })

    cov = compute_covariance(returns)

    assert cov.shape == (2, 2)
    assert cov[0, 0] > 0  # Variance should be positive
    assert cov[1, 1] > 0
    # Covariance matrix should be symmetric
    assert abs(cov[0, 1] - cov[1, 0]) < 1e-10

    print(f"✓ Covariance computation works")


if __name__ == "__main__":
    print("Running unit tests...")
    print()

    test_parse_goal_basic()
    test_parse_goal_with_contributions()
    test_parse_goal_thousands_notation()
    test_download_yahoo_data()
    test_leveraged_etf_detection()
    test_covariance_computation()

    print()
    print("=" * 60)
    print("✓ ALL UNIT TESTS PASSED")
    print("=" * 60)
