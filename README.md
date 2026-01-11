# Portfolio Construction Assessment - AgentBeats Competition

A novel portfolio construction assessment system for the AgentBeats Finance Agent Track, featuring multi-criteria LLM-based evaluation of investment recommendations.

**Competition**: [AgentBeats Phase 1](https://rdi.berkeley.edu/agentx-agentbeats)
**Track**: Finance Agents (OpenAI sponsored)
**Prizes**: $10,000 / $5,000 / $1,000
**Submission Date**: January 2026

---

## 🎯 Overview

This assessment evaluates an agent's ability to recommend investment portfolios for specific financial goals. The system uses two agents:

- **Purple Agent (Constructor)**: Receives financial goals and recommends diversified portfolios with ticker symbols and allocations
- **Green Agent (Evaluator)**: Assesses portfolio quality using multi-criteria LLM-as-judge methodology

### Example

**Input Goal:**
> Save $50,000 for a house down payment in 5 years. Starting: $10,000, Monthly: $500, Risk tolerance: Moderate

**Purple Agent Output:**
```json
{
  "tickers": [
    {"symbol": "VTI", "allocation_percent": 60},
    {"symbol": "BND", "allocation_percent": 30},
    {"symbol": "VNQ", "allocation_percent": 10}
  ],
  "expected_annual_return": "6-8%",
  "risk_assessment": "moderate"
}
```

**Green Agent Evaluation:**
- Probability of Success: 65%
- Diversification: 75/100
- Risk Appropriateness: 80/100
- Return Likelihood: 70/100
- Concerns: Interest rate sensitivity, goal ambition, market volatility

---

## 🐳 Docker Images

### Pull Images

```bash
# Purple Agent (Constructor)
docker pull ghcr.io/rachnog/portfolio-constructor:v1.0

# Green Agent (Evaluator)
docker pull ghcr.io/rachnog/portfolio-evaluator:v1.0
```

### Run Locally

```bash
# Purple Agent
docker run -p 9019:9019 \
  -e GOOGLE_API_KEY=your_key_here \
  ghcr.io/rachnog/portfolio-constructor:v1.0

# Green Agent
docker run -p 9009:9009 \
  -e GOOGLE_API_KEY=your_key_here \
  ghcr.io/rachnog/portfolio-evaluator:v1.0
```

### Agent Card URLs

Once running, agent cards are accessible at:
- Purple: `http://localhost:9019/.well-known/agent-card.json`
- Green: `http://localhost:9009/.well-known/agent-card.json`

---

## 🏗️ Architecture

### Purple Agent (Portfolio Constructor)

**Technology**: Google ADK (Agent Development Kit)
**Model**: Gemini 2.0 Flash (configurable via `CONSTRUCTOR_MODEL` env var)
**Port**: 9019

**Capabilities:**
- Analyzes financial goals in natural language
- Recommends 3-5 ticker portfolio with allocations
- Validates allocations sum to 100%
- Provides reasoning for each recommendation
- Returns structured JSON output

### Green Agent (Portfolio Evaluator)

**Technology**: A2A SDK
**Model**: Gemini 2.0 Flash (configurable via `EVALUATOR_MODEL` env var)
**Port**: 9009

**Evaluation Criteria:**
- **Diversification**: Portfolio spread across asset classes
- **Risk Appropriateness**: Match to goal timeline and risk tolerance
- **Return Likelihood**: Ability to achieve financial goal
- **Time Horizon**: Alignment with goal timeline
- **Overall Success Probability**: Weighted composite score

**Output**: Structured JSON with scores, concerns, and probability estimate

---

## 🔧 Configuration

### Environment Variables

Both agents require:

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
CONSTRUCTOR_MODEL=gemini-2.0-flash  # Purple agent model
EVALUATOR_MODEL=gemini-2.0-flash    # Green agent model
```

### Bring Your Own Key (BYOK)

This assessment uses Google's Gemini API (free tier available). You must provide your own API key:

1. Get a free API key: https://aistudio.google.com/apikey
2. Set as environment variable when running containers
3. Cost: Essentially free for testing (under free tier limits)

---

## 📊 Evaluation Methodology

### LLM-as-Judge

The green agent uses structured LLM evaluation with:

1. **Portfolio Validation**: Checks allocations, tickers, format
2. **Multi-Criteria Assessment**: Scores across 4 dimensions
3. **Concern Identification**: Flags potential issues
4. **Probability Estimation**: Overall success likelihood (0-100%)

### Scoring

```python
{
  "diversification_score": 0-100,      # Portfolio spread quality
  "risk_score": 0-100,                 # Risk alignment
  "return_score": 0-100,               # Return potential
  "time_horizon_score": 0-100,         # Timeline match
  "concerns": ["...", "...", "..."],   # Up to 5 issues
  "probability_of_success": 0-100      # Overall score
}
```

---

## 🚀 Development

### Build from Source

```bash
cd deployment/

# Build purple agent
docker build --platform linux/amd64 \
  -t portfolio-constructor:latest \
  -f Dockerfile.purple .

# Build green agent
docker build --platform linux/amd64 \
  -t portfolio-evaluator:latest \
  -f Dockerfile.green .
```

### Local Testing

```bash
# Create .env file
echo "GOOGLE_API_KEY=your_key" > .env

# Test purple agent
docker run -p 9019:9019 --env-file .env portfolio-constructor:latest

# Test green agent (in another terminal)
docker run -p 9009:9009 --env-file .env portfolio-evaluator:latest
```

---

## 📦 Repository Structure

```
.
├── README.md                      # This file
├── deployment/
│   ├── Dockerfile.purple          # Purple agent container
│   ├── Dockerfile.green           # Green agent container
│   ├── requirements.txt           # Python dependencies
│   ├── portfolio_constructor.py   # Purple agent code (88 lines)
│   ├── portfolio_evaluator.py     # Green agent code (306 lines)
│   └── agentbeats/                # Local A2A framework
└── .github/
    └── workflows/
        └── publish.yml            # Auto-publish to ghcr.io
```

---

## 🔬 Technical Details

### Dependencies

```
a2a-sdk>=0.3.0           # A2A protocol support
google-adk>=1.0.0        # Google Agent Development Kit
google-genai>=1.0.0      # Gemini API client
pydantic>=2.0.0          # Data validation
uvicorn>=0.23.0          # ASGI server
python-dotenv>=1.0.0     # Environment management
```

### A2A Protocol

Both agents implement the A2A protocol v0.3.0:
- **Transport**: JSON-RPC
- **Streaming**: Supported
- **Input/Output**: Text mode
- **Agent Cards**: Standard format

### Performance

- **Execution Time**: ~15-20 seconds per assessment
- **LLM Calls**: 2 (constructor + evaluator)
- **Token Usage**: ~700 tokens total
- **Cost**: Free tier (Gemini)

---

## 🎓 Why This Assessment?

### Novel Domain

Portfolio construction is rare in agent benchmarks, yet represents a real-world application with:
- Clear success criteria
- Measurable outcomes
- Professional-quality expectations
- Multiple valid approaches

### Sophisticated Evaluation

Unlike simple right/wrong benchmarks, this uses:
- Multi-dimensional scoring
- Risk-adjusted evaluation
- Concern identification
- Probability estimation

### OpenAI-Sponsored Track

The Finance Agent Track has dedicated prizes and judging, making this a competitive submission.

---

## 📈 Results

### Test Performance

**Scenario**: Save $50K for house in 5 years
- **Recommended Portfolio**: VTI (60%), BND (30%), VNQ (10%)
- **Success Probability**: 65%
- **Diversification**: 75/100
- **Risk Alignment**: 80/100
- **Return Potential**: 70/100
- **Concerns**: 3 realistic issues identified

### Quality Metrics

- ✅ Professional financial advice quality
- ✅ Real ticker symbols (not hallucinated)
- ✅ Valid JSON output
- ✅ Thoughtful concern identification
- ✅ Appropriate probability estimates

---

## 🎥 Demo Video

Watch the system in action: [YouTube Link]

Topics covered:
- System architecture explanation
- Live portfolio construction
- Evaluation criteria walkthrough
- Result interpretation
- Technical implementation

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built for the AgentBeats competition by RDI Foundation and UC Berkeley:
- **AgentBeats**: https://agentbeats.dev
- **A2A Protocol**: https://a2a-protocol.org
- **Tutorial**: https://github.com/RDI-Foundation/agentbeats-tutorial

**Competition Organizers**: RDI Foundation, UC Berkeley
**Sponsor**: OpenAI (Finance Agent Track)

---

## 📞 Contact

For questions about this submission:
- GitHub Issues: This repository
- AgentBeats Discord: #competition-q-and-a
- Competition Form: [Submission Link]

---

**Last Updated**: January 2026
**Version**: 1.0.0
**Status**: Submitted to AgentBeats Phase 1
