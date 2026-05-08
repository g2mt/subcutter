"""Action history manager with undo/redo support."""

from PySide6.QtCore import QObject, Signal


from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from subcutter.actions.action import Action


class ActionHistory(QObject):
    """Manages a stack of undoable actions with undo/redo support."""

    can_undo_changed = Signal(bool)
    can_redo_changed = Signal(bool)
    action_performed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._undo_stack: list[Action] = []
        self._redo_stack: list[Action] = []

    def do(self, action: Action) -> None:
        """Execute an action and push it onto the undo stack."""
        action.do()
        self._undo_stack.append(action)
        self._redo_stack.clear()
        self._emit_signals()
        self.action_performed.emit()

    def undo(self) -> None:
        """Undo the most recent action."""
        if not self._undo_stack:
            return
        action = self._undo_stack.pop()
        action.undo()
        self._redo_stack.append(action)
        self._emit_signals()
        self.action_performed.emit()

    def redo(self) -> None:
        """Redo the most recently undone action."""
        if not self._redo_stack:
            return
        action = self._redo_stack.pop()
        action.do()
        self._undo_stack.append(action)
        self._emit_signals()
        self.action_performed.emit()

    def can_undo(self) -> bool:
        """Return whether there are actions that can be undone."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Return whether there are actions that can be redone."""
        return len(self._redo_stack) > 0

    def _emit_signals(self) -> None:
        self.can_undo_changed.emit(self.can_undo())
        self.can_redo_changed.emit(self.can_redo())
