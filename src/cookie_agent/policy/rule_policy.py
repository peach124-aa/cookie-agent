"""Deterministic heuristic rule-based policy."""

from cookie_agent.core.actions import ActionIntent, IntentType
from cookie_agent.core.state import GameState


class RulePolicy:
    """A stateless, deterministic policy using basic heuristics.

    This policy evaluates the GameState to trigger basic actions
    such as jumping to avoid imminent obstacles or falling into pits.
    """

    def __init__(self, jump_threshold_x: float = 0.2) -> None:
        """Initialize the RulePolicy.

        Args:
            jump_threshold_x: Normalized x-distance threshold to trigger a jump.
        """
        self._jump_threshold_x = jump_threshold_x

    def select_action(self, state: GameState) -> ActionIntent:
        """Select a deterministic action based on the current state.

        Args:
            state: The current unified GameState.

        Returns:
            An ActionIntent for locomotion.
        """
        player = state.player

        # Very basic heuristic: if we are grounded and there's an obstacle ahead, jump.
        # We assume tracked objects have been classified by the tracker/builder.
        # Since we don't have exact obstacle classifications here, we can mock it
        # based on velocity or simple proximity if any object is close in front.

        # If player is not grounded, maybe we shouldn't jump or we could double jump.
        if player.grounded:
            for obj in state.objects:
                # Using the bounding box directly from the tracked object
                obj_x = obj.bbox.xmin
                if 0 < obj_x < self._jump_threshold_x:
                    return ActionIntent(IntentType.JUMP)

        return ActionIntent(IntentType.NONE)
