#!/usr/bin/env python3
"""
Portfolio Evaluator Agent (Green Agent)
Orchestrates portfolio construction and evaluates recommendations.
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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("portfolio_evaluator")


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

            evaluation = await self.evaluate_portfolio(goal, portfolio)
            logger.info(f"Evaluation: {evaluation.model_dump_json()}")

            # Create result
            result = EvalResult(
                winner=f"probability_{int(evaluation.probability_of_success)}",
                detail=evaluation.model_dump()
            )

            # Add artifacts
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=json.dumps({
                        "goal": goal,
                        "portfolio": portfolio,
                        "evaluation": evaluation.model_dump()
                    }, indent=2)))
                ],
                name="PortfolioEvaluation",
            )

        finally:
            self._tool_provider.reset()

    async def evaluate_portfolio(
        self,
        goal: str,
        portfolio: dict
    ) -> PortfolioEvaluation:
        """Evaluate a portfolio recommendation using LLM-as-judge"""

        system_prompt = """You are an expert financial portfolio evaluator. Your job is to assess portfolio recommendations for achieving specific financial goals.

Evaluate the portfolio on these dimensions (each 0-100):
1. **Diversification Score**: How well diversified is the portfolio across asset classes?
2. **Risk Score**: How appropriate is the risk level for the goal and timeline?
3. **Return Score**: How likely are the returns to meet the goal?

Based on these scores, estimate the **probability of success** (0-100) for achieving the goal with this portfolio.

Provide detailed reasoning and any concerns."""

        user_prompt = f"""Financial Goal:
{goal}

Recommended Portfolio:
{json.dumps(portfolio, indent=2)}

Evaluate this portfolio and provide scores and analysis. Format your response as JSON:
{{
  "diversification_score": <0-100>,
  "risk_score": <0-100>,
  "return_score": <0-100>,
  "probability_of_success": <0-100>,
  "reasoning": "Detailed explanation",
  "concerns": ["concern1", "concern2"],
  "overall_assessment": "Brief summary"
}}"""

        response = self._client.models.generate_content(
            model=os.getenv("EVALUATOR_MODEL", "gemini-2.0-flash"),
            contents=[
                {"role": "user", "parts": [{"text": system_prompt}]},
                {"role": "model", "parts": [{"text": "I understand. I will evaluate portfolios objectively."}]},
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            config={
                "temperature": 0.0,  # Deterministic outputs for reproducibility
                "top_p": 1.0,
                "top_k": 1,
            }
        )

        eval_text = response.text
        logger.info(f"LLM evaluation response: {eval_text}")

        # Parse evaluation
        try:
            eval_json = json.loads(eval_text)
            return PortfolioEvaluation(**eval_json)
        except:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', eval_text, re.DOTALL)
            if json_match:
                eval_json = json.loads(json_match.group(0))
                return PortfolioEvaluation(**eval_json)

            # Fallback: basic evaluation
            return PortfolioEvaluation(
                probability_of_success=50.0,
                diversification_score=50.0,
                risk_score=50.0,
                return_score=50.0,
                reasoning=f"Unable to parse LLM response: {eval_text}",
                concerns=["Evaluation parsing failed"],
                overall_assessment="Unable to complete evaluation"
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
