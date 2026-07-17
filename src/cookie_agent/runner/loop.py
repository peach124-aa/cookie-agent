"""Continuous execution loop for the InferenceRunner."""

import time

from cookie_agent.runner.exceptions import LoopStoppedError
from cookie_agent.runner.metrics import LoopMetrics
from cookie_agent.runner.runner import InferenceRunner


class InferenceLoop:
    """Manages the continuous execution of the inference pipeline."""

    def __init__(self, runner: InferenceRunner) -> None:
        """Initialize the InferenceLoop.

        Args:
            runner: The configured InferenceRunner instance to execute.
        """
        self._runner = runner
        self._is_running = False

    def run_forever(self) -> LoopMetrics:
        """Run the inference pipeline continuously until stopped.

        Returns:
            LoopMetrics summarizing the execution block.
        """
        self._is_running = True
        frame_count = 0
        step_count = 0
        start_time = time.perf_counter()

        try:
            while self._is_running:
                self._runner.run_step()
                frame_count += 1
                step_count += 1
        except (KeyboardInterrupt, LoopStoppedError):
            self.stop()

        loop_duration_ms = (time.perf_counter() - start_time) * 1000.0

        return LoopMetrics(
            frame_count=frame_count,
            step_count=step_count,
            loop_duration_ms=loop_duration_ms,
        )

    def stop(self) -> None:
        """Signal the loop to stop executing after the current step."""
        self._is_running = False
