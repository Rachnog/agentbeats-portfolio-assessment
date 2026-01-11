#!/usr/bin/env python3
"""
Portfolio Constructor Agent (Purple Agent)
Receives financial goals and recommends portfolio of tickers.
"""

import argparse
import logging
import os
import uvicorn
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from a2a.types import (
    AgentCapabilities,
    AgentCard,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("portfolio_constructor")


def main():
    parser = argparse.ArgumentParser(description="Run the portfolio constructor agent")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9019)
    parser.add_argument("--card-url", type=str, help="External URL for agent card")
    args = parser.parse_args()

    model_name = os.getenv("CONSTRUCTOR_MODEL", "gemini-2.0-flash")
    card_url = args.card_url or f'http://{args.host}:{args.port}/'

    logger.info(f"Starting portfolio constructor on {args.host}:{args.port}")
    logger.info(f"Using model: {model_name}")
    logger.info(f"Card URL: {card_url}")

    # Create agent with instruction
    root_agent = Agent(
        name="portfolio_constructor",
        model=os.getenv("CONSTRUCTOR_MODEL", "gemini-2.0-flash"),
        description="Analyzes financial goals and recommends investment portfolios.",
        instruction="""You are a financial portfolio advisor. When given a financial goal, recommend a diversified portfolio of 3-5 ticker symbols (ETFs or stocks).

Provide your response in this EXACT JSON format:
{
  "tickers": [
    {
      "symbol": "TICKER1",
      "allocation_percent": 40,
      "reasoning": "Brief explanation"
    }
  ],
  "investment_horizon_years": 5,
  "expected_annual_return": "6-8%",
  "risk_assessment": "moderate",
  "reasoning": "Overall portfolio strategy explanation"
}

Important rules:
- Allocations must sum to 100%
- Use real, common ticker symbols (VTI, BND, VNQ, SPY, QQQ, etc.)
- Match risk level to the goal's timeline and risk tolerance
- Be specific and concise
- Return ONLY valid JSON, no other text""",
    )

    # Create agent card
    agent_card = AgentCard(
        name="portfolio_constructor",
        description="Analyzes financial goals and recommends investment portfolios with ticker symbols and allocations.",
        url=card_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[],
    )

    # Convert to A2A app
    a2a_app = to_a2a(root_agent, agent_card=agent_card)

    # Run the server
    uvicorn.run(a2a_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
