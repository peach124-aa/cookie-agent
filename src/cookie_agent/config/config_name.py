"""Configuration name enumeration."""

from enum import StrEnum, auto


class ConfigName(StrEnum):
    """Enumeration of config files/sections in the system."""

    APP = auto()
    DEVICE = auto()
    CAPTURE = auto()
    DETECTOR = auto()
    PLANNER = auto()
    REWARD = auto()
    CHARACTER = auto()
    TRAINING = auto()
    LOGGING = auto()
