"""PPO Algorithm Orchestrator."""

from dataclasses import dataclass

from cookie_agent.rl.advantage import compute_gae
from cookie_agent.rl.losses import (
    compute_entropy_bonus,
    compute_policy_loss,
    compute_value_loss,
)
from cookie_agent.rl.metrics import compute_approx_kl, compute_clip_fraction


@dataclass
class PPOLossResult:
    """Container for computed PPO loss components."""
    policy_loss: float
    value_loss: float
    entropy_loss: float
    total_loss: float
    approx_kl: float
    clip_fraction: float


class PPOAlgorithm:
    """Coordinates PPO mathematical functions over sequences of scalars.
    
    This class does not optimize, own parameters, or update neural networks.
    It strictly orchestrates the pure Python math functions for the algorithm.
    """

    def __init__(
        self,
        gamma: float = 0.99,
        lambda_: float = 0.95,
        epsilon: float = 0.2,
        value_coef: float = 0.5,
        entropy_coef: float = 0.01,
    ) -> None:
        """Initialize PPO hyperparameters.
        
        Args:
            gamma: Discount factor.
            lambda_: GAE smoothing parameter.
            epsilon: Clipping parameter for surrogate objective.
            value_coef: Weight multiplier for the value loss.
            entropy_coef: Weight multiplier for the entropy bonus.
        """
        self.gamma = gamma
        self.lambda_ = lambda_
        self.epsilon = epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef

    def compute_advantages(
        self,
        rewards: list[float],
        values: list[float],
        dones: list[bool],
    ) -> tuple[list[float], list[float]]:
        """Compute GAE advantages and target returns.
        
        Args:
            rewards: Scalar rewards sequence.
            values: State value estimates sequence.
            dones: Episode termination flags sequence.
            
        Returns:
            Tuple of (advantages, returns).
        """
        return compute_gae(
            rewards=rewards,
            values=values,
            dones=dones,
            gamma=self.gamma,
            lambda_=self.lambda_,
        )

    def compute_losses(
        self,
        advantages: list[float],
        returns: list[float],
        values: list[float],
        log_probs: list[float],
        old_log_probs: list[float],
        entropies: list[float],
    ) -> PPOLossResult:
        """Compute the full set of PPO losses and metrics for a batch.
        
        Args:
            advantages: Computed GAE advantages.
            returns: Computed target returns.
            values: Current value estimates.
            log_probs: Current policy log probabilities.
            old_log_probs: Previous policy log probabilities.
            entropies: Policy entropies.
            
        Returns:
            PPOLossResult containing separated components and metrics.
        """
        # Calculate core losses
        policy_loss = compute_policy_loss(
            advantages, log_probs, old_log_probs, self.epsilon
        )
        value_loss = compute_value_loss(values, returns)
        entropy_loss = compute_entropy_bonus(entropies, self.entropy_coef)
        
        total_loss = policy_loss + (self.value_coef * value_loss) + entropy_loss
        
        # Calculate metrics
        approx_kl = compute_approx_kl(log_probs, old_log_probs)
        clip_frac = compute_clip_fraction(log_probs, old_log_probs, self.epsilon)

        return PPOLossResult(
            policy_loss=policy_loss,
            value_loss=value_loss,
            entropy_loss=entropy_loss,
            total_loss=total_loss,
            approx_kl=approx_kl,
            clip_fraction=clip_frac,
        )
