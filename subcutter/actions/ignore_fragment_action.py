"""Action for toggling the ignored state of subtitle fragments."""



from subcutter.actions.action import Action
from subcutter.widgets.subtitle_fragment import SubtitleFragment


class IgnoreFragmentAction(Action):
    """Toggle the ignored state of a set of subtitle fragments."""

    def __init__(self, fragments: list[SubtitleFragment]) -> None:
        super().__init__()
        self._fragments = list(fragments)
        self._previous_states: list[bool] | None = None

    def do(self) -> None:
        if self._previous_states is None:
            self._previous_states = [f.ignored for f in self._fragments]
        state = not self._fragments[0].ignored
        for frag in self._fragments:
            frag.ignored = state

    def undo(self) -> None:
        if self._previous_states is None:
            return
        for frag, state in zip(self._fragments, self._previous_states):
            frag.ignored = state
