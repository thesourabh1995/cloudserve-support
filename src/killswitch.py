"""The stop control: make the system escalate everything, immediately.

The Governance Framework requires a way to stop answering automatically
"without a deployment", and treats the absence of one as a governance finding
in its own right. This is that mechanism.

It is a file rather than an environment variable or a config flag, for three
reasons. A variable needs the process restarted, which is a deployment by
another name and loses the tickets in flight. A file can be created by someone
who cannot deploy, which matters because the person who notices a bad answer at
two in the morning is usually not the person who can ship. And the switch is
read once per ticket rather than once at startup, so it takes effect on the
next ticket rather than the next release.

Engaging it does not stop the system. It stops the system *answering*: every
ticket is still classified, still logged and still escalated with its context
attached, so the queue a human picks up is the same queue they would have had,
and nothing is dropped while the switch is on.
"""

import os
from dataclasses import dataclass
from typing import Optional

from src.config import settings


@dataclass(frozen=True)
class Halt:
    """Why automation is stopped, as written by whoever stopped it."""

    engaged: bool
    note: str = ""


def _path() -> str:
    return os.getenv("KILL_SWITCH_FILE", settings.kill_switch_file)


def status() -> Halt:
    """Read the switch. Never raises.

    A switch whose own check can throw is not a safety control, so an
    unreadable file that exists is treated as engaged. If someone created it
    while the system was reading it, the safe reading is that they meant to.
    """
    path = _path()
    try:
        if not os.path.exists(path):
            return Halt(engaged=False)
    except OSError:
        return Halt(engaged=False)

    try:
        with open(path, encoding="utf-8") as handle:
            note = handle.read().strip()
    except OSError:
        note = ""
    return Halt(engaged=True, note=note or "no reason recorded")


def engage(note: str, path: Optional[str] = None) -> str:
    """Stop automatic answering. Returns the file that now holds the switch.

    Provided so the control can be exercised from a test and from the demo.
    In production this is `touch`, which is the point: it needs no tooling.
    """
    target = path or _path()
    directory = os.path.dirname(target)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(note)
    return target


def release(path: Optional[str] = None) -> None:
    """Resume automatic answering. Safe to call when already released."""
    try:
        os.remove(path or _path())
    except OSError:
        pass
