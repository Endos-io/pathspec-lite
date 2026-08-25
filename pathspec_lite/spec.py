"""An ordered collection of patterns — the last one that matches decides.

This is the rule ``.gitignore`` uses and the reason a spec is a *list* rather than a set: order
carries meaning. ``*.log`` followed by ``!keep.log`` excludes every log except one; reverse the
two lines and the exception is silently lost.

Blank lines and ``#`` comments are skipped, so a spec can be read straight out of a file without
the caller having to pre-filter it.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from pathspec_lite.pattern import compile_pattern

__all__ = ["PathSpec"]


@dataclass(frozen=True, slots=True)
class _Rule:
    """One compiled line. ``source`` is kept for :meth:`PathSpec.__repr__` and for error messages
    — a compiled pattern cannot be read back, and a spec that cannot say which line matched is
    unusable to debug against."""

    source: str
    negated: bool
    regex: re.Pattern[str]


class PathSpec:
    """A sequence of patterns matched against relative POSIX paths.

    >>> spec = PathSpec(["*.log", "!keep.log"])
    >>> spec.match_file("debug.log")
    True
    >>> spec.match_file("keep.log")
    False
    """

    __slots__ = ("_rules",)

    def __init__(self, patterns: Iterable[str]) -> None:
        """:raises PatternError: if any line is malformed. A spec is all-or-nothing — a partially
        compiled one would match on some lines and silently ignore others."""
        rules: list[_Rule] = []
        for source in patterns:
            text = source.strip()
            if not text or text.startswith("#"):
                continue
            negated = text.startswith("!")
            if negated:
                text = text[1:]
            rules.append(_Rule(source=source, negated=negated, regex=compile_pattern(text)))
        self._rules: tuple[_Rule, ...] = tuple(rules)

    def __len__(self) -> int:
        """The number of compiled rules — blank and comment lines do not count."""
        return len(self._rules)

    def __iter__(self) -> Iterator[str]:
        """The source text of each compiled rule, in order."""
        return (rule.source for rule in self._rules)

    def __repr__(self) -> str:
        return f"PathSpec({[rule.source for rule in self._rules]!r})"

    def match_file(self, path: str) -> bool:
        """True if *path* is selected by this spec.

        Every rule is tried, in order, and the last one that matches decides — an earlier
        ``return`` would make a later negation unreachable.
        """
        selected = False
        for rule in self._rules:
            if rule.regex.match(path) is not None:
                selected = not rule.negated
        return selected

    def match_files(self, paths: Iterable[str]) -> tuple[str, ...]:
        """Every path in *paths* that :meth:`match_file` selects, in the order given."""
        return tuple(path for path in paths if self.match_file(path))
