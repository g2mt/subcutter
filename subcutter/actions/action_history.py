"""Action history manager with undo/redo support."""

from PySide6.QtCore import QObject, Signal


class ActionHistory(QObject):
    """Manages a stack of undoable actions with undo/redo support."""

    can_undo_changed = Signal(bool)
    can_redo_changed = Signal(bool)
    action_performed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._undo_stack = []
        self._redo_stack = []

    def do(self, action):
        """Execute an action and push it onto the undo stack."""
        action.do()
        self._undo_stack.append(action)
        self._redo_stack.clear()
        self._emit_signals()
        self.action_performed.emit()

    def undo(self):
        """Undo the most recent action."""
        if not self._undo_stack:
            return
        action = self._undo_stack.pop()
        action.undo()
        self._redo_stack.append(action)
        self._emit_signals()
        self.action_performed.emit()

    def redo(self):
        """Redo the most recently undone action."""
        if not self._redo_stack:
            return
        action = self._redo_stack.pop()
        action.do()
        self._undo_stack.append(action)
        self._emit_signals()
        self.action_performed.emit()

    def can_undo(self):
        """Return whether there are actions that can be undone."""
        return len(self._undo_stack) > 0

    def can_redo(self):
        """Return whether there are actions that can be redone."""
        return len(self._redo_stack) > 0

    def _emit_signals(self):
        self.can_undo_changed.emit(self.can_undo())
        self.can_redo_changed.emit(self.can_redo())
