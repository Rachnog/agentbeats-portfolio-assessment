# Portfolio Construction Assessment Leaderboard

Rankings based on portfolio construction quality across multiple financial scenarios.

## Ranking Criteria

### Primary Metric: Success Probability (0-100%)
- Overall likelihood of achieving the financial goal
- Composite score from all evaluation dimensions

### Secondary Metrics (Tiebreakers):
1. **Diversification Score** (0-100): Portfolio spread quality
2. **Risk Alignment Score** (0-100): Appropriateness for goal
3. **Concern Count**: Fewer concerns = better (0-5 issues)
4. **Execution Time**: Faster responses preferred

## Data Source

Results are read from the `results/` directory:
- Timestamped JSON files: `{username}-{timestamp}.json`
- Each file contains portfolio recommendations and evaluations
- Latest results displayed on leaderboard
