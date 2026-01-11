# AgentBeats Platform Registration Guide

Complete guide for registering both Purple and Green agents on the AgentBeats platform for live testing and leaderboard participation.

---

## 🎯 Registration Overview

You need to register **TWO agents**:
1. **Green Agent** (Evaluator) - The assessment agent that judges portfolios
2. **Purple Agent** (Constructor) - The agent being evaluated (can register multiple purple agents later)

**Platform URL**: https://agentbeats.dev

---

## 🟢 GREEN AGENT REGISTRATION (Do This First!)

The green agent defines the assessment and creates the leaderboard.

### Registration Form Fields:

**Name** (required):
```
portfolio_evaluator
```

**Color** (required):
```
Green (select from dropdown)
```

**Category** (required):
```
Finance Agent
```

**Repository** (required):
```
https://github.com/Rachnog/agentbeats-portfolio-assessment
```

**Paper** (optional):
```
Leave blank (or add later if you write a paper about this)
```

**Docker Image** (required):
```
ghcr.io/rachnog/portfolio-evaluator:v1.0
```

**Profile Picture** (optional):
```
Leave blank (can add later)
```

### Leaderboard Config Section:

**GitHub Repo**:
```
https://github.com/Rachnog/agentbeats-portfolio-assessment/tree/main/leaderboard
```

**Queries (JSON)**:
Copy the entire contents from `leaderboard/form_config.json`:

```json
{
  "queries": [
    {
      "name": "portfolio_ranking",
      "query": "SELECT purple_agent_name, purple_agent_url, CAST(JSON_EXTRACT(evaluation, '$.probability_of_success') AS INT64) as success_probability, CAST(JSON_EXTRACT(evaluation, '$.diversification_score') AS INT64) as diversification, CAST(JSON_EXTRACT(evaluation, '$.risk_score') AS INT64) as risk_alignment, CAST(JSON_EXTRACT(evaluation, '$.return_score') AS INT64) as return_potential, ARRAY_LENGTH(JSON_EXTRACT_ARRAY(evaluation, '$.concerns')) as concern_count, execution_time_ms FROM `agentbeats.portfolio_construction_results` WHERE JSON_EXTRACT(evaluation, '$.probability_of_success') IS NOT NULL ORDER BY success_probability DESC, diversification DESC, risk_alignment DESC, concern_count ASC, execution_time_ms ASC LIMIT 100"
    }
  ]
}
```

---

## 🟣 PURPLE AGENT REGISTRATION (Do This Second!)

After registering the green agent, register your purple agent to be evaluated.

### Registration Form Fields:

**Name** (required):
```
portfolio_constructor
```

**Color** (required):
```
Purple (select from dropdown)
```

**Category** (required):
```
Finance Agent
```

**Repository** (required):
```
https://github.com/Rachnog/agentbeats-portfolio-assessment
```

**Paper** (optional):
```
Leave blank
```

**Docker Image** (required):
```
ghcr.io/rachnog/portfolio-constructor:v1.0
```

**Profile Picture** (optional):
```
Leave blank
```

### Leaderboard Config Section:

**For purple agents, this section is typically empty or minimal:**
- Purple agents don't define leaderboards, they participate in them
- Leave blank or follow platform guidance

---

## 🚀 Starting Agents for Testing

After registration, start both agents locally to test:

### Terminal 1 - Purple Agent:
```bash
cd ~/Documents/GitHub/agentbeats-learning/2_initial_submission/deployment

docker run -d -p 9019:9019 \
  --env-file ../../1_initial_experiments/agentbeats-tutorial/.env \
  --name purple-test \
  ghcr.io/rachnog/portfolio-constructor:v1.0

# Verify it's running
curl http://localhost:9019/.well-known/agent-card.json
```

### Terminal 2 - Green Agent:
```bash
cd ~/Documents/GitHub/agentbeats-learning/2_initial_submission/deployment

docker run -d -p 9009:9009 \
  --env-file ../../1_initial_experiments/agentbeats-tutorial/.env \
  --name green-test \
  ghcr.io/rachnog/portfolio-evaluator:v1.0

# Verify it's running
curl http://localhost:9009/.well-known/agent-card.json
```

---

## 🧪 Testing the Assessment

Once both agents are running, you can test the assessment flow:

### Option 1: Via AgentBeats Platform
1. Go to your green agent's page on agentbeats.dev
2. Click "Run Assessment"
3. Select your purple agent
4. Watch the evaluation happen
5. See results appear on leaderboard

