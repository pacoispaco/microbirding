"""Minimal task-list support for Mistune 3.x. This is used to render the CHANGELOG.md
   file as HTML with nicer layout for checkboxes.

Turns:
  - [x] Done
  - [ ] Todo
into:
  <li><input type="checkbox" disabled checked> Done</li>
  <li><input type="checkbox" disabled> Todo</li>"""

from __future__ import annotations
import re
from mistune import HTMLRenderer, Markdown

_TASK = re.compile(r'^\s*\[(?P<mark>[ xX])\]\s+')


class TasklistRenderer(HTMLRenderer):
    def __init__(self, *, disabled: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.disabled = disabled

    # NOTE: Mistune 3.x uses list_item(self, text)  ← no "level"
    def list_item(self, text: str) -> str:
        s = text.strip()

        # Handle loose list items (<p>…</p>) and tight ones
        loose = s.startswith("<p>") and s.endswith("</p>")
        inner = s[3:-4].strip() if loose else s

        m = _TASK.match(inner)
        if not m:
            return super().list_item(text)  # delegate to default

        checked = (m.group("mark").lower() == "x")
        rest = inner[m.end():]

        attrs = ['type="checkbox"']
        if self.disabled:
            attrs.append("disabled")
        if checked:
            attrs.append("checked")
        box = f"<input {' '.join(attrs)}>"

        if loose:
            rest = f"<p>{rest}</p>"

        return f"<li>{box}{rest}</li>\n"


def mistune_markdown_instance(*, disabled: bool = True) -> Markdown:
    """Return a Mistune Markdown instance with task-list checkboxes."""
    return Markdown(renderer=TasklistRenderer(disabled=disabled))
