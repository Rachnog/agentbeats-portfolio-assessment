"""
Quantitative Portfolio Evaluation Module

Implements deterministic Monte Carlo simulation with block bootstrap
for portfolio evaluation. Uses Yahoo Finance historical data and
enforces financial sanity checks.
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.covariance import LedoitWolf


# Configuration
CACHE_DIR = Path(__file__).parent / "ticker_cache"
CACHE_TTL_DAYS = 30
YEARS_OF_HISTORY = 5
NUM_SIMULATION_PATHS = 3000
BLOCK_SIZE = 6  # months for block bootstrap

# Financial bounds
STOCK_RETURN_BOUNDS = (0.04, 0.15)  # 4-15% annual
BOND_RETURN_BOUNDS = (0.02, 0.06)   # 2-6% annual
VOLATILITY_BOUNDS = (0.05, 0.25)     # 5-25% annual
EXTREME_VOL_THRESHOLD = 0.40          # Flag if exceeded

# Leveraged ETF patterns
LEVERAGED_PATTERNS = [
    'TQQQ', 'SQQQ', 'UPRO', 'SPXU', 'SPXL', 'TNA', 'TZA',
    'SOXL', 'SOXS', 'UDOW', 'SDOW', 'UMDD', 'SMDD',
    'URTY', 'SRTY', 'FAS', 'FAZ', 'CURE', 'RXD',
    'LABU', 'LABD', 'TECL', 'TECS', 'WANT', 'NEED'
]


def parse_goal(goal_text: str) -> dict:
    """
    Extract goal parameters from natural language text.

    Returns dict with:
    - starting_wealth (W0): Current wealth
    - target_wealth (W*): Goal wealth
    - timeline_years (T): Time horizon
    - monthly_contribution (C): Monthly contribution
    - goal_description: Original text
    """

    # Initialize defaults
    params = {
        'starting_wealth': 0,
        'target_wealth': 0,
        'timeline_years': 0,
        'monthly_contribution': 0,
        'goal_description': goal_text
    }

    text = goal_text.lower()

    # Extract starting wealth
    starting_patterns = [
        r'starting with \$?([\d,]+)k?',
        r'i have \$?([\d,]+)k?',
        r'current(?:ly)? \$?([\d,]+)k?',
        r'\$?([\d,]+)k? (?:to start|currently)',
    ]
    for pattern in starting_patterns:
        match = re.search(pattern, text)
        if match:
            value = match.group(1).replace(',', '')
            params['starting_wealth'] = float(value) * 1000 if 'k' in match.group(0) else float(value)
            break

    # Extract target wealth
    target_patterns = [
        r'(?:save|reach|achieve|need) \$?([\d,]+)k?',
        r'goal (?:of )?\$?([\d,]+)k?',
        r'\$?([\d,]+)k? (?:goal|target)',
    ]
    for pattern in target_patterns:
        match = re.search(pattern, text)
        if match:
            value = match.group(1).replace(',', '')
            params['target_wealth'] = float(value) * 1000 if 'k' in match.group(0) else float(value)
            break

    # Extract timeline
    timeline_patterns = [
        r'in (\d+) years?',
        r'over (\d+) years?',
        r'(\d+)[-\s]year',
    ]
    for pattern in timeline_patterns:
        match = re.search(pattern, text)
        if match:
            params['timeline_years'] = int(match.group(1))
            break

    # Extract monthly contribution
    contribution_patterns = [
        r'(?:add|contribute|invest|save) \$?([\d,]+)(?:/month| monthly| per month)',
        r'\$?([\d,]+)(?:/month| monthly| per month)',
    ]
    for pattern in contribution_patterns:
        match = re.search(pattern, text)
        if match:
            value = match.group(1).replace(',', '')
            params['monthly_contribution'] = float(value)
            break

    return params


def download_yahoo_data(tickers: list[str], years: int = YEARS_OF_HISTORY) -> pd.DataFrame:
    """
    Download historical adjusted close prices from Yahoo Finance.
    Returns DataFrame of monthly returns for each ticker.
    """

    # Download data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)

    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        progress=False,
        interval='1mo',
        auto_adjust=True  # Use adjusted prices directly
    )

    # Handle single ticker vs multiple tickers
    if len(tickers) == 1:
        # For single ticker, data is a simple DataFrame
        if isinstance(data['Close'], pd.Series):
            prices = data['Close'].to_frame()
            prices.columns = tickers
        else:
            # Already a DataFrame
            prices = data['Close']
            if prices.columns[0] != tickers[0]:
                prices.columns = tickers
    else:
        # For multiple tickers, Close is multi-level
        prices = data['Close']

    # Compute monthly returns
    returns = prices.pct_change().dropna()

    return returns


def compute_covariance(returns: pd.DataFrame) -> np.ndarray:
    """
    Compute covariance matrix using Ledoit-Wolf shrinkage estimator.
    Falls back to sample covariance if shrinkage fails.
    """

    try:
        lw = LedoitWolf()
        cov_matrix = lw.fit(returns).covariance_
        return cov_matrix
    except:
        # Fallback to sample covariance
        return returns.cov().values


def run_simulation(
    goal_params: dict,
    portfolio: dict,
    historical_returns: pd.DataFrame,
    num_paths: int = NUM_SIMULATION_PATHS
) -> dict:
    """
    Run block bootstrap Monte Carlo simulation.

    Returns dict with:
    - terminal_wealths: Array of final wealth values
    - probability_of_success: Percentage achieving goal
    - median_wealth: Median terminal wealth
    - percentiles: Various percentile values
    """

    # Extract parameters
    W0 = goal_params['starting_wealth']
    W_star = goal_params['target_wealth']
    T = goal_params['timeline_years']
    C = goal_params['monthly_contribution']

    # Get portfolio weights
    tickers = [t['symbol'] for t in portfolio['tickers']]
    weights = np.array([t['allocation_percent'] / 100 for t in portfolio['tickers']])

    # Ensure returns match tickers
    returns = historical_returns[tickers]
    n_months = len(returns)

    # Compute portfolio returns
    portfolio_returns = (returns * weights).sum(axis=1).values

    # Deterministic seed for reproducibility
    seed_str = f"{goal_params['goal_description']}{json.dumps(portfolio, sort_keys=True)}{num_paths}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed)

    # Run simulations
    terminal_wealths = []
    num_months = T * 12

    for _ in range(num_paths):
        wealth = W0

        # Block bootstrap sampling
        for month in range(num_months):
            # Sample a block starting point
            if n_months > BLOCK_SIZE:
                block_start = np.random.randint(0, n_months - BLOCK_SIZE + 1)
                block_idx = month % BLOCK_SIZE
                sampled_return = portfolio_returns[block_start + block_idx]
            else:
                # If not enough history, use standard bootstrap
                sampled_return = portfolio_returns[np.random.randint(0, n_months)]

            # Apply return and add contribution
            wealth = wealth * (1 + sampled_return) + C

        terminal_wealths.append(wealth)

    terminal_wealths = np.array(terminal_wealths)

    # Compute statistics
    probability = (terminal_wealths >= W_star).sum() / num_paths * 100

    return {
        'terminal_wealths': terminal_wealths,
        'probability_of_success': probability,
        'median_wealth': np.median(terminal_wealths),
        'p10_wealth': np.percentile(terminal_wealths, 10),
        'p25_wealth': np.percentile(terminal_wealths, 25),
        'p75_wealth': np.percentile(terminal_wealths, 75),
        'p90_wealth': np.percentile(terminal_wealths, 90),
    }


def compute_scores(
    simulation_results: dict,
    portfolio: dict,
    goal_params: dict,
    historical_returns: pd.DataFrame,
    concerns: list[str]
) -> dict:
    """
    Compute final scores with financial sanity checks.

    Returns dict with:
    - probability_of_success: 0-100
    - diversification_score: 0-100
    - risk_score: 0-100
    - return_score: 0-100
    - reasoning: Detailed explanation
    - concerns: List of concerns
    """

    # Get portfolio attributes
    tickers = [t['symbol'] for t in portfolio['tickers']]
    weights = np.array([t['allocation_percent'] / 100 for t in portfolio['tickers']])

    # Compute portfolio metrics
    returns = historical_returns[tickers]
    portfolio_returns = (returns * weights).sum(axis=1)

    annual_return = (1 + portfolio_returns.mean()) ** 12 - 1
    annual_vol = portfolio_returns.std() * np.sqrt(12)

    # === DIVERSIFICATION SCORE ===
    # Use Herfindahl index (inverse of effective N)
    effective_n = 1 / (weights ** 2).sum()
    max_effective_n = len(tickers)  # Perfect diversification
    diversification_score = min(100, (effective_n / max_effective_n) * 100)

    # Penalize concentration
    max_weight = weights.max()
    if max_weight > 0.6:
        diversification_score *= 0.7
        concerns.append(f"Concentrated portfolio: {max_weight*100:.0f}% in single ticker")

    # === RISK SCORE ===
    # Lower volatility = higher score
    # Map volatility to score: 5% vol = 100, 25% vol = 50, >40% vol = 0
    if annual_vol < VOLATILITY_BOUNDS[0]:
        risk_score = 100
    elif annual_vol < VOLATILITY_BOUNDS[1]:
        # Linear scale from 100 to 50
        risk_score = 100 - 50 * (annual_vol - VOLATILITY_BOUNDS[0]) / (VOLATILITY_BOUNDS[1] - VOLATILITY_BOUNDS[0])
    elif annual_vol < EXTREME_VOL_THRESHOLD:
        # Linear scale from 50 to 20
        risk_score = 50 - 30 * (annual_vol - VOLATILITY_BOUNDS[1]) / (EXTREME_VOL_THRESHOLD - VOLATILITY_BOUNDS[1])
    else:
        risk_score = 20
        concerns.append(f"Extreme volatility ({annual_vol*100:.1f}% annual) - very high risk")

    # === RETURN SCORE ===
    # Higher returns = higher score, but check realism
    # Map return to score: 4% = 40, 8% = 70, 12% = 100, 15% = 100
    if annual_return < STOCK_RETURN_BOUNDS[0]:
        return_score = max(20, annual_return / STOCK_RETURN_BOUNDS[0] * 40)
    elif annual_return < 0.08:
        return_score = 40 + 30 * (annual_return - STOCK_RETURN_BOUNDS[0]) / (0.08 - STOCK_RETURN_BOUNDS[0])
    elif annual_return < 0.12:
        return_score = 70 + 30 * (annual_return - 0.08) / (0.12 - 0.08)
    elif annual_return <= STOCK_RETURN_BOUNDS[1]:
        return_score = 100
    else:
        return_score = 100
        concerns.append(f"Unusually high historical returns ({annual_return*100:.1f}%) - may not persist")

    # === PROBABILITY OF SUCCESS ===
    probability = simulation_results['probability_of_success']

    # Clip extreme probabilities
    if probability < 0.5:
        probability = max(0.5, probability)
    elif probability > 99.5:
        probability = min(99.5, probability)

    # Flag impossible or trivial goals
    if probability < 5:
        concerns.append("Goal appears very difficult to achieve with this portfolio")
    elif probability > 95 and goal_params['starting_wealth'] >= goal_params['target_wealth']:
        concerns.append("Goal already achieved with starting wealth")

    # === FINANCIAL SANITY CHECKS ===

    # Check if returns are realistic
    if annual_return > STOCK_RETURN_BOUNDS[1]:
        concerns.append(f"Historical returns ({annual_return*100:.1f}%) exceed typical stock market returns")

    # Check volatility bounds
    if annual_vol > VOLATILITY_BOUNDS[1]:
        concerns.append(f"Volatility ({annual_vol*100:.1f}%) is higher than typical diversified portfolios")

    # Generate reasoning
    reasoning = (
        f"Portfolio Analysis:\n"
        f"- Expected annual return: {annual_return*100:.1f}%\n"
        f"- Annual volatility: {annual_vol*100:.1f}%\n"
        f"- Diversification: {len(tickers)} tickers, effective N = {effective_n:.1f}\n"
        f"- Probability of achieving ${goal_params['target_wealth']:,.0f} in {goal_params['timeline_years']} years: {probability:.1f}%\n"
        f"\n"
        f"The portfolio shows {_characterize_return(annual_return)} returns with "
        f"{_characterize_volatility(annual_vol)} risk. "
        f"Diversification is {_characterize_diversification(diversification_score)}."
    )

    return {
        'probability_of_success': round(probability, 1),
        'diversification_score': round(diversification_score, 1),
        'risk_score': round(risk_score, 1),
        'return_score': round(return_score, 1),
        'reasoning': reasoning,
        'concerns': concerns
    }


def _characterize_return(annual_return: float) -> str:
    """Characterize return level"""
    if annual_return < 0.04:
        return "very low"
    elif annual_return < 0.06:
        return "conservative"
    elif annual_return < 0.08:
        return "moderate"
    elif annual_return < 0.10:
        return "solid"
    elif annual_return < 0.12:
        return "strong"
    else:
        return "very high"


def _characterize_volatility(annual_vol: float) -> str:
    """Characterize volatility level"""
    if annual_vol < 0.08:
        return "very low"
    elif annual_vol < 0.12:
        return "low"
    elif annual_vol < 0.16:
        return "moderate"
    elif annual_vol < 0.20:
        return "elevated"
    elif annual_vol < 0.25:
        return "high"
    else:
        return "very high"


def _characterize_diversification(score: float) -> str:
    """Characterize diversification level"""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "adequate"
    else:
        return "poor"


# === TICKER VALIDATION WITH CACHING ===

def get_cached_ticker_info(ticker: str) -> Optional[dict]:
    """
    Get cached ticker validation info.
    Returns None if not cached or expired.
    """
    cache_file = CACHE_DIR / f"{ticker}.json"

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, 'r') as f:
            cached = json.load(f)

        # Check if expired
        cached_date = datetime.fromisoformat(cached['cached_at'])
        age = datetime.now() - cached_date

        if age > timedelta(days=CACHE_TTL_DAYS):
            return None  # Expired

        return cached

    except Exception:
        # Cache file corrupted, treat as not cached
        return None


def cache_ticker_info(ticker: str, search_result: str) -> dict:
    """
    Parse search result and save to cache.
    Returns parsed info dict.
    """
    CACHE_DIR.mkdir(exist_ok=True)

    # Parse search result (use keywords + patterns)
    result_lower = search_result.lower()

    is_leveraged = any(kw in result_lower for kw in [
        'leveraged', '3x', '2x', 'triple', 'double',
        'ultra', 'proshares ultra', 'direxion daily', '-3x', '-2x'
    ])

    is_inverse = any(kw in result_lower for kw in [
        'inverse', 'short', 'bear', 'inverse etf'
    ])

    is_etn = 'etn' in result_lower or 'exchange traded note' in result_lower

    is_delisted = any(kw in result_lower for kw in [
        'delisted', 'no longer trades', 'discontinued', 'merged'
    ])

    # Determine if risky
    is_risky = is_leveraged or is_inverse or is_etn or is_delisted

    # Generate warning message
    warning_parts = []
    if is_leveraged:
        warning_parts.append("leveraged ETF")
    if is_inverse:
        warning_parts.append("inverse ETF")
    if is_etn:
        warning_parts.append("ETN")
    if is_delisted:
        warning_parts.append("delisted/discontinued")

    warning_message = ""
    if warning_parts:
        warning_message = f"{ticker} is {'/'.join(warning_parts)} - extreme risk"

    # Create cache entry
    cache_entry = {
        'ticker': ticker,
        'is_leveraged': is_leveraged,
        'is_inverse': is_inverse,
        'is_etn': is_etn,
        'is_delisted': is_delisted,
        'is_risky': is_risky,
        'warning_message': warning_message,
        'search_result': search_result[:500],  # Truncate for storage
        'cached_at': datetime.now().isoformat()
    }

    # Save to cache file
    cache_file = CACHE_DIR / f"{ticker}.json"
    with open(cache_file, 'w') as f:
        json.dump(cache_entry, f, indent=2)

    return cache_entry


def validate_tickers_with_patterns(tickers: list[str]) -> list[str]:
    """
    Validate tickers using pattern matching (fallback method).
    Returns list of concerns.
    """
    concerns = []

    for ticker in tickers:
        if ticker.upper() in LEVERAGED_PATTERNS:
            concerns.append(f"{ticker} is a leveraged/inverse ETF - extreme risk")

    return concerns
