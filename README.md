# Portfolio Construction Assessment - AgentBeats Competition

A novel portfolio construction assessment system for the AgentBeats Finance Agent Track, featuring multi-criteria LLM-based evaluation of investment recommendations using GitHub Actions for reproducible assessment execution.

**Competition**: [AgentBeats Phase 1](https://rdi.berkeley.edu/agentx-agentbeats)
**Track**: Finance Agents (OpenAI sponsored)
**Prizes**: $10,000 / $5,000 / $1,000
**Deadline**: January 15, 2026, 11:59pm PT
**Platform**: [agentbeats.dev](https://agentbeats.dev)

---

## 🎯 Overview

This assessment evaluates an agent's ability to recommend investment portfolios for specific financial goals. The system uses two agents:

- **🟣 Purple Agent (Constructor)**: Receives financial goals and recommends diversified portfolios with ticker symbols and allocations
- **🟢 Green Agent (Evaluator)**: Assesses portfolio quality using multi-criteria LLM-as-judge methodology

### Example Evaluation

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
- **Probability of Success**: 65%
- **Diversification Score**: 75/100
- **Risk Appropriateness**: 80/100
- **Return Likelihood**: 70/100
- **Time Horizon Alignment**: 85/100
- **Concerns**: Interest rate sensitivity, goal ambition, market volatility

---

## 🐳 Docker Images

### Public Images on GitHub Container Registry

```bash
# Purple Agent (Portfolio Constructor)
docker pull ghcr.io/rachnog/portfolio-constructor:v1.0

# Green Agent (Portfolio Evaluator)
docker pull ghcr.io/rachnog/portfolio-evaluator:v1.0
```

**Registry**: [GitHub Container Registry](https://github.com/Rachnog?tab=packages)
**Platform**: linux/amd64
**Size**: ~746MB each

### Quick Local Test

```bash
# Start Purple Agent
docker run -d -p 9019:9019 \
  -e GOOGLE_API_KEY=your_gemini_api_key \
  ghcr.io/rachnog/portfolio-constructor:v1.0

# Start Green Agent
docker run -d -p 9009:9009 \
  -e GOOGLE_API_KEY=your_gemini_api_key \
  ghcr.io/rachnog/portfolio-evaluator:v1.0

# Verify agents are running
curl http://localhost:9019/.well-known/agent-card.json
curl http://localhost:9009/.well-known/agent-card.json
```

---

## 🏗️ Architecture

### Purple Agent (Portfolio Constructor)

**Technology**: Google ADK (Agent Development Kit)
**Model**: Gemini 2.0 Flash
**Port**: 9019
**Protocol**: A2A v0.3.0 (JSON-RPC)

**Capabilities:**
- Natural language financial goal analysis
- 3-5 ticker portfolio recommendations
- Allocation validation (sums to 100%)
- Risk-adjusted asset selection
- Structured JSON output

**Code**: [`deployment/portfolio_constructor.py`](deployment/portfolio_constructor.py) (88 lines)

### Green Agent (Portfolio Evaluator)

**Technology**: A2A SDK
**Model**: Gemini 2.0 Flash
**Port**: 9009
**Protocol**: A2A v0.3.0 (JSON-RPC)

**Evaluation Criteria:**
1. **Diversification** (0-100): Portfolio spread across asset classes
2. **Risk Appropriateness** (0-100): Match to goal timeline and risk tolerance
3. **Return Likelihood** (0-100): Ability to achieve financial goal
4. **Time Horizon Alignment** (0-100): Alignment with goal timeline
5. **Overall Success Probability** (0-100%): Weighted composite score

**Code**: [`deployment/portfolio_evaluator.py`](deployment/portfolio_evaluator.py) (306 lines)

---

## 🚀 Running Assessments

### Method 1: GitHub Actions (Official & Automated) ✅

The official way to run assessments on AgentBeats platform:

#### Step 1: Configure Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add secret: `GOOGLE_API_KEY` with your Gemini API key

#### Step 2: Trigger Workflow

```bash
# Option A: Push scenario.toml changes
git add scenario.toml
git commit -m "Update assessment scenarios"
git push origin main

# Option B: Manual trigger via GitHub UI
# Go to Actions → Run Portfolio Assessment → Run workflow
```

#### Step 3: Monitor Execution

1. Navigate to **Actions** tab
2. Click on latest workflow run
3. Watch agents start and execute assessments (~5-10 minutes)
4. Download results from artifacts

#### Step 4: Review Results

Workflow creates a pull request with results:
- JSON artifacts in `results/` directory
- Assessment summary
- Execution metrics

Merge PR → Results appear on leaderboard!

### Method 2: Local Testing (Development)

```bash
# Clone repository
git clone https://github.com/Rachnog/agentbeats-portfolio-assessment.git
cd agentbeats-portfolio-assessment

# Set API key
export GOOGLE_API_KEY=your_key_here

# Start agents
docker-compose up -d

# Run assessment script
python scripts/run_local_assessment.py

# View results
cat results/assessment_results.json
```

---

## 📊 Evaluation Methodology

### LLM-as-Judge Framework

The green agent uses structured LLM evaluation with:

1. **Portfolio Validation**: Checks allocations, ticker validity, format compliance
2. **Multi-Criteria Scoring**: 4 dimensions with 0-100 scores
3. **Concern Identification**: Flags up to 5 potential issues
4. **Probability Estimation**: Overall success likelihood (0-100%)

### Scoring Algorithm

```python
success_probability = (
    0.40 * diversification_score +
    0.20 * risk_score +
    0.20 * return_score +
    0.10 * time_horizon_score -
    0.10 * concern_penalty
)
```

### Ranking System

Agents ranked by:
1. **Primary**: Success probability (higher is better)
2. **Tiebreaker 1**: Diversification score
3. **Tiebreaker 2**: Risk alignment score
4. **Tiebreaker 3**: Fewer concerns
5. **Tiebreaker 4**: Faster execution time

---

## 📈 Leaderboard

### SQL Query Configuration

The leaderboard uses DuckDB to query JSON results:

```sql
SELECT
    purple_agent_name,
    purple_agent_url,
    CAST(JSON_EXTRACT(evaluation, '$.probability_of_success') AS INT64) as success_probability,
    CAST(JSON_EXTRACT(evaluation, '$.diversification_score') AS INT64) as diversification,
    -- ... more metrics
FROM `agentbeats.portfolio_construction_results`
WHERE JSON_EXTRACT(evaluation, '$.probability_of_success') IS NOT NULL
ORDER BY success_probability DESC, diversification DESC
LIMIT 100;
```

**Full query**: [`leaderboard/leaderboard.sql`](leaderboard/leaderboard.sql)

### Display

| Rank | Agent | Success % | Diversification | Risk Align | Concerns |
|------|-------|-----------|-----------------|------------|----------|
| 1 | portfolio_constructor | 65% | 75 | 80 | 3 |

---

## 🔧 Configuration

### Environment Variables

Both agents require:

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional (defaults shown)
CONSTRUCTOR_MODEL=gemini-2.0-flash    # Purple agent model
EVALUATOR_MODEL=gemini-2.0-flash      # Green agent model
```

### Assessment Scenarios

Edit [`scenario.toml`](scenario.toml) to customize test scenarios:

```toml
[[scenarios]]
id = "house_down_payment_5yr"
goal = "Save $50,000 for house in 5 years..."
starting_amount = 10000
monthly_contribution = 500
target_amount = 50000
timeline_years = 5
risk_tolerance = "moderate"
```

**Included scenarios**:
1. House down payment (5 years, moderate risk)
2. Retirement savings (30 years, aggressive risk)
3. Education fund (10 years, moderate risk)
4. Emergency fund (1 year, conservative risk)
5. Wealth growth (15 years, aggressive risk)

---

## 📦 Repository Structure

```
.
├── README.md                      # This file
├── scenario.toml                  # Assessment configuration
├── deployment/
│   ├── Dockerfile.purple          # Purple agent container
│   ├── Dockerfile.green           # Green agent container
│   ├── requirements.txt           # Python dependencies
│   ├── portfolio_constructor.py   # Purple agent code (88 lines)
│   ├── portfolio_evaluator.py     # Green agent code (306 lines)
│   └── agentbeats/                # Local A2A framework
├── leaderboard/
│   ├── leaderboard.sql            # DuckDB ranking query
│   ├── leaderboard_config.json    # Full configuration
│   └── README.md                  # Methodology documentation
├── .github/
│   └── workflows/
│       ├── publish.yml            # Auto-publish Docker images
│       └── run-assessment.yml     # Run evaluations
└── DEMO_VIDEO_SCRIPT.md           # Video recording guide
```

---

## 🎥 Demo Video

Watch the system in action: [YouTube Link]

**Topics covered**:
- System architecture explanation
- Live portfolio construction demonstration
- Evaluation criteria walkthrough
- Result interpretation
- GitHub Actions workflow
- Technical implementation details

**Script**: [`DEMO_VIDEO_SCRIPT.md`](DEMO_VIDEO_SCRIPT.md)

---

## 🛠️ Development

### Building from Source

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
echo "GOOGLE_API_KEY=your_key" > deployment/.env

# Test purple agent
docker run -p 9019:9019 --env-file deployment/.env portfolio-constructor:latest

# Test green agent (in another terminal)
docker run -p 9009:9009 --env-file deployment/.env portfolio-evaluator:latest

# Verify both agents
curl http://localhost:9019/.well-known/agent-card.json | jq .
curl http://localhost:9009/.well-known/agent-card.json | jq .
```

### Running Assessments Locally

```bash
# Test purple agent
curl -X POST http://localhost:9019/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agent_send",
    "params": {
      "message": {
        "role": "user",
        "content": "I want to save $50,000 for a house down payment in 5 years..."
      }
    },
    "id": 1
  }' | jq .
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

Both agents implement A2A protocol v0.3.0:
- **Transport**: JSON-RPC over HTTP
- **Streaming**: Supported
- **Input/Output**: Text mode
- **Agent Cards**: Standard format at `/.well-known/agent-card.json`

### Performance

- **Execution Time**: ~15-20 seconds per assessment
- **LLM Calls**: 2 per evaluation (constructor + evaluator)
- **Token Usage**: ~700 tokens total
- **Cost**: Free tier (Gemini 2.0 Flash)

---

## 🎓 Why This Assessment?

### Novel Financial Domain

Portfolio construction is rare in agent benchmarks, yet represents a real-world application with:
- Clear success criteria
- Measurable outcomes
- Professional-quality expectations
- Multiple valid approaches

### Sophisticated Multi-Criteria Evaluation

Unlike simple right/wrong benchmarks, this uses:
- 4-dimensional scoring (diversification, risk, return, time)
- Weighted composite probability
- Concern identification and penalty
- Risk-adjusted evaluation

### OpenAI-Sponsored Finance Track

The Finance Agent Track has dedicated prizes and judging, making this a competitive submission.

### Reproducible via GitHub Actions

- Isolated execution environment
- Verifiable results in version control
- Automated leaderboard updates
- Full audit trail

---

## 📝 Submission

### Competition Form

Submit via [Google Form](https://docs.google.com/forms/d/e/1FAIpQLSdtqxWcGl2Qg5RPuNF2O3_N07uD0HMJpWBCwZWZbD3dxTuWmg/viewform):

**Required information**:
- Track: Finance Agents
- Purple Agent: `ghcr.io/rachnog/portfolio-constructor:v1.0` (port 9019)
- Green Agent: `ghcr.io/rachnog/portfolio-evaluator:v1.0` (port 9009)
- GitHub: `https://github.com/Rachnog/agentbeats-portfolio-assessment`
- Demo Video: [YouTube URL]
- Leaderboard: `https://github.com/Rachnog/agentbeats-portfolio-assessment/tree/main/leaderboard`

**Description**:
> Multi-criteria portfolio construction assessment using LLM-as-judge methodology. Purple agent recommends investment portfolios for financial goals, green agent evaluates across diversification, risk alignment, return potential, and time horizon. Built with Google ADK and A2A protocol v0.3.0.

### Platform Registration

Both agents registered on [agentbeats.dev](https://agentbeats.dev):
- Purple: portfolio_constructor
- Green: portfolio_evaluator
- Category: Finance Agent
- Leaderboard: Configured with BigQuery SQL queries

---

## 🙏 Acknowledgments

Built for the AgentBeats competition by RDI Foundation and UC Berkeley:
- **AgentBeats**: https://agentbeats.dev
- **A2A Protocol**: https://a2a-protocol.org
- **Tutorial**: https://github.com/RDI-Foundation/agentbeats-tutorial
- **Competition**: https://rdi.berkeley.edu/agentx-agentbeats

**Competition Organizers**: RDI Foundation, UC Berkeley
**Sponsor**: OpenAI (Finance Agent Track)
**Author**: Rachnog (Alex Honchar)

---

## 📞 Contact

For questions about this submission:
- **GitHub Issues**: This repository
- **AgentBeats Discord**: #competition-q-and-a
- **Competition Form**: [Submission Link](https://docs.google.com/forms/d/e/1FAIpQLSdtqxWcGl2Qg5RPuNF2O3_N07uD0HMJpWBCwZWZbD3dxTuWmg/viewform)

---

## 📜 License

MIT License - See LICENSE file for details

---

**Last Updated**: January 11, 2026
**Version**: 1.0.0
**Status**: Ready for Submission
**Agents**: Registered on agentbeats.dev
**Docker Images**: Public on ghcr.io
**GitHub Actions**: Configured for automated assessments
