# Portfolio Assessment Agents - AgentBeats Competition

**Multi-scenario portfolio evaluation system** that tests investment portfolios across diverse financial goals simultaneously.

**Competition**: [AgentBeats Phase 1](https://rdi.berkeley.edu/agentx-agentbeats)
**Track**: Finance Agents (OpenAI sponsored)
**Status**: ✅ Deployed & Working
**Live**: [agentbeats.dev/rachnog](https://agentbeats.dev/rachnog)

## 🚀 Green Agent Quick Start (Competition Submission)

**Build and run the Portfolio Evaluator (Green Agent) end-to-end in 3 commands:**

```bash
# 1. Clone and navigate
git clone https://github.com/Rachnog/agentbeats-portfolio-assessment.git
cd agentbeats-portfolio-assessment/deployment

# 2. Build the green agent Docker image
docker build --platform linux/amd64 \
  -t portfolio-evaluator:latest \
  -f Dockerfile.green .

# 3. Run the green agent (replace your_gemini_api_key)
docker run -d -p 9009:9009 \
  -e GOOGLE_API_KEY=your_gemini_api_key \
  portfolio-evaluator:latest

# 4. Verify the agent is running
curl http://localhost:9009/.well-known/agent-card.json
```

**Requirements:**
- Docker with linux/amd64 platform support
- Google Gemini API key ([Get one free here](https://aistudio.google.com/app/apikey))
- Port 9009 available

**Expected output:** Agent card JSON with agent metadata, capabilities, and A2A protocol information.

**Pre-built images available:** `ghcr.io/rachnog/portfolio-evaluator:latest`

---

## Key Innovation: Multi-Scenario Evaluation

Unlike single-goal testing, this system evaluates **portfolio versatility** by testing the same portfolio across:
- **Retirement** (30 years): Long-term wealth accumulation
- **House Down Payment** (10 years): Medium-term savings goal
- **College Savings** (15 years): Education funding

**Results**: Aggregate success metrics + individual scenario breakdowns provide rich insights into portfolio adaptability.

**Latest Performance**: 94.3% average success (84.0% retirement, 99.5% house, 99.4% college)

## Agents

### Purple Agent (Portfolio Constructor)
**Image**: `ghcr.io/rachnog/portfolio-constructor:latest`
**Port**: 9009
**Technology**: Google ADK with Gemini 2.0 Flash
**Role**: Receives financial goals and recommends diversified investment portfolios

**Features**:
- Generates ticker-based portfolio recommendations (VTI, VXUS, BND, etc.)
- Validates allocations sum to 100%
- Provides reasoning for each holding
- Adapts to different risk tolerances and timelines

### Green Agent (Portfolio Evaluator)
**Image**: `ghcr.io/rachnog/portfolio-evaluator:latest`
**Port**: 9009
**Technology**: A2A SDK with Gemini 2.0 Flash
**Role**: Evaluates portfolio recommendations using multi-criteria LLM-as-judge methodology

**Features**:
- **Multi-scenario orchestration**: Tests portfolio across 3 diverse goals per run
- **Aggregate scoring**: Calculates average performance across scenarios
- **Individual analysis**: Detailed breakdown for each scenario
- **Assessment time**: ~1 minute for 3 scenarios
- **Cost**: < $0.02 per assessment (Gemini free tier)

## Repository Structure

```
.
├── deployment/
│   ├── Dockerfile.purple          # Purple agent container
│   ├── Dockerfile.green           # Green agent container
│   ├── requirements.txt           # Python dependencies
│   ├── portfolio_constructor.py   # Purple agent implementation
│   ├── portfolio_evaluator.py     # Green agent implementation
│   ├── quant_eval.py              # Quantitative evaluation module
│   ├── agentbeats/                # A2A framework modules
│   ├── ticker_cache/              # Cached market data
│   └── tests/                     # Unit tests
├── .github/
│   └── workflows/
│       └── publish.yml            # Docker image publishing
├── pyproject.toml                 # Project configuration
└── README.md                      # This file
```

## Additional Setup Options

### Pull Pre-Built Images

```bash
docker pull ghcr.io/rachnog/portfolio-constructor:latest
docker pull ghcr.io/rachnog/portfolio-evaluator:latest
```

### Run Locally with Pre-Built Images

```bash
# Start Purple Agent
docker run -d -p 9009:9009 \
  -e GOOGLE_API_KEY=your_key \
  ghcr.io/rachnog/portfolio-constructor:latest

# Start Green Agent
docker run -d -p 9009:9009 \
  -e GOOGLE_API_KEY=your_key \
  ghcr.io/rachnog/portfolio-evaluator:latest

# Verify
curl http://localhost:9009/.well-known/agent-card.json
```

### Build Both Agents from Source

```bash
cd deployment/

# Build purple agent
docker build --platform linux/amd64 \
  -t ghcr.io/rachnog/portfolio-constructor:latest \
  -f Dockerfile.purple .

# Build green agent
docker build --platform linux/amd64 \
  -t ghcr.io/rachnog/portfolio-evaluator:latest \
  -f Dockerfile.green .
```

## Environment Variables

Both agents require:
```bash
GOOGLE_API_KEY=your_gemini_api_key    # Required

# Optional (defaults shown)
CONSTRUCTOR_MODEL=gemini-2.0-flash    # Purple agent model
EVALUATOR_MODEL=gemini-2.0-flash      # Green agent model
LOG_LEVEL=INFO                        # Logging level
```

## Leaderboard

Assessment scenarios and leaderboard execution are managed in a separate repository:
**https://github.com/Rachnog/agentbeats-portfolio-assessment-leaderboard**

## Technical Details

### A2A Protocol
Both agents implement A2A protocol v0.3.0:
- Transport: JSON-RPC over HTTP
- Streaming: Supported
- Input/Output: Text mode
- Agent Cards: Standard format at `/.well-known/agent-card.json`

### Multi-Scenario Results Format

Assessment results include both aggregate scores and individual scenario breakdowns:

```json
{
  "participants": {
    "portfolio_constructor": "agent-id"
  },
  "results": [{
    "aggregate_scores": {
      "probability_of_success": 94.3,
      "diversification_score": 75.8,
      "risk_score": 80.4,
      "return_score": 89.1
    },
    "scenarios": [
      {
        "goal_type": "retirement",
        "timeline_years": 30,
        "probability_of_success": 84.0,
        "diversification_score": 75.8,
        "risk_score": 80.4,
        "return_score": 89.1,
        "portfolio": {...}
      },
      {
        "goal_type": "house",
        "timeline_years": 10,
        "probability_of_success": 99.5,
        ...
      },
      {
        "goal_type": "college",
        "timeline_years": 15,
        "probability_of_success": 99.4,
        ...
      }
    ],
    "num_scenarios": 3
  }]
}
```

### Dependencies
```
a2a-sdk>=0.3.0           # A2A protocol support
google-adk>=1.0.0        # Google Agent Development Kit
google-genai>=1.0.0      # Gemini API client
pydantic>=2.0.0          # Data validation
uvicorn>=0.23.0          # ASGI server
python-dotenv>=1.0.0     # Environment variables
yfinance>=0.2.0          # Market data
pandas>=2.0.0            # Data analysis
numpy>=1.24.0            # Numerical computing
scikit-learn>=1.3.0      # Machine learning utilities
```

## AgentBeats Registration

Both agents are registered on [agentbeats.dev](https://agentbeats.dev):
- Green Agent ID: `019bae3b-ca70-70b3-9e37-84e58b997c5e`
- Purple Agent ID: `019bae0d-9747-7102-8351-aff6255bc8a4`

## License

MIT License - See LICENSE file for details

---

**Author**: Rachnog (Alex Honchar)
**Last Updated**: January 12, 2026
**Version**: Multi-Scenario (v2.0)
