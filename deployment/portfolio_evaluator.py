#!/usr/bin/env python3
"""
Portfolio Evaluator Agent (Green Agent)
Quantitative portfolio evaluation using Monte Carlo simulation.
"""

import argparse
import json
import logging
import os
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

from google import genai
from google.adk import Agent
from google.adk.tools import FunctionTool, google_search, AgentTool
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import TaskState, Part, TextPart
from a2a.utils import new_agent_text_message
from a2a.client import A2AClient

# Import from local copy
from agentbeats.green_executor import GreenAgent, GreenExecutor
from agentbeats.models import EvalRequest, EvalResult
from agentbeats.tool_provider import ToolProvider

# Import quantitative evaluation functions
from quant_eval import (
    parse_goal,
    download_yahoo_data,
    run_simulation,
    compute_scores,
    get_cached_ticker_info,
    cache_ticker_info,
    validate_tickers_with_patterns
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("portfolio_evaluator")


# === ADK SEARCHAGENT SETUP ===

# Create dedicated search agent for ticker validation
search_agent = Agent(
    name="ticker_search_agent",
    model="gemini-2.0-flash",
    tools=[google_search],
    instruction="""You are a financial ticker research assistant.
When asked about a ticker, search for information about whether it is:
- A leveraged ETF (2x, 3x, etc.)
- An inverse ETF (short, bear, etc.)
- An Exchange Traded Note (ETN)
- A delisted or renamed ticker

Provide a clear yes/no answer with brief explanation."""
)

# Wrap search agent as a tool
search_tool = AgentTool(search_agent)


class PortfolioEvaluation(BaseModel):
    """Evaluation result for a portfolio"""
    probability_of_success: float  # 0-100
    diversification_score: float  # 0-100
    risk_score: float  # 0-100
    return_score: float  # 0-100
    reasoning: str
    concerns: list[str]
    overall_assessment: str


def validate_portfolio(portfolio: dict) -> tuple[bool, str]:
    """Validate portfolio structure and constraints"""

    # Check for parse errors
    if "error" in portfolio:
        return False, f"Portfolio parsing error: {portfolio.get('error', 'unknown')}"

    # Check required fields
    if "tickers" not in portfolio:
        return False, "Missing 'tickers' field"

    if not isinstance(portfolio["tickers"], list):
        return False, "'tickers' must be a list"

    # Check ticker count
    if len(portfolio["tickers"]) < 1:
        return False, "Must have at least 1 ticker"
    if len(portfolio["tickers"]) > 10:
        return False, "Too many tickers (max 10 for reasonable evaluation)"

    # Check allocations sum to 100
    try:
        total_allocation = sum(
            float(t.get("allocation_percent", 0))
            for t in portfolio["tickers"]
        )
        if abs(total_allocation - 100) > 1.0:  # Allow 1% tolerance for rounding
            return False, f"Allocations sum to {total_allocation:.1f}%, not 100%"
    except (ValueError, TypeError) as e:
        return False, f"Invalid allocation values: {e}"

    # Check ticker format
    for i, ticker in enumerate(portfolio["tickers"]):
        if not isinstance(ticker, dict):
            return False, f"Ticker {i} must be a dictionary"
        if "symbol" not in ticker:
            return False, f"Ticker {i} missing 'symbol' field"
        if "allocation_percent" not in ticker:
            return False, f"Ticker {i} missing 'allocation_percent' field"

    return True, "Valid"


class PortfolioEvaluator(GreenAgent):
    def __init__(self):
        self._required_roles = ["portfolio_constructor"]
        self._required_config_keys = ["goal_description"]
        self._client = genai.Client()
        self._tool_provider = ToolProvider()

    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        missing_roles = set(self._required_roles) - set(request.participants.keys())
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"
        missing_config_keys = set(self._required_config_keys) - set(request.config.keys())
        if missing_config_keys:
            return False, f"Missing config keys: {missing_config_keys}"
        return True, "ok"

    async def run_eval(self, req: EvalRequest, updater: TaskUpdater) -> None:
        logger.info(f"Starting portfolio evaluation: {req}")

        try:
            # Get goal description
            goal = req.config["goal_description"]

            # Request portfolio from constructor
            await updater.update_status(
                TaskState.working,
                new_agent_text_message("Requesting portfolio recommendation...")
            )

            portfolio_json = await self._tool_provider.talk_to_agent(
                goal,
                str(req.participants["portfolio_constructor"]),
                new_conversation=True
            )

            logger.info(f"Received portfolio: {portfolio_json}")
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(f"Portfolio received: {portfolio_json}")
            )

            # Parse portfolio
            try:
                portfolio = json.loads(portfolio_json)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', portfolio_json, re.DOTALL)
                if json_match:
                    portfolio = json.loads(json_match.group(1))
                else:
                    # Last resort: look for JSON object
                    json_match = re.search(r'\{.*\}', portfolio_json, re.DOTALL)
                    if json_match:
                        portfolio = json.loads(json_match.group(0))
                    else:
                        portfolio = {"error": "Could not parse portfolio", "raw": portfolio_json}

            # Validate portfolio
            valid, validation_message = validate_portfolio(portfolio)
            if not valid:
                logger.warning(f"Portfolio validation warning: {validation_message}")
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(f"Portfolio validation issue: {validation_message}. Continuing with evaluation...")
                )
                # Continue anyway, let LLM judge the quality

            # Evaluate portfolio
            await updater.update_status(
                TaskState.working,
                new_agent_text_message("Evaluating portfolio recommendation...")
            )

            evaluation = await self.evaluate_portfolio(goal, portfolio, req.config)
            logger.info(f"Evaluation: {evaluation.model_dump_json()}")

            # Create result with flattened structure for leaderboard
            result = EvalResult(
                winner=f"probability_{int(evaluation.probability_of_success)}",
                detail={
                    "probability_of_success": evaluation.probability_of_success,
                    "diversification_score": evaluation.diversification_score,
                    "risk_score": evaluation.risk_score,
                    "return_score": evaluation.return_score
                }
            )

            # Add artifacts with simplified structure for leaderboard
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=json.dumps({
                        "probability_of_success": evaluation.probability_of_success,
                        "diversification_score": evaluation.diversification_score,
                        "risk_score": evaluation.risk_score,
                        "return_score": evaluation.return_score
                    }, indent=2)))
                ],
                name="PortfolioEvaluation",
            )

        finally:
            self._tool_provider.reset()

    async def evaluate_portfolio(
        self,
        goal: str,
        portfolio: dict,
        config: dict = None
    ) -> PortfolioEvaluation:
        """Evaluate a portfolio recommendation using quantitative Monte Carlo simulation"""

        try:
            # Parse goal parameters from natural language
            goal_params = parse_goal(goal)

            # Override with structured config if available
            if config:
                goal_params['starting_wealth'] = config.get('starting_amount', goal_params['starting_wealth'])
                goal_params['target_wealth'] = config.get('target_amount', goal_params['target_wealth'])
                goal_params['timeline_years'] = config.get('timeline_years', goal_params['timeline_years'])
                goal_params['monthly_contribution'] = config.get('monthly_contribution', goal_params['monthly_contribution'])

            logger.info(f"Parsed goal: {goal_params}")

            # Validate ticker information with caching
            concerns = []
            tickers = [t['symbol'] for t in portfolio['tickers']]

            # First try pattern matching (fast)
            pattern_concerns = validate_tickers_with_patterns(tickers)
            concerns.extend(pattern_concerns)

            # Then use web search for thorough validation (with caching)
            for ticker in tickers:
                # Check cache first
                cached_info = get_cached_ticker_info(ticker)

                if cached_info is None:
                    try:
                        # Query search agent directly
                        search_query = (
                            f"Is {ticker} a leveraged ETF, inverse ETF, or ETN? "
                            f"Is it delisted or renamed? Provide clear yes/no answers."
                        )
                        response = search_agent.run(search_query)
                        search_result = str(response.output)
                        cached_info = cache_ticker_info(ticker, search_result)
                        logger.info(f"Cached ticker info for {ticker}: {cached_info}")
                    except Exception as e:
                        logger.warning(f"Search failed for {ticker}: {e}")
                        # Continue without web search validation
                        continue

                # Add concerns if ticker is risky
                if cached_info and cached_info['is_risky']:
                    if cached_info['warning_message'] not in concerns:
                        concerns.append(cached_info['warning_message'])

            # Download historical data
            logger.info(f"Downloading data for tickers: {tickers}")
            historical_returns = download_yahoo_data(tickers, years=5)

            # Run simulation
            logger.info("Running Monte Carlo simulation...")
            simulation_results = run_simulation(goal_params, portfolio, historical_returns)

            # Compute scores with financial sanity checks
            scores = compute_scores(
                simulation_results,
                portfolio,
                goal_params,
                historical_returns,
                concerns
            )

            return PortfolioEvaluation(
                probability_of_success=scores['probability_of_success'],
                diversification_score=scores['diversification_score'],
                risk_score=scores['risk_score'],
                return_score=scores['return_score'],
                reasoning=scores['reasoning'],
                concerns=scores['concerns'],
                overall_assessment=f"{scores['probability_of_success']:.1f}% probability of success"
            )

        except Exception as e:
            logger.error(f"Evaluation error: {e}", exc_info=True)
            # Fallback: return reasonable defaults
            return PortfolioEvaluation(
                probability_of_success=50.0,
                diversification_score=50.0,
                risk_score=50.0,
                return_score=50.0,
                reasoning=f"Evaluation error: {str(e)}",
                concerns=["Unable to complete full quantitative evaluation"],
                overall_assessment="Evaluation incomplete due to error"
            )


def create_portfolio_evaluator_agent_card(url: str):
    from a2a.types import AgentCard, AgentCapabilities
    return AgentCard(
        name="portfolio_evaluator",
        description="Evaluates portfolio recommendations for achieving financial goals",
        url=url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[],
    )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9009)
    parser.add_argument("--card-url", type=str, help="External URL for agent card")
    args = parser.parse_args()

    # Create executor and app
    executor = GreenExecutor(PortfolioEvaluator())
    task_store = InMemoryTaskStore()
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=task_store,
    )

    server = A2AStarletteApplication(
        agent_card=create_portfolio_evaluator_agent_card(
            url=args.card_url or f'http://{args.host}:{args.port}/'
        ),
        http_handler=request_handler,
    )

    # Run server
    uvicorn_config = uvicorn.Config(server.build(), host=args.host, port=args.port)
    uvicorn_server = uvicorn.Server(uvicorn_config)
    await uvicorn_server.serve()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
