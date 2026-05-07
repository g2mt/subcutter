"""Action for toggling the ignored state of subtitle fragments."""

from subcutter.actions.action import Action


class IgnoreFragmentAction(Action):
    """Toggle the ignored state of a set of subtitle fragments."""

    def __init__(self, fragments):
        super().__init__()
        self._fragments = list(fragments)
        self._previous_states = None

    def do(self):
        if self._previous_states is None:
            self._previous_states = [f.ignored for f in self._fragments]
        state = not self._fragments[0].ignored
        for frag in self._fragments:
            frag.ignored = state

    def undo(self):
        for frag, state in zip(self._fragments, self._previous_states):
            frag.ignored = state
