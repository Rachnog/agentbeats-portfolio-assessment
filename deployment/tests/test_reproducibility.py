"""
Reproducibility Tests - CRITICAL

Tests that same input produces identical output every time.
Zero tolerance for randomness.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant_eval import (
    parse_goal,
    download_yahoo_data,
    run_simulation,
    compute_scores
)


def test_reproducibility_simple_portfolio():
    """
    Run same evaluation 5 times, verify identical results.
    This is the most critical test.
    """

    # Goal parameters
    goal_text = "I have $10,000 and want to save $100,000 in 20 years, investing $200/month"
    goal_params = parse_goal(goal_text)

    # Portfolio
    portfolio = {
        "tickers": [
            {"symbol": "VTI", "allocation_percent": 60},
            {"symbol": "BND", "allocation_percent": 40}
        ]
    }

    # Download data once (to avoid network variability)
    tickers = [t['symbol'] for t in portfolio['tickers']]
    historical_returns = download_yahoo_data(tickers, years=5)

    # Run simulation 5 times
    results = []
    for i in range(5):
        sim_result = run_simulation(goal_params, portfolio, historical_returns)
        results.append(sim_result)

    # Verify all results are identical
    for i in range(1, 5):
        assert results[i]['probability_of_success'] == results[0]['probability_of_success'], \
            f"Run {i} probability differs: {results[i]['probability_of_success']} vs {results[0]['probability_of_success']}"

        assert results[i]['median_wealth'] == results[0]['median_wealth'], \
            f"Run {i} median wealth differs: {results[i]['median_wealth']} vs {results[0]['median_wealth']}"

        assert results[i]['p10_wealth'] == results[0]['p10_wealth'], \
            f"Run {i} p10 wealth differs"

        assert results[i]['p90_wealth'] == results[0]['p90_wealth'], \
            f"Run {i} p90 wealth differs"

    print(f"✓ Reproducibility test passed: {results[0]['probability_of_success']:.1f}% probability")


def test_reproducibility_with_different_portfolios():
    """
    Verify that different portfolios get different (but reproducible) results.
    """

    goal_text = "Save $50,000 in 10 years starting with $5,000"
    goal_params = parse_goal(goal_text)

    # Portfolio A: Conservative
    portfolio_a = {
        "tickers": [
            {"symbol": "BND", "allocation_percent": 100}
        ]
    }

    # Portfolio B: Aggressive
    portfolio_b = {
        "tickers": [
            {"symbol": "VTI", "allocation_percent": 100}
        ]
    }

    # Download data
    data_a = download_yahoo_data(["BND"], years=5)
    data_b = download_yahoo_data(["VTI"], years=5)

    # Run each portfolio 3 times
    results_a = [run_simulation(goal_params, portfolio_a, data_a) for _ in range(3)]
    results_b = [run_simulation(goal_params, portfolio_b, data_b) for _ in range(3)]

    # Verify reproducibility within each portfolio
    assert all(r['probability_of_success'] == results_a[0]['probability_of_success'] for r in results_a), \
        "Portfolio A not reproducible"
    assert all(r['probability_of_success'] == results_b[0]['probability_of_success'] for r in results_b), \
        "Portfolio B not reproducible"

    # Verify portfolios give different results
    assert results_a[0]['probability_of_success'] != results_b[0]['probability_of_success'], \
        "Different portfolios should give different results"

    print(f"✓ Portfolio A (bonds): {results_a[0]['probability_of_success']:.1f}%")
    print(f"✓ Portfolio B (stocks): {results_b[0]['probability_of_success']:.1f}%")


def test_deterministic_seed():
    """
    Verify that the seed generation is deterministic.
    """

    goal_text = "Retire in 30 years with $1,000,000"
    goal_params = parse_goal(goal_text)

    portfolio = {
        "tickers": [
            {"symbol": "VTI", "allocation_percent": 70},
            {"symbol": "BND", "allocation_percent": 30}
        ]
    }

    tickers = [t['symbol'] for t in portfolio['tickers']]
    data = download_yahoo_data(tickers, years=5)

    # Run multiple times
    probabilities = [
        run_simulation(goal_params, portfolio, data)['probability_of_success']
        for _ in range(10)
    ]

    # All should be identical
    assert len(set(probabilities)) == 1, f"Non-deterministic results: {set(probabilities)}"

    print(f"✓ Deterministic seed test passed: {probabilities[0]:.1f}% (consistent across 10 runs)")


if __name__ == "__main__":
    print("Running reproducibility tests...")
    print()

    print("Test 1: Simple portfolio reproducibility")
    test_reproducibility_simple_portfolio()
    print()

    print("Test 2: Different portfolios")
    test_reproducibility_with_different_portfolios()
    print()

    print("Test 3: Deterministic seed")
    test_deterministic_seed()
    print()

    print("=" * 60)
    print("✓ ALL REPRODUCIBILITY TESTS PASSED")
    print("=" * 60)
