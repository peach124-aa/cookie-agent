"""Metrics collection for PPO algorithm."""


def compute_approx_kl(log_probs: list[float], old_log_probs: list[float]) -> float:
    """Compute the approximate KL divergence between current and old policy.

    Using the approximation: KL ~ (old_log_prob - log_prob).mean()

    Args:
        log_probs: Log probabilities of actions under current policy.
        old_log_probs: Log probabilities of actions under old policy.

    Returns:
        The approximate KL divergence scalar.
    """
    if not log_probs:
        return 0.0

    diffs = [olp - lp for lp, olp in zip(log_probs, old_log_probs)]
    return sum(diffs) / len(diffs)


def compute_clip_fraction(
    log_probs: list[float],
    old_log_probs: list[float],
    epsilon: float,
) -> float:
    """Compute the fraction of policy ratio updates that were clipped.

    Args:
        log_probs: Log probabilities of actions under current policy.
        old_log_probs: Log probabilities of actions under old policy.
        epsilon: PPO clipping parameter.

    Returns:
        Fraction of elements where ratio was clipped (between 0.0 and 1.0).
    """
    if not log_probs:
        return 0.0

    clipped_count = 0
    from cookie_agent.rl.losses import clip_ratio
    
    ratios = clip_ratio(log_probs, old_log_probs)
    for ratio in ratios:
        if ratio < (1.0 - epsilon) or ratio > (1.0 + epsilon):
            clipped_count += 1

    return clipped_count / len(ratios)
