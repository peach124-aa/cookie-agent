"""Generics and types for the RL Experience Buffer."""

from typing import TypeVar

# Generic type definitions representing abstract RL structures
StateType = TypeVar("StateType")
ActionType = TypeVar("ActionType")
InfoType = TypeVar("InfoType")
