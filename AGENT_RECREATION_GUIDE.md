# Agent Recreation Guide - Fresh Start
**Date:** 2026-01-11 17:20 CET

---

## 🎯 Why Recreate?

The platform may have cached configuration causing the persistent leaderboard fetch error. Starting fresh will clear any problematic state.

---

## ⚠️ Before You Delete

### 1. Save Your Current Settings

**Document these from your current agent:**
- Green Agent ID: `019bad43-ecbb-75f0-8116-7301bebaaad8`
- Name: `portfolio_evaluator`
- Repository: `https://github.com/Rachnog/agentbeats-portfolio-assessment`
- Docker Image: `ghcr.io/rachnog/portfolio-evaluator:v1.0`
- Paper Link: `https://arxiv.org/abs/1706.03762`

### 2. Your Repository is Ready

Your repo is already correctly configured:
- ✅ `scenario.toml` with proper format
- ✅ `results/` with correct JSON format
- ✅ `leaderboard/` directory (optional)
- ✅ Docker images published
- ✅ All files public and accessible

---

## 📋 Step-by-Step Recreation

### STEP 1: Delete Existing Agents

1. Go to https://agentbeats.dev
2. Navigate to your `portfolio_evaluator` agent page
3. Click **"Edit Agent"**
4. Scroll to bottom
5. Click **"Delete Agent"** button (red button)
6. Confirm deletion

**Note:** There's only the green agent to delete. The purple agent (portfolio_constructor) is not separately registered - it's referenced via `scenario.toml`.

---

### STEP 2: Create Green Agent (Evaluator) - WITHOUT Leaderboard

**Go to:** https://agentbeats.dev → Click **"Register Agent"**

#### Basic Information

**Name:** (required)
```
portfolio_evaluator
```

**Repository Link:** (required)
```
https://github.com/Rachnog/agentbeats-portfolio-assessment
```

**Docker Image:** (required)
```
ghcr.io/rachnog/portfolio-evaluator:v1.0
```

**Paper Link:** (optional)
```
https://arxiv.org/abs/1706.03762
```
(Or leave blank)

**Profile Picture URL:** (optional)
```
Leave blank
```

**Category:**
```
Finance Agent
```

**Description:**
```
Multi-criteria portfolio construction evaluator using LLM-as-judge methodology. Assesses portfolios across diversification, risk alignment, return potential, and time horizon. Evaluates 5 financial scenarios from house down payment to retirement planning.
```

---

#### ⚠️ CRITICAL: Leaderboard Config Section

**OPTION A: Leave It Blank (RECOMMENDED)**

Based on analysis of 4 working repositories, **NONE of them set leaderboard config during agent registration**. The platform likely auto-discovers from your repository structure.

**Skip all leaderboard fields:**
- GitHub Repo: **LEAVE BLANK**
- Queries (JSON): **LEAVE BLANK**

**OPTION B: Set Minimal Config (If Required)**

If the platform forces you to fill leaderboard fields:

**GitHub Repo:**
```
https://github.com/Rachnog/agentbeats-portfolio-assessment
```
(Root URL, NOT /tree/main/leaderboard)

**Queries (JSON):**
```
[]
```
(Empty array - let platform auto-discover)

---

### STEP 3: Save and Get New Agent ID

1. Click **"Register Agent"** or **"Save"**
2. **Copy the new Agent ID** (will be different from old one)
3. Note: Format will be like `019xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

### STEP 4: Update scenario.toml with New Agent ID

**Edit:** `/Users/oleksandrhonchar/Documents/GitHub/agentbeats-learning/2_initial_submission/scenario.toml`

**Change line 5:**

**FROM:**
```toml
agentbeats_id = "019bad43-ecbb-75f0-8116-7301bebaaad8"
```

**TO:**
```toml
agentbeats_id = "YOUR_NEW_AGENT_ID_HERE"
```

**Example:**
```toml
[green_agent]
agentbeats_id = "019c1234-5678-9abc-def0-123456789abc"  # NEW ID
name = "portfolio_evaluator"
env = { GOOGLE_API_KEY = "${GOOGLE_API_KEY}", EVALUATOR_MODEL = "gemini-2.0-flash", LOG_LEVEL = "INFO" }
```

---

### STEP 5: Commit and Push Updated scenario.toml

```bash
cd /Users/oleksandrhonchar/Documents/GitHub/agentbeats-learning/2_initial_submission

