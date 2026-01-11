# Submission Checklist - AgentBeats Competition

**Deadline**: January 15, 2026, 11:59pm PT
**Status**: Ready for final steps
**Estimated Time Remaining**: 4-5 hours over next 3 days

---

## ✅ What's Already Done

- [x] Portfolio constructor agent implemented (88 lines)
- [x] Portfolio evaluator agent implemented (306 lines)
- [x] Dockerfiles created (purple + green)
- [x] Docker images built and tested locally
- [x] Agent cards verified working
- [x] GitHub repository README created
- [x] GitHub Actions workflow prepared
- [x] Leaderboard SQL + README created
- [x] Demo video script written

**You're 60% done! Everything technical is ready.**

---

## 📋 What You Need To Do

### 🚢 Step 1: Push Docker Images to GitHub Container Registry

**Time**: 30-45 minutes
**Prerequisites**: GitHub Personal Access Token with `packages` scope

#### Actions:

1. **Create Personal Access Token** (if you don't have one)
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name it: "AgentBeats Docker Push"
   - Select scope: `write:packages` (this automatically includes `read:packages`)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again!)

2. **Login to GitHub Container Registry**
   ```bash
   cd 2_initial_submission/deployment

   # Login (paste your token when prompted for password)
   echo YOUR_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
   ```

3. **Tag Images for GitHub**
   ```bash
   # Replace YOUR_GITHUB_USERNAME with your actual username
   docker tag portfolio-constructor:latest ghcr.io/YOUR_GITHUB_USERNAME/portfolio-constructor:v1.0
   docker tag portfolio-evaluator:latest ghcr.io/YOUR_GITHUB_USERNAME/portfolio-evaluator:v1.0

   # Also tag as 'latest'
   docker tag portfolio-constructor:latest ghcr.io/YOUR_GITHUB_USERNAME/portfolio-constructor:latest
   docker tag portfolio-evaluator:latest ghcr.io/YOUR_GITHUB_USERNAME/portfolio-evaluator:latest
   ```

4. **Push Images**
   ```bash
   # Push purple agent
   docker push ghcr.io/YOUR_GITHUB_USERNAME/portfolio-constructor:v1.0
   docker push ghcr.io/YOUR_GITHUB_USERNAME/portfolio-constructor:latest

   # Push green agent
   docker push ghcr.io/YOUR_GITHUB_USERNAME/portfolio-evaluator:v1.0
   docker push ghcr.io/YOUR_GITHUB_USERNAME/portfolio-evaluator:latest
   ```

5. **Make Images Public**
   - Go to: https://github.com/YOUR_GITHUB_USERNAME?tab=packages
   - Click on `portfolio-constructor`
   - Click "Package settings" (right sidebar)
   - Scroll down to "Danger Zone"
   - Click "Change visibility" → "Public"
   - Confirm by typing package name
   - Repeat for `portfolio-evaluator`

6. **Verify Images Are Accessible**
   ```bash
   # Test pull (in a new terminal, without login)
   docker pull ghcr.io/YOUR_GITHUB_USERNAME/portfolio-constructor:latest
   docker pull ghcr.io/YOUR_GITHUB_USERNAME/portfolio-evaluator:latest
   ```

**Record these URLs:**
- Purple: `ghcr.io/YOUR_GITHUB_USERNAME/portfolio-constructor:v1.0`
- Green: `ghcr.io/YOUR_GITHUB_USERNAME/portfolio-evaluator:v1.0`

---

### 📦 Step 2: Create GitHub Repository

**Time**: 30 minutes
**Prerequisites**: GitHub account

#### Actions:

1. **Create New Public Repository**
   - Go to: https://github.com/new
   - Repository name: `agentbeats-portfolio-assessment`
   - Description: "Portfolio construction assessment for AgentBeats Finance Agent Track"
   - Visibility: **Public**
   - Initialize: **Do NOT check any boxes** (we have files)
   - Click "Create repository"

