# Approximate USD cost per 1,000 tokens. This is NOT guaranteed to match current provider
# pricing exactly — update these constants when a provider changes pricing. This exists for
# internal budget estimation and dashboards only; it is not a source of truth for billing.
PRICING_PER_1K_TOKENS = {
    ("anthropic", "claude-sonnet-4-6"): {"prompt": 0.003, "completion": 0.015},
    ("openai", "gpt-4o"): {"prompt": 0.0025, "completion": 0.010},
}


def estimate_cost_usd(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = PRICING_PER_1K_TOKENS.get((provider, model))
    if rates is None:
        return 0.0
    return (prompt_tokens / 1000) * rates["prompt"] + (completion_tokens / 1000) * rates["completion"]