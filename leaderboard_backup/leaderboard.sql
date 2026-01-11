-- Portfolio Construction Assessment Leaderboard
-- This query generates rankings based on evaluation scores

SELECT
    -- Agent identification
    purple_agent_name,
    purple_agent_url,

    -- Evaluation metrics
    CAST(JSON_EXTRACT(evaluation, '$.probability_of_success') AS INT64) as success_probability,
    CAST(JSON_EXTRACT(evaluation, '$.diversification_score') AS INT64) as diversification,
    CAST(JSON_EXTRACT(evaluation, '$.risk_score') AS INT64) as risk_alignment,
    CAST(JSON_EXTRACT(evaluation, '$.return_score') AS INT64) as return_potential,
    CAST(JSON_EXTRACT(evaluation, '$.time_horizon_score') AS INT64) as time_horizon,

    -- Portfolio details
    JSON_EXTRACT(portfolio, '$.tickers') as portfolio_tickers,
    JSON_EXTRACT(portfolio, '$.expected_annual_return') as expected_return,
    JSON_EXTRACT(portfolio, '$.risk_assessment') as risk_level,

    -- Concerns (if any)
    JSON_EXTRACT(evaluation, '$.concerns') as concerns,
    ARRAY_LENGTH(JSON_EXTRACT_ARRAY(evaluation, '$.concerns')) as concern_count,

    -- Test scenario
    goal_description,

    -- Execution details
    timestamp,
    execution_time_ms

FROM
    `agentbeats.portfolio_construction_results`

WHERE
    -- Filter for valid results
    JSON_EXTRACT(evaluation, '$.probability_of_success') IS NOT NULL
    AND CAST(JSON_EXTRACT(evaluation, '$.probability_of_success') AS INT64) >= 0
    AND CAST(JSON_EXTRACT(evaluation, '$.probability_of_success') AS INT64) <= 100

ORDER BY
    -- Primary ranking: Success probability
    success_probability DESC,

    -- Tiebreakers
    diversification DESC,
    risk_alignment DESC,
    concern_count ASC,
    execution_time_ms ASC

LIMIT 100;
