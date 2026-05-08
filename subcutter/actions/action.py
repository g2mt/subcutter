"""Abstract base class for undoable actions."""

from abc import ABC, abstractmethod


class Action(ABC):
    """An undoable operation on the project state."""

    @abstractmethod
    def do(self) -> None:
        """Apply the action."""

    @abstractmethod
    def undo(self) -> None:
        """Reverse the action."""