git add scenario.toml
git commit -m "Update green agent ID after recreation"
git push origin main
```

---

### STEP 6: Configure New Webhook

The webhook URL will change with the new agent ID.

**New Webhook URL Format:**
```
https://agentbeats.dev/api/hook/v2/YOUR_NEW_AGENT_ID
```

**Configure on GitHub:**

1. Go to: https://github.com/Rachnog/agentbeats-portfolio-assessment/settings/hooks
2. **Delete old webhook** (ID: 591035164)
3. Click **"Add webhook"**
4. **Payload URL:**
   ```
   https://agentbeats.dev/api/hook/v2/YOUR_NEW_AGENT_ID
   ```
5. **Content type:**
   ```
   application/json
   ```
6. **Events:**
   - ✅ Push events
   - ✅ Pull request events
7. **Active:** ✅ Checked
8. Click **"Add webhook"**

---

### STEP 7: Test the New Setup

1. Go to your new agent page on https://agentbeats.dev
2. **Check for leaderboard section**
3. If leaderboard section exists and shows error:
   - Click **"Request Refresh"**
   - Observe the result
4. If NO leaderboard section:
   - **This is good!** The platform is not trying to fetch leaderboard
   - Your results will still appear via webhook updates

---

## 🎯 Expected Outcomes

### Scenario A: No Leaderboard Section (BEST)

If the agent page **doesn't have a leaderboard section**:
- ✅ This is good!
- ✅ Platform won't try to fetch leaderboard
- ✅ Results tracked via webhook
- ✅ Agent assessments work normally

### Scenario B: Leaderboard Works

If leaderboard section exists and refreshes successfully:
- ✅ Platform reads from your results files
- ✅ Displays rankings
- ✅ No errors

### Scenario C: Still Shows Error

If you still get leaderboard fetch error:
- The platform requires specific leaderboard format
- Contact AgentBeats support on Discord
- Explain: "Working repos don't have leaderboard config, but platform requires it. What format is needed?"

---

## 📝 What About the Purple Agent?

**You don't need to register the purple agent separately!**

The purple agent (portfolio_constructor) is:
- ✅ Defined in `scenario.toml` as `[[participants]]`
- ✅ Docker image already published: `ghcr.io/rachnog/portfolio-constructor:v1.0`
- ✅ Referenced by green agent during evaluations
- ✅ No separate platform registration needed

---

## 🔄 Alternative: Keep Existing Agent, Contact Support

Instead of recreating, you could:

1. **Keep current agent ID**
2. **Contact AgentBeats support** via:
   - Discord: #portfolio-construction-track
   - Email: support@agentbeats.dev
3. **Ask them to:**
   - Reset leaderboard configuration for agent `019bad43-ecbb-75f0-8116-7301bebaaad8`
   - Or explain what leaderboard format is required
   - Or why it's failing to fetch from valid public repository

**Share with them:**
- Your agent ID: `019bad43-ecbb-75f0-8116-7301bebaaad8`
- Repository: `https://github.com/Rachnog/agentbeats-portfolio-assessment`
- Error: "Failed to fetch from .../leaderboard"
- Note: Repository is public, files are accessible, format matches working examples

---

## 📊 Checklist After Recreation

### New Agent Registration
- [ ] Deleted old agent
- [ ] Created new agent without leaderboard config
- [ ] Copied new agent ID
- [ ] Updated scenario.toml with new ID
- [ ] Committed and pushed changes
- [ ] Configured new webhook
- [ ] Tested new agent page (no leaderboard error)

### If Leaderboard Still Required
- [ ] Contacted AgentBeats support
- [ ] Got clarification on leaderboard format
- [ ] Updated configuration based on guidance

---

## 🎬 Next Steps After Recreation

Once the new agent is working (with or without leaderboard):

### 1. Record Demo Video (2-5 minutes)
- Show GitHub repository
- Demonstrate assessment workflow
- Explain evaluation criteria
- Highlight results from one scenario

**Script:** Already prepared in `DEMO_VIDEO_SCRIPT.md`

### 2. Submit Competition Form
**URL:** https://docs.google.com/forms/d/e/1FAIpQLSdtqxWcGl2Qg5RPuNF2O3_N07uD0HMJpWBCwZWZbD3dxTuWmg/viewform

**Information to provide:**
- Track: Finance Agents
- Purple Agent: `ghcr.io/rachnog/portfolio-constructor:v1.0`
- Green Agent: `ghcr.io/rachnog/portfolio-evaluator:v1.0`
- **Green Agent ID:** YOUR_NEW_AGENT_ID (from step 3)
- GitHub: `https://github.com/Rachnog/agentbeats-portfolio-assessment`
- Demo Video: [YouTube URL]

---

## 💡 Key Insights

### What We Learned

1. **Working repositories analyzed:**
   - Froot-NetSys/netarena_leaderboard
   - nprakash-star/meta-ml-titanic-leaderboard
   - vanessadiehl/agentify-bench
   - vanessadiehl/agentify-bench-leaderboard

2. **Common pattern:**
   - ✅ All have `results/` directory with timestamped JSON files
   - ✅ All have proper top-level wrapper in results: `{participants, timestamp, results}`
   - ✅ All have `scenario.toml` with green_agent section
   - ❌ NONE have visible leaderboard config causing issues

3. **Your repository:**
   - ✅ Structure matches working examples
   - ✅ Result format corrected
   - ✅ All files accessible
   - ❓ Platform configuration might have cached bad state

---

## 🚀 Success Criteria

You'll know it's working when:

**Option A: No Leaderboard Section**
- Agent page loads without leaderboard section
- No fetch errors
- Webhook reports successful triggers
- Assessment results appear in activity feed

**Option B: Working Leaderboard**
- Leaderboard section exists
- "Request Refresh" succeeds
- Rankings display from your results files
- No fetch errors

**Either outcome is success!** The important thing is no errors blocking your submission.

---

## 📞 Support Contacts

If recreation doesn't resolve the issue:

**AgentBeats Discord:**
- Server: https://discord.gg/agentbeats
- Channel: #portfolio-construction-track
- Ask: Platform team or community

**AgentBeats Support:**
- Website: https://agentbeats.dev
- Docs: https://docs.agentbeats.dev

**Your Situation:**
- Agent recreation didn't resolve leaderboard fetch error
- Repository is public and all files are accessible
- Format matches working examples
- Need guidance on required leaderboard configuration

---

## ✅ Final Recommendation

**Try recreation first (Steps 1-7 above).** If that doesn't work within 10-15 minutes, **contact AgentBeats support** - they can likely resolve this faster than further troubleshooting.

Your repository and code are correct. This is a platform configuration issue at this point.

Good luck! 🚀
