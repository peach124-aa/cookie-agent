"""Main action planner orchestration."""

from collections.abc import Sequence

from cookie_agent.core.actions import ActionIntent, ADBCommand, IntentType
from cookie_agent.core.state import GameState
from cookie_agent.planner import builder, mapping
from cookie_agent.planner.exceptions import MappingError


class CookieActionPlanner:
    """Stateless translator mapping abstract intents into deterministic device commands."""

    def plan(self, intent: ActionIntent, state: GameState) -> Sequence[ADBCommand]:
        """Translates abstract actions to hardware commands.

        Args:
            intent: Abstract motion intent choice.
            state: Current environment state.

        Returns:
            Touch event sequence lists.

        Raises:
            MappingError: If the intent type cannot be handled.
        """
        match intent.intent:
            case IntentType.IDLE | IntentType.NONE:
                return []

            case IntentType.JUMP:
                return builder.tap(
                    x=mapping.JUMP_BUTTON_X,
                    y=mapping.JUMP_BUTTON_Y,
                    hold_ms=50,
                    delay_ms=0,
                )

            case IntentType.DOUBLE_JUMP:
                # Issue two consecutive taps on the jump button with a small delay
                seq1 = builder.tap(
                    x=mapping.JUMP_BUTTON_X,
                    y=mapping.JUMP_BUTTON_Y,
                    hold_ms=50,
                    delay_ms=100,
                )
                seq2 = builder.tap(
                    x=mapping.JUMP_BUTTON_X,
                    y=mapping.JUMP_BUTTON_Y,
                    hold_ms=50,
                    delay_ms=0,
                )
                return list(seq1) + list(seq2)

            case IntentType.SLIDE:
                # Slide is typically a longer hold
                return builder.hold(
                    x=mapping.SLIDE_BUTTON_X,
                    y=mapping.SLIDE_BUTTON_Y,
                    hold_ms=500,
                    delay_ms=0,
                )

            case IntentType.DASH:
                # Dash might be a quick swipe or another hold depending on character.
                return builder.swipe(
                    start_x=mapping.DASH_BUTTON_X,
                    start_y=mapping.DASH_BUTTON_Y,
                    end_x=mapping.DASH_BUTTON_X - 200,
                    end_y=mapping.DASH_BUTTON_Y,
                    duration_ms=100,
                )

            case IntentType.RELAY:
                # Assuming relay isn't explicitly requested in the prompt but exists
                return builder.tap(
                    x=mapping.JUMP_BUTTON_X,
                    y=mapping.JUMP_BUTTON_Y,
                    hold_ms=50,
                    delay_ms=0,
                )

            case _:
                raise MappingError(f"Unsupported intent mapping: {intent.intent}")
