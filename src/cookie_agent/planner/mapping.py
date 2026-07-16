"""Physical configuration mappings for device input coordinates."""

# Default standardized coordinates based on a 1920x1080 baseline orientation.
# X is horizontal, Y is vertical.
# Note: These values should be adjusted or scaled by higher-level configuration,
# but we provide static defaults to maintain a deterministic stateless planner.

# Left side screen for jumping
JUMP_BUTTON_X = 200
JUMP_BUTTON_Y = 800

# Right side screen for sliding
SLIDE_BUTTON_X = 1720
SLIDE_BUTTON_Y = 800

# Dash might map to a swipe or a specific button if the character has a dash skill.
# Here we'll treat it as a right-side swipe or special button.
DASH_BUTTON_X = 1720
DASH_BUTTON_Y = 500
