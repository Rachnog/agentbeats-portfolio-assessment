# Contributing to Portfolio Construction Assessment

Thank you for your interest in contributing to this AgentBeats Finance Agent Track submission!

## 🎯 Project Overview

This repository implements a two-agent portfolio construction assessment system:
- **Purple Agent (Constructor)**: Generates investment portfolios based on financial goals
- **Green Agent (Evaluator)**: Evaluates portfolio quality across multiple criteria

## 📋 Ways to Contribute

### 1. Improve Portfolio Construction Logic
- Enhance asset allocation algorithms in `deployment/portfolio_constructor.py`
- Add new portfolio strategies (value, growth, dividend-focused, ESG, etc.)
- Improve risk-return optimization
- Implement dynamic rebalancing strategies

### 2. Enhance Evaluation Criteria
- Add new evaluation metrics in `deployment/portfolio_evaluator.py`
- Improve scoring algorithms (diversification, risk alignment, return potential)
- Add scenario-specific evaluation logic
- Implement backtesting capabilities

### 3. Expand Test Scenarios
- Add new financial scenarios in `scenario.toml`
- Cover edge cases (market crashes, inflation spikes, etc.)
- Add international investment scenarios
- Include crypto/alternative asset scenarios

### 4. Improve Documentation
- Enhance README sections
- Add code comments and docstrings
- Create tutorials or guides
- Document evaluation methodology

### 5. Add Tests
- Create A2A conformance tests
- Add unit tests for portfolio logic
- Implement integration tests
- Add performance benchmarks

## 🛠️ Development Setup

### Prerequisites
- Python 3.11 or higher
- Docker and Docker Compose
- Google API key (for Gemini 2.0 Flash)
- Git

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rachnog/agentbeats-portfolio-assessment.git
   cd agentbeats-portfolio-assessment
   ```

2. **Install dependencies:**
   ```bash
   # Using pip
   pip install -r deployment/requirements.txt

   # Or using the new pyproject.toml
   pip install -e .
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

4. **Run agents locally:**
   ```bash
   # Purple agent (Constructor)
   cd deployment
   python portfolio_constructor.py --host 0.0.0.0 --port 9019

   # Green agent (Evaluator) - in another terminal
   python portfolio_evaluator.py --host 0.0.0.0 --port 9009
   ```

5. **Test the integration:**
   ```bash
   # Run assessment workflow
   python .github/workflows/assessment_script.py
   ```

## 📝 Contribution Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints where applicable
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Commit Messages
Use conventional commit format:
```
<type>(<scope>): <subject>

<body>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(constructor): add ESG-focused portfolio strategy
fix(evaluator): correct diversification score calculation
docs(readme): add installation troubleshooting section
```

### Pull Request Process

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Test your changes:**
   ```bash
   # Run local tests
   pytest tests/

   # Test Docker builds
   docker build -f deployment/Dockerfile.purple -t test-purple .
   docker build -f deployment/Dockerfile.green -t test-green .
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat(scope): descriptive message"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** with:
   - Clear title describing the change
   - Detailed description of what and why
   - Link to any related issues
   - Screenshots or examples (if UI/output changes)
   - Test results

### Review Process
- All PRs require at least one approval
- CI checks must pass (GitHub Actions)
- Code must follow style guidelines
- Documentation must be updated for user-facing changes

## 🧪 Testing

### Running Tests Locally
```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=deployment --cov-report=html

# Run A2A conformance tests
pytest tests/test_a2a_conformance.py
```

### Adding New Tests
Place tests in `tests/` directory:
```python
# tests/test_portfolio_constructor.py
import pytest
from deployment.portfolio_constructor import construct_portfolio

def test_moderate_risk_allocation():
    goal = "Save $50k in 5 years, moderate risk"
    portfolio = construct_portfolio(goal)
    assert 40 <= portfolio["equity_allocation"] <= 80
```

## 🐛 Reporting Issues

### Bug Reports
Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages or logs
- Screenshots (if applicable)

### Feature Requests
Include:
- Use case and motivation
- Proposed solution or approach
- Alternative solutions considered
- Impact on existing functionality

## 📚 Resources

### AgentBeats Documentation
- **Main Docs**: https://docs.agentbeats.dev
- **A2A Protocol**: https://docs.agentbeats.dev/a2a-protocol
- **Finance Track**: https://docs.agentbeats.dev/tracks/finance

### Related Projects
- **Official Template**: https://github.com/RDI-Foundation/agent-template
- **A2A SDK**: https://github.com/agentbeats/a2a-sdk
- **Google ADK**: https://github.com/google/adk

### Financial Portfolio Theory
- Modern Portfolio Theory (MPT)
- Capital Asset Pricing Model (CAPM)
- Efficient Frontier optimization
- Risk-adjusted returns (Sharpe ratio)

## 🔐 Security

- **Never commit API keys** or secrets to the repository
- Use environment variables or `.env` files (gitignored)
- Report security vulnerabilities privately via GitHub Security Advisories
- Follow secure coding practices (input validation, error handling)

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project is part of the AgentBeats Finance Agent Track competition. We appreciate:
- The AgentBeats team for the platform
- Google for the Gemini 2.0 Flash model
- The A2A protocol contributors
- All community contributors

## 📞 Questions?

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Discord**: #portfolio-construction-track channel
- **Email**: rachnog@gmail.com

---

Thank you for contributing to better portfolio construction agents! 🚀
