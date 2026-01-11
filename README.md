# Portfolio Assessment Agents - AgentBeats Competition

Agent implementations for the AgentBeats Finance Agent Track competition.

**Competition**: [AgentBeats Phase 1](https://rdi.berkeley.edu/agentx-agentbeats)
**Track**: Finance Agents (OpenAI sponsored)
**Deadline**: January 15, 2026

## Agents

### Purple Agent (Portfolio Constructor)
**Image**: `ghcr.io/rachnog/portfolio-constructor:latest`
**Port**: 9009
**Technology**: Google ADK with Gemini 2.0 Flash
**Role**: Receives financial goals and recommends diversified investment portfolios

### Green Agent (Portfolio Evaluator)
**Image**: `ghcr.io/rachnog/portfolio-evaluator:latest`
**Port**: 9009
**Technology**: A2A SDK with Gemini 2.0 Flash
**Role**: Evaluates portfolio recommendations using multi-criteria LLM-as-judge methodology

## Repository Structure

```
.
├── deployment/
│   ├── Dockerfile.purple          # Purple agent container
│   ├── Dockerfile.green           # Green agent container
│   ├── requirements.txt           # Python dependencies
│   ├── portfolio_constructor.py   # Purple agent implementation
│   ├── portfolio_evaluator.py     # Green agent implementation
│   └── agentbeats/                # A2A framework modules
├── .github/
│   └── workflows/
│       └── publish.yml            # Docker image publishing
├── pyproject.toml                 # Project configuration
└── README.md                      # This file
```

## Quick Start

### Pull Images

```bash
docker pull ghcr.io/rachnog/portfolio-constructor:latest
docker pull ghcr.io/rachnog/portfolio-evaluator:latest
```

### Run Locally

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

### Build from Source

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

### Dependencies
```
a2a-sdk>=0.3.0           # A2A protocol support
google-adk>=1.0.0        # Google Agent Development Kit
google-genai>=1.0.0      # Gemini API client
pydantic>=2.0.0          # Data validation
uvicorn>=0.23.0          # ASGI server
```

## AgentBeats Registration

Both agents are registered on [agentbeats.dev](https://agentbeats.dev):
- Green Agent ID: `019bae3b-ca70-70b3-9e37-84e58b997c5e`
- Purple Agent ID: `019bae0d-9747-7102-8351-aff6255bc8a4`

## License

MIT License - See LICENSE file for details

---

**Author**: Rachnog (Alex Honchar)
**Last Updated**: January 11, 2026
