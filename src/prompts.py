"""Loader for the prompt library.

Prompts live in `prompts/` as versioned files rather than as string literals in
the code, so that the question "which requirement does this instruction serve,
and what did it say last week" has an answer. The version travels with every
decision written to the log.
"""

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache

PROMPT_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


@dataclass
class Prompt:
    id: str
    name: str
    version: str
    purpose: str
    requirements: list[str]
    system: str
    user: str
    path: str
    notes: str = ""
    acceptance: list[str] = field(default_factory=list)

    @property
    def reference(self) -> str:
        """What gets written into the decision log, e.g. 'PR-01 v1.0'."""
        return f"{self.id} v{self.version}"

    def render_user(self, **values) -> str:
        return self.user.format(**values)


def _parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    _, raw, body = text.split("---", 2)

    meta: dict = {}
    key = None
    for line in raw.strip().splitlines():
        if re.match(r"^\s", line) and key:
            meta[key] = f"{meta[key]} {line.strip()}".strip()
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            meta[key] = "" if value == ">" else value
    return meta, body


def _section(body: str, heading: str) -> str:
    match = re.search(
        rf"^##\s+{heading}\s*$(.*?)(?=^##\s+|\Z)", body, re.MULTILINE | re.DOTALL
    )
    return match.group(1).strip() if match else ""


@lru_cache(maxsize=None)
def load_prompt(relative_path: str) -> Prompt:
    """Load one prompt, e.g. load_prompt('build/classify.md')."""
    path = os.path.join(PROMPT_ROOT, relative_path)
    with open(path, encoding="utf-8") as handle:
        text = handle.read()

    meta, body = _parse_front_matter(text)
    if not meta.get("id"):
        raise ValueError(f"{relative_path}: prompt is missing an id in its front matter")

    def listed(name: str) -> list[str]:
        raw = meta.get(name, "")
        return [item.strip() for item in raw.split(",") if item.strip()]

    return Prompt(
        id=meta["id"],
        name=meta.get("name", os.path.basename(relative_path)),
        version=meta.get("version", "0"),
        purpose=meta.get("purpose", ""),
        requirements=listed("requirements"),
        acceptance=listed("acceptance"),
        notes=meta.get("notes", ""),
        system=_section(body, "System"),
        user=_section(body, "User"),
        path=relative_path,
    )


def register() -> list[Prompt]:
    """Every prompt in the library. Rendered into the Stage 3 register."""
    found = []
    for root, _, files in os.walk(PROMPT_ROOT):
        for name in sorted(files):
            if name.endswith(".md") and name != "README.md":
                relative = os.path.relpath(os.path.join(root, name), PROMPT_ROOT)
                found.append(load_prompt(relative))
    return sorted(found, key=lambda prompt: prompt.id)