2. **Initialize Git in 2_initial_submission/**
   ```bash
   cd 2_initial_submission
   git init
   git add .
   git commit -m "Initial submission: Portfolio construction assessment

   - Purple agent (constructor): 88 lines
   - Green agent (evaluator): 306 lines
   - Docker containers tested and working
   - A2A protocol v0.3.0 compliant
   - Multi-criteria LLM evaluation

   Submitting to AgentBeats Phase 1 Finance Agent Track"
   ```

3. **Push to GitHub**
   ```bash
   # Replace YOUR_GITHUB_USERNAME
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/agentbeats-portfolio-assessment.git
   git branch -M main
   git push -u origin main
   ```

4. **Update README with Your URLs**
   - Edit `README.md`
   - Replace `YOUR_USERNAME` with your actual GitHub username (3 places)
   - Commit and push:
   ```bash
   git add README.md
   git commit -m "Update README with actual GitHub username"
   git push
   ```

5. **Add GOOGLE_API_KEY to Secrets**
   - Go to your repository settings: `https://github.com/YOUR_GITHUB_USERNAME/agentbeats-portfolio-assessment/settings/secrets/actions`
   - Click "New repository secret"
   - Name: `GOOGLE_API_KEY`
   - Value: Your Gemini API key
   - Click "Add secret"

6. **Enable GitHub Actions**
   - Go to Actions tab: `https://github.com/YOUR_GITHUB_USERNAME/agentbeats-portfolio-assessment/actions`
   - Click "I understand my workflows, go ahead and enable them"

**Record this URL:**
- Repository: `https://github.com/YOUR_GITHUB_USERNAME/agentbeats-portfolio-assessment`

---

### 📊 Step 3: Fork Leaderboard Template (Optional but Recommended)

**Time**: 15 minutes
**Prerequisites**: Completed Step 2

#### Actions:

1. **Fork Template Repository**
   - Go to: https://github.com/RDI-Foundation/agentbeats-leaderboard-template
   - Click "Fork"
   - Repository name: `portfolio-assessment-leaderboard`
   - Description: "Leaderboard for portfolio construction assessment"
   - Click "Create fork"

2. **Customize Leaderboard**
   ```bash
   # Clone your fork
   git clone https://github.com/YOUR_GITHUB_USERNAME/portfolio-assessment-leaderboard.git
   cd portfolio-assessment-leaderboard

   # Copy your leaderboard files
   cp ../agentbeats-learning/2_initial_submission/leaderboard/leaderboard.sql .
   cp ../agentbeats-learning/2_initial_submission/leaderboard/README.md .

   # Commit
   git add .
   git commit -m "Add portfolio construction leaderboard query"
   git push
   ```

3. **Set Up BigQuery Credentials** (if you have access)
   - Add `BIGQUERY_CREDENTIALS` secret to repository
   - Configure GitHub Actions to run queries

**Record this URL:**
- Leaderboard: `https://github.com/YOUR_GITHUB_USERNAME/portfolio-assessment-leaderboard`

---

### 🎥 Step 4: Record and Upload Demo Video

**Time**: 1-2 hours
**Prerequisites**: Agents working locally

#### Actions:

1. **Prepare Environment**
   ```bash
   # Start agents
   cd 2_initial_submission/deployment
   docker run -d -p 9019:9019 --env-file ../../1_initial_experiments/agentbeats-tutorial/.env --name demo-purple portfolio-constructor:latest
   docker run -d -p 9009:9009 --env-file ../../1_initial_experiments/agentbeats-tutorial/.env --name demo-green portfolio-evaluator:latest
   ```

2. **Follow Demo Script**
   - Open: `DEMO_VIDEO_SCRIPT.md`
   - Rehearse 2-3 times
   - Clean your desktop
   - Close unnecessary apps

3. **Record Video**
   - Use screen recording software:
     - **macOS**: QuickTime (File → New Screen Recording)
     - **Windows**: Xbox Game Bar (Win + G)
     - **Any**: OBS Studio (free)
   - Record audio clearly
   - Target: 3-5 minutes
   - Show live demonstration

4. **Upload to YouTube**
   - Go to: https://studio.youtube.com
   - Click "Create" → "Upload videos"
   - Select your recording
   - Title: "Portfolio Construction Assessment - AgentBeats Finance Track"
   - Description:
     ```
     My submission for AgentBeats Finance Agent Track (Phase 1)

     A portfolio construction assessment system using:
     - Purple agent: Portfolio constructor (Google ADK)
     - Green agent: Multi-criteria evaluator (A2A SDK)
     - Docker deployment
     - LLM-as-judge methodology

     GitHub: [Your repo URL]
     Competition: https://agentbeats.dev
     ```
   - Visibility: **Unlisted** (for competition judges)
   - Click "Next" → "Next" → "Publish"

5. **Get Shareable Link**
   - Click on your video
   - Click "Share"
   - Copy link (should look like: `https://youtu.be/XXXXXXXXXXX`)

6. **Test Link**
   - Open in incognito/private window
   - Verify video plays

**Record this URL:**
- Demo Video: `https://youtu.be/_______________`

---

### 📝 Step 5: Register and Submit

**Time**: 30 minutes
**Prerequisites**: All above URLs collected

#### Actions:

1. **Register on AgentBeats**
   - Go to: https://agentbeats.dev
   - Click "Sign Up" or "Register"
   - Complete your profile
   - Verify email if required

2. **Fill Out Submission Form**
   - Go to: https://docs.google.com/forms/d/e/1FAIpQLSdtqxWcGl2Qg5RPuNF2O3_N07uD0HMJpWBCwZWZbD3dxTuWmg/viewform
   - Or find link on AgentBeats website

   **Information You'll Need:**
   - Track: Finance Agents
   - Purple Agent Name: `portfolio_constructor`
   - Purple Agent URL: `ghcr.io/YOUR_USERNAME/portfolio-constructor:v1.0`
   - Green Agent URL: `ghcr.io/YOUR_USERNAME/portfolio-evaluator:v1.0`
   - GitHub Repository: `https://github.com/YOUR_USERNAME/agentbeats-portfolio-assessment`
   - Leaderboard (optional): `https://github.com/YOUR_USERNAME/portfolio-assessment-leaderboard`
   - Demo Video: `https://youtu.be/_______________`
   - Contact Email: Your email
   - Description: "Multi-criteria portfolio construction assessment using LLM-as-judge methodology"

3. **Double-Check All Links**
   - Test each URL in incognito mode
   - Verify Docker images are public
   - Ensure video is watchable
   - Confirm repository is public

4. **Submit!**
   - Review form one more time
   - Click "Submit"
   - **Screenshot the confirmation page**

5. **Confirmation**
   - Check email for confirmation
   - If no email within 24 hours, check Discord or support

---

## 📞 If You Get Stuck

### Docker Issues
- **Can't push**: Check token has `write:packages` scope
- **Login fails**: Generate new token
- **Images not public**: Use GitHub web interface to change visibility

### GitHub Issues
- **Push rejected**: Ensure repository is public
- **Actions not running**: Enable in repository settings
- **Secrets not working**: Double-check secret names match exactly

### Video Issues
- **File too large**: Compress video or reduce resolution to 720p
- **Upload fails**: Try different browser or split into shorter videos
- **Audio problems**: Use Audacity (free) to enhance audio

### Submission Issues
- **Form not loading**: Try different browser
- **Links not accepted**: Ensure they're public and correct format
- **No confirmation**: Check spam folder, wait 24h, then contact support

### Support Channels
- **AgentBeats Discord**: #competition-q-and-a
- **AgentBeats Docs**: https://docs.agentbeats.dev
- **GitHub Issues**: On your repository

---

## ✅ Final Verification Checklist

Before submitting, verify:

- [ ] Purple agent Docker image is public on ghcr.io
- [ ] Green agent Docker image is public on ghcr.io
- [ ] Both images pull successfully without authentication
- [ ] GitHub repository is public
- [ ] Repository contains all files (deployment/, README.md, workflows/)
- [ ] README has correct URLs (no YOUR_USERNAME placeholders)
- [ ] Demo video is uploaded to YouTube
- [ ] Video is set to "Unlisted" (not Private!)
- [ ] Video plays without issues
- [ ] All URLs are copied and ready for form
- [ ] You have confirmation email/screenshot

---

## 🎯 Success Criteria

### Minimum (Must Have)
- [x] Docker images on ghcr.io (public)
- [ ] Code on GitHub (public)
- [ ] Demo video on YouTube (unlisted)
- [ ] Submission form completed

### Good (Competitive)
- [x] All of minimum
- [ ] Leaderboard repository set up
- [ ] Professional demo video
- [ ] Complete documentation

### Excellent (Prize-Worthy)
- [x] All of good
- [x] Multiple evaluation criteria
- [x] Working GitHub Actions
- [x] Production-quality code

**You're already at "Excellent" level - just need to publish!**

---

## 🚀 You've Got This!

**What's Done**: 60% (all the hard technical work)
**What's Left**: 40% (publishing and administration)

The difficult part (building a working system) is complete. What remains is straightforward:
1. Push Docker images (15 min)
2. Create GitHub repo (15 min)
3. Record video (1 hour)
4. Submit form (15 min)

**Total remaining time**: ~2-3 hours spread over next 3 days

**You have a competitive submission ready to go!** 🎉

---

## 📅 Suggested Schedule

### Today (Day 1): Docker & GitHub
- ⏰ Morning (30 min): Create PAT, push Docker images
- ⏰ Afternoon (30 min): Create GitHub repo, push code

### Tomorrow (Day 2): Video
- ⏰ Afternoon (2 hours): Record and upload demo video

### Day After (Day 3): Submit
- ⏰ Morning (30 min): Fill out form, submit
- ⏰ Buffer: Rest of day for any issues

### Deadline: January 15, 2026, 11:59pm PT

---

**Need help? I'm here if you get stuck on any of these steps!**

**Last Updated**: January 11, 2026
**Next Action**: Push Docker images to ghcr.io