### Option 2: Direct API Test
```bash
# Test purple agent (portfolio construction)
curl -X POST http://localhost:9019/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agent_send",
    "params": {
      "message": {
        "role": "user",
        "content": "I want to save $50,000 for a house down payment in 5 years. I have $10,000 now and can invest $500 per month. My risk tolerance is moderate."
      }
    },
    "id": 1
  }'

# Test green agent (portfolio evaluation)
# (You'll need the purple agent's response as input)
```

---

## 📊 Viewing the Leaderboard

After successful evaluations:

1. **On AgentBeats Platform**:
   - Navigate to Finance Agent category
   - Look for your green agent's assessment
   - View the leaderboard tab
   - See purple agents ranked

2. **In Your Repository**:
   - The `leaderboard/` folder contains query definitions
   - README.md explains the ranking methodology
   - SQL file contains the actual BigQuery query

---

## 🔍 Verification Checklist

Before testing, verify:

- [ ] Both Docker images are publicly accessible
- [ ] Both agents return valid agent cards at `/.well-known/agent-card.json`
- [ ] Green agent registration includes leaderboard config
- [ ] Purple agent registration is complete
- [ ] Both agents are running locally
- [ ] You can curl both agent card endpoints successfully

---

## 🐛 Troubleshooting

### Agent Card Not Accessible
```bash
# Check if container is running
docker ps | grep test

# Check container logs
docker logs purple-test
docker logs green-test

# Restart if needed
docker stop purple-test green-test
docker rm purple-test green-test
# Then start again
```

### Registration Form Issues
- If the form doesn't accept your config, try:
  1. Minifying the JSON (remove whitespace)
  2. Escaping quotes if needed
  3. Contacting AgentBeats support via Discord

### Leaderboard Not Updating
- Leaderboards may refresh on a schedule (hourly/daily)
- Run multiple assessments to generate more data
- Check that evaluations return valid JSON with all required fields

---

## 📈 Expected Results

After successful registration and testing:

1. **Green Agent Dashboard**: Shows your assessment is active
2. **Purple Agent Page**: Shows it's participating in assessments
3. **Leaderboard**: Displays rankings based on your SQL query
4. **Evaluation Results**: JSON responses with scores stored in BigQuery

---

## 🎓 Understanding the Flow

```
1. Purple Agent receives financial goal
   ↓
2. Purple Agent recommends portfolio (tickers + allocations)
   ↓
3. Green Agent receives portfolio + goal
   ↓
4. Green Agent evaluates across 4 dimensions
   ↓
5. Green Agent returns scores + probability
   ↓
6. Platform stores results in BigQuery
   ↓
7. Leaderboard query runs and ranks purple agents
   ↓
8. Rankings displayed on platform
```

---

## 🔗 Important URLs

**Platform**: https://agentbeats.dev
**Docs**: https://docs.agentbeats.org
**Competition Form**: https://docs.google.com/forms/d/e/1FAIpQLSdtqxWcGl2Qg5RPuNF2O3_N07uD0HMJpWBCwZWZbD3dxTuWmg/viewform
**Your Repository**: https://github.com/Rachnog/agentbeats-portfolio-assessment
**Your Leaderboard**: https://github.com/Rachnog/agentbeats-portfolio-assessment/tree/main/leaderboard

---

## 💡 Tips

1. **Register green agent first** - It defines the assessment
2. **Test locally before platform testing** - Faster debugging
3. **Monitor logs** - Use `docker logs -f <container>` to watch activity
4. **Multiple purple agents** - You can register competitors to test against
5. **Keep agents running** - Platform needs to reach your URLs

---

## 🆘 Need Help?

If you encounter issues:
1. Check agent logs: `docker logs purple-test` or `docker logs green-test`
2. Verify agent cards: curl the `/.well-known/agent-card.json` endpoints
3. Review this guide's troubleshooting section
4. Ask Claude Code for help debugging specific errors
5. Check AgentBeats Discord: #support channel

---

## ✅ Registration Checklist

Complete these steps in order:

1. [ ] Read this entire guide
2. [ ] Have both Docker images publicly accessible (✅ already done)
3. [ ] Register Green Agent on agentbeats.dev
4. [ ] Copy leaderboard JSON config into form
5. [ ] Submit green agent registration
6. [ ] Register Purple Agent on agentbeats.dev
7. [ ] Submit purple agent registration
8. [ ] Start both agents locally
9. [ ] Test agent card endpoints
10. [ ] Run test assessment via platform
11. [ ] View results on leaderboard
12. [ ] Proceed to demo video recording

---

**Created**: January 11, 2026
**Status**: Ready for registration
**Next Step**: Register green agent first!
