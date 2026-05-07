"""Abstract base class for undoable actions."""

from abc import ABC, abstractmethod


class Action(ABC):
    """An undoable operation on the project state."""

    @abstractmethod
    def do(self):
        """Apply the action."""

    @abstractmethod
    def undo(self):
        """Reverse the action."""
