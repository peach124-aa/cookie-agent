"""Unit tests for the pure Python PPO algorithm."""

import math

from cookie_agent.rl.advantage import compute_gae
from cookie_agent.rl.losses import (
    clip_ratio,
    compute_entropy_bonus,
    compute_policy_loss,
    compute_value_loss,
)
from cookie_agent.rl.metrics import compute_approx_kl, compute_clip_fraction
from cookie_agent.rl.ppo import PPOAlgorithm
from cookie_agent.rl.returns import compute_discounted_returns


def test_compute_discounted_returns() -> None:
    """Verify reverse discounting calculation."""
    rewards = [1.0, 1.0, 1.0]
    gamma = 0.9
    returns = compute_discounted_returns(rewards, gamma)

    # R_2 = 1.0
    # R_1 = 1.0 + 0.9 * 1.0 = 1.9
    # R_0 = 1.0 + 0.9 * 1.9 = 2.71
    assert math.isclose(returns[2], 1.0)
    assert math.isclose(returns[1], 1.9)
    assert math.isclose(returns[0], 2.71)


def test_compute_gae() -> None:
    """Verify Generalized Advantage Estimation logic."""
    rewards = [1.0, -1.0, 1.0]
    values = [0.5, 0.5, 0.5]
    dones = [False, False, True]
    gamma = 0.99
    lambda_ = 0.95

    advs, rets = compute_gae(rewards, values, dones, gamma, lambda_)

    assert len(advs) == 3
    assert len(rets) == 3
    # Step 2: terminal state, next_value = 0, delta = 1.0 + 0 - 0.5 = 0.5
    # adv = 0.5, ret = 1.0
    assert math.isclose(advs[2], 0.5)
    assert math.isclose(rets[2], 1.0)


def test_clip_ratio() -> None:
    """Verify exponentiated log probability ratios."""
    log_probs = [math.log(0.5), math.log(0.8)]
    old_log_probs = [math.log(0.25), math.log(0.4)]
    ratios = clip_ratio(log_probs, old_log_probs)

    assert math.isclose(ratios[0], 2.0)
    assert math.isclose(ratios[1], 2.0)


def test_compute_policy_loss() -> None:
    """Verify clipped surrogate objective."""
    advantages = [1.0, -1.0]
    log_probs = [math.log(0.4), math.log(0.4)]
    old_log_probs = [math.log(0.2), math.log(0.2)]
    # ratio = 2.0 for both
    epsilon = 0.2

    # For adv=1.0:
    # surr1 = 2.0 * 1.0 = 2.0
    # surr2 = min(2.0, 1.2) * 1.0 = 1.2
    # loss = -min(2.0, 1.2) = -1.2

    # For adv=-1.0:
    # surr1 = 2.0 * -1.0 = -2.0
    # surr2 = max(0.8, min(2.0, 1.2)) * -1.0 = 1.2 * -1.0 = -1.2
    # (Wait, clip(ratio, 0.8, 1.2) = 1.2 -> 1.2 * -1 = -1.2)
    # Actually, ratio=2.0 is clipped to 1.2.
    # surr2 = 1.2 * -1.0 = -1.2
    # min(-2.0, -1.2) = -2.0
    # loss = --2.0 = 2.0 ? Wait.
    # The loss function negates min(surr1, surr2).

    loss = compute_policy_loss(advantages, log_probs, old_log_probs, epsilon)
    # Mean of -1.2 and 2.0 = 0.4
    assert math.isclose(loss, 0.4)


def test_empty_lists() -> None:
    """Verify robust handling of empty sequences."""
    assert compute_policy_loss([], [], [], 0.2) == 0.0
    assert compute_value_loss([], []) == 0.0
    assert compute_entropy_bonus([], 0.01) == 0.0
    assert compute_approx_kl([], []) == 0.0
    assert compute_clip_fraction([], [], 0.2) == 0.0


def test_compute_value_loss() -> None:
    """Verify Mean Squared Error."""
    values = [0.0, 1.0, -1.0]
    returns = [1.0, 1.0, 2.0]
    # sq_errors = [1.0, 0.0, 9.0], sum = 10.0, mean = 3.333...
    loss = compute_value_loss(values, returns)
    assert math.isclose(loss, 10.0 / 3.0)


def test_compute_entropy_bonus() -> None:
    """Verify entropy scaling."""
    entropies = [1.0, 2.0, 3.0]
    # mean = 2.0
    # c = 0.1, loss = -0.2
    loss = compute_entropy_bonus(entropies, 0.1)
    assert math.isclose(loss, -0.2)


def test_compute_approx_kl() -> None:
    """Verify KL approximation."""
    log_probs = [0.5, 0.2]
    old_log_probs = [0.6, 0.4]
    # diffs = [0.1, 0.2], sum = 0.3, mean = 0.15
    kl = compute_approx_kl(log_probs, old_log_probs)
    assert math.isclose(kl, 0.15)


def test_compute_clip_fraction() -> None:
    """Verify clip fraction metric."""
    # ratios = exp(log_prob - old_log_prob)
    # 0 -> exp(0) = 1.0 (not clipped for eps 0.2)
    # ln(2.0) -> 2.0 (clipped for eps 0.2)
    log_probs = [0.0, math.log(2.0)]
    old_log_probs = [0.0, 0.0]

    frac = compute_clip_fraction(log_probs, old_log_probs, 0.2)
    assert math.isclose(frac, 0.5)


def test_ppo_algorithm() -> None:
    """Verify orchestration of all metrics and losses in PPOAlgorithm."""
    algo = PPOAlgorithm(
        gamma=0.9, lambda_=0.95, epsilon=0.2, value_coef=0.5, entropy_coef=0.1
    )

    # Minimal mock data
    rewards = [1.0]
    values = [0.5]
    dones = [True]
    log_probs = [math.log(0.4)]
    old_log_probs = [math.log(0.2)]
    entropies = [0.5]

    advs, rets = algo.compute_advantages(rewards, values, dones)
    # step 0: next_v=0, mask=0. delta = 1.0 + 0 - 0.5 = 0.5
    assert advs == [0.5]
    assert rets == [1.0]

    res = algo.compute_losses(advs, rets, values, log_probs, old_log_probs, entropies)

    # ratio = 2.0
    # surr1 = 1.0
    # surr2 = min(2.0, 1.2) * 0.5 = 0.6
    # policy_loss = -0.6
    assert math.isclose(res.policy_loss, -0.6)

    # val_loss = (0.5 - 1.0)^2 = 0.25
    assert math.isclose(res.value_loss, 0.25)

    # ent = -0.1 * 0.5 = -0.05
    assert math.isclose(res.entropy_loss, -0.05)

    # total = -0.6 + 0.5(0.25) - 0.05 = -0.6 + 0.125 - 0.05 = -0.525
    assert math.isclose(res.total_loss, -0.525)

    assert res.clip_fraction == 1.0
