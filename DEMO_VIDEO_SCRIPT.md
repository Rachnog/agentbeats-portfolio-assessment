# Demo Video Script - Portfolio Construction Assessment

**Target Length**: 3-5 minutes
**Format**: Screen recording with voiceover
**Goal**: Clearly demonstrate the system and its value

---

## 🎬 Scene 1: Introduction (30 seconds)

### Visual
- Show GitHub repository README
- Highlight competition badges
- Quick overview of repository structure

### Script
> "Hi, I'm presenting my submission for the AgentBeats Finance Agent Track - a portfolio construction assessment system. This evaluates an agent's ability to recommend investment portfolios for specific financial goals using multi-criteria LLM evaluation. Let me show you how it works."

---

## 🎬 Scene 2: Architecture Overview (45 seconds)

### Visual
- Show architecture diagram (or simple drawing)
- Display both agent cards in browser

### Script
> "The system uses two agents following the A2A protocol. The purple agent is the constructor - it receives financial goals and recommends diversified portfolios with specific ticker symbols and allocations. The green agent is the evaluator - it assesses portfolio quality across multiple dimensions: diversification, risk appropriateness, return likelihood, and time horizon alignment."

### Demo Actions
```bash
# Show purple agent card
curl http://localhost:9019/.well-known/agent-card.json | jq

# Show green agent card
curl http://localhost:9009/.well-known/agent-card.json | jq
```

---

## 🎬 Scene 3: Live Demonstration (90-120 seconds)

### Visual
- Terminal showing agent logs
- JSON responses highlighted

### Script
> "Let me run a live assessment. Our test goal is: Save $50,000 for a house down payment in 5 years, starting with $10,000 and contributing $500 monthly, with moderate risk tolerance."

### Demo Actions
```bash
# If you have agentbeats CLI setup:
cd ../1_initial_experiments/agentbeats-tutorial
PYTHONPATH=src uv run python src/agentbeats/run_scenario.py \
  ../portfolio_minimal/scenarios/portfolio/scenario.toml --show-logs
```

### Narration During Execution
> "Watch as the purple agent analyzes the goal... It's recommending a three-ETF portfolio: 60% VTI for broad market exposure, 30% BND for stability, and 10% VNQ for real estate diversification."

> "Now the green agent evaluates this portfolio... It's scoring diversification at 75 out of 100, risk alignment at 80, and return potential at 70. The overall success probability is 65%."

> "The evaluator also identified three realistic concerns: interest rate sensitivity from the bond allocation, the ambitious goal relative to contributions, and general market volatility risk."

---

## 🎬 Scene 4: Results Interpretation (45 seconds)

### Visual
- Show JSON output formatted nicely
- Highlight key metrics

### Script
> "The results are comprehensive. We get structured evaluation across four criteria, specific concerns with explanations, and an overall probability of success. This goes beyond simple right-or-wrong evaluation - it provides nuanced assessment of financial advice quality."

### Show in Terminal
```json
{
  "probability_of_success": 65,
  "diversification_score": 75,
  "risk_score": 80,
  "return_score": 70,
  "time_horizon_score": 75,
  "concerns": [
    "Interest rate sensitivity in bonds",
    "Goal may be ambitious given contributions",
    "Market volatility risk exposure"
  ]
}
```

---

## 🎬 Scene 5: Why This Matters (30 seconds)

### Visual
- Show competition information
- Display key differentiators

### Script
> "Why portfolio construction? It's a real-world financial application with measurable outcomes and multiple valid approaches. Unlike simple benchmarks, this requires understanding risk tolerance, time horizons, and market dynamics. It's perfect for evaluating agent capabilities in a professional domain."

---

## 🎬 Scene 6: Technical Highlights (30 seconds)

### Visual
- Show Dockerfiles
- Display deployment architecture

### Script
> "From a technical standpoint: Both agents run in Docker containers on x86 architecture, use Google's Gemini API under a bring-your-own-key model, and implement the A2A protocol version 0.3.0. The entire assessment runs in about 15 seconds and costs essentially nothing thanks to Gemini's free tier."

---

## 🎬 Scene 7: Leaderboard & Closing (30 seconds)

### Visual
- Show leaderboard repository
- Display SQL query briefly
- End on GitHub repository

### Script
> "I've also prepared a leaderboard system using BigQuery to rank different agents by success probability and other metrics. The complete code, Dockerfiles, and documentation are available in the GitHub repository. Thank you for watching, and I look forward to seeing this in the AgentBeats competition!"

---

## 📝 Recording Tips

### Preparation
1. **Clean your desktop** - Close unnecessary applications
2. **Test audio** - Clear microphone, no background noise
3. **Rehearse** - Practice script 2-3 times
4. **Have agents running** - Start containers before recording
5. **Prepare terminals** - Have commands ready to copy-paste

### During Recording
1. **Speak clearly and naturally** - Don't rush
2. **Pause between sections** - Easier to edit
3. **Use a timer** - Stay within 3-5 minute target
4. **Show enthusiasm** - This is cool work!
5. **Point with cursor** - Highlight important info

### Technical Setup
```bash
# Terminal 1: Purple agent
docker run -p 9019:9019 --env-file .env portfolio-constructor:latest

# Terminal 2: Green agent
docker run -p 9009:9009 --env-file .env portfolio-evaluator:latest

# Terminal 3: Demo commands
cd 1_initial_experiments/agentbeats-tutorial
# Ready to run assessment
```

### Screen Recording Tools
- **macOS**: QuickTime Player (free, built-in)
- **Windows**: OBS Studio (free)
- **Linux**: SimpleScreenRecorder (free)

### Video Editing (Optional)
- **Basic**: iMovie (Mac), Photos (Windows)
- **Advanced**: DaVinci Resolve (free, all platforms)

### Upload Specs
- **Resolution**: 1080p minimum
- **Format**: MP4
- **Privacy**: Unlisted (shareable link for judges)
- **Title**: "Portfolio Construction Assessment - AgentBeats Submission"
- **Description**: Link to GitHub repository

---

## ✅ Pre-Recording Checklist

- [ ] Docker images built and tested
- [ ] API key in .env file
- [ ] Agents start successfully
- [ ] Test run completes successfully
- [ ] Script rehearsed
- [ ] Audio tested
- [ ] Screen clean
- [ ] Recording software configured
- [ ] Timer ready

---

## 🎯 Key Points to Emphasize

1. **Novel Domain**: Financial portfolio construction is unique
2. **Real-World Application**: Actual professional use case
3. **Sophisticated Evaluation**: Multi-criteria, not binary
4. **Working System**: Live demonstration proves it works
5. **Production Ready**: Dockerized, documented, deployable

---

## 📺 After Recording

1. **Watch once** - Check for issues
2. **Edit if needed** - Trim mistakes, add title card
3. **Upload to YouTube** - Unlisted privacy
4. **Get shareable link** - Copy for submission form
5. **Test link** - Make sure it works in incognito mode

---

**Good luck with your recording! You've built something impressive - now show it off!** 🚀
