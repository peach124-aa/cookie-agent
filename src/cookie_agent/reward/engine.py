"""Default implementation of the Reward Strategy protocol."""

from collections.abc import Sequence

from cookie_agent.core.protocols import RewardStrategy
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState
from cookie_agent.reward.rule import RewardRule


class RewardEngine(RewardStrategy):
    """Computes scalar reinforcement training metrics by evaluating registered rules."""

    def __init__(self, rules: Sequence[RewardRule] | None = None):
        """Initialize the RewardEngine.

        Args:
            rules: Initial sequence of reward rules to evaluate.
        """
        self.rules: list[RewardRule] = list(rules) if rules else []

    def add_rule(self, rule: RewardRule) -> None:
        """Register a new reward rule.

        Args:
            rule: The reward rule to append to the evaluation chain.
        """
        self.rules.append(rule)

    def calculate(
        self,
        previous_state: GameState,
        current_state: GameState,
    ) -> RewardEvent:
        """Evaluate performance of transitions across all registered rules.

        Args:
            previous_state: Prior environment state.
            current_state: Updated step state.

        Returns:
            Evaluation score event metrics aggregating all triggered rules.
        """
        total_value = 0.0
        event_types: list[str] = []

        for rule in self.rules:
            event = rule.evaluate(previous_state, current_state)
            if event:
                total_value += event.value
                event_types.append(event.event_type)

        if not event_types:
            return RewardEvent(value=0.0, event_type="NONE")

        return RewardEvent(value=total_value, event_type="|".join(event_types))
