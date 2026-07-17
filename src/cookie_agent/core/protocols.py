"""Formal communication contracts (Protocols)."""

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from cookie_agent.core.actions import ActionIntent, ADBCommand
from cookie_agent.core.detection import Detection
from cookie_agent.core.frame import Frame
from cookie_agent.core.reward import RewardEvent
from cookie_agent.core.state import GameState, MapHint
from cookie_agent.core.tracking import TrackedObject


@runtime_checkable
class CaptureSource(Protocol):
    """Contract for polling the emulator window stream."""

    def capture(self) -> Frame:
        """Capture a lossless graphic buffer.

        Returns:
            A Frame if capture is successful.
            Raises exception on failure.
        """
        ...


@runtime_checkable
class Detector(Protocol):
    """Contract for predicting object coordinate boxes."""

    def detect(self, frame: Frame) -> Sequence[Detection]:
        """Runs inference on a Frame.

        Args:
            frame: The captured Frame.

        Returns:
            A list of detected objects.
        """
        ...


@runtime_checkable
class Tracker(Protocol):
    """Contract for tracking bounding box lifecycles across frames."""

    def track(self, detections: Sequence[Detection]) -> Sequence[TrackedObject]:
        """Link object coordinates across times steps.

        Args:
            detections: List of raw predictions.

        Returns:
            List of tracked entities.
        """
        ...


@runtime_checkable
class StateBuilder(Protocol):
    """Contract for merging tracking outputs into a unified GameState."""

    def build(
        self,
        tracked_objects: Sequence[TrackedObject],
        ocr_results: dict[str, float | str] | None = None,
        character_status: dict[str, bool | float | str] | None = None,
        map_hint: MapHint | None = None,
        previous_state: GameState | None = None,
    ) -> GameState:
        """Compose the unified state representation.

        Args:
            tracked_objects: Output from Tracker.
            ocr_results: Parsed character indicators.
            character_status: Attributes representing the cookie.
            map_hint: Advisory layout targets.
            previous_state: Prior environment snapshot.

        Returns:
            A GameState describing the environment state.
        """
        ...


@runtime_checkable
class RewardStrategy(Protocol):
    """Contract for scoring step-wise state updates."""

    def calculate(
        self,
        previous_state: GameState,
        current_state: GameState,
    ) -> RewardEvent:
        """Evaluate performance of transitions.

        Args:
            previous_state: Prior environment state.
            current_state: Updated step state.

        Returns:
            Evaluation score event metrics.
        """
        ...


@runtime_checkable
class Policy(Protocol):
    """Contract for choosing navigation intent targets."""

    def select_action(self, state: GameState) -> ActionIntent:
        """Choose target locomotion intent.

        Args:
            state: Unified environment properties.

        Returns:
            Abstract movement category intent.
        """
        ...


@runtime_checkable
class ActionPlanner(Protocol):
    """Contract for converting motion intents to device clicks."""

    def plan(self, intent: ActionIntent, state: GameState) -> Sequence[ADBCommand]:
        """Translates abstract actions to hardware commands.

        Args:
            intent: Abstract motion intent choice.
            state: Current environment state.

        Returns:
            Touch event sequence lists.
        """
        ...


@runtime_checkable
class DeviceController(Protocol):
    """Contract for writing command lists to hardware sockets."""

    def execute(self, commands: Sequence[ADBCommand]) -> bool:
        """Writes command lists to target socket streams.

        Args:
            commands: Sequence of tap triggers.

        Returns:
            True if all commands execute successfully, else False.
        """
        ...


@runtime_checkable
class ReplayObserver(Protocol):
    """Contract for recording raw record timelines."""

    def observe(
        self,
        frame: Frame,
        commands: Sequence[ADBCommand],
        metadata: dict[str, bool | float | str],
    ) -> None:
        """Logs raw inputs and outputs.

        Args:
            frame: Raw captured display graphics.
            commands: Emitted tap triggers.
            metadata: Setup parameters.
        """
        ...
