"""Compile one gitignore-style path pattern into a regular expression.

A pattern is matched against a **relative POSIX path** — ``docs/readme.txt``, never
``./docs/readme.txt`` and never a Windows separator. The whole path must match; there is no
"matches somewhere inside" mode, because a half-anchored matcher is the kind of thing that is
convenient once and wrong forever after.

The syntax is the familiar one:

==========  =====================================================================
``*``       any run of characters within a single path segment
``**``      any run of characters, separators included
``?``       exactly one character
``[abc]``   one character from the set; ``[a-z]`` ranges work
``[!abc]``  one character *not* in the set
==========  =====================================================================

Anything else is a literal, including ``.``, which is the character people most often expect to
be a wildcard because a regular expression taught them so.

**Translation, not interpretation.** A pattern becomes a :class:`re.Pattern` once and is then
matched many times, which is the only reason this module is worth having over a hand-rolled loop.
"""

from __future__ import annotations

import re
from typing import Final

__all__ = ["PatternError", "compile_pattern", "translate"]


class PatternError(ValueError):
    """A pattern is malformed and cannot be compiled.

    A ``ValueError`` because a bad pattern is bad input, and callers that already handle
    ``ValueError`` around a compile step should not have to learn a new type to keep working.
    """


#: The atom a star becomes.
_ANY: Final[str] = ".*"

#: The atom a question mark becomes.
_ONE: Final[str] = "."


def translate(pattern: str) -> str:
    """Translate *pattern* into an anchored regular-expression source string.

    The result is wrapped in ``(?s:...)`` so that a wildcard also spans a newline — a path may
    legally contain one — and terminated with ``\\Z`` so a match is a whole-path match.

    :raises PatternError: on an empty pattern or a malformed character class.
    """
    if not pattern:
        raise PatternError("a pattern must not be empty")

    parts: list[str] = []
    index = 0
    end = len(pattern)
    while index < end:
        char = pattern[index]
        if char == "*":
            # A run of stars is one wildcard.
            while index < end and pattern[index] == "*":
                index += 1
            parts.append(_ANY)
        elif char == "?":
            index += 1
            parts.append(_ONE)
        elif char == "[":
            atom, index = _character_class(pattern, index)
            parts.append(atom)
        else:
            index += 1
            parts.append(re.escape(char))
    return "(?s:" + "".join(parts) + r")\Z"


def _character_class(pattern: str, start: int) -> tuple[str, int]:
    """Read the class opening at ``pattern[start]``; return its atom and the index after it.

    ``]`` closes the class at the first opportunity, so a literal ``]`` cannot be a member. That
    is a real limit and it is documented rather than worked around: the escape rules that would
    lift it are the part of glob syntax nobody agrees on.
    """
    close = pattern.find("]", start + 1)
    if close == -1:
        raise PatternError(
            f"pattern {pattern!r} opens a character class at index {start} and never closes it"
        )

    body = pattern[start + 1 : close]
    if not body:
        raise PatternError(f"pattern {pattern!r} has an empty character class at index {start}")

    negated = body.startswith("!")
    if negated:
        body = body[1:]
        if not body:
            raise PatternError(
                f"pattern {pattern!r} has a negated character class with no members at "
                f"index {start}"
            )

    # Only the two characters that would change the meaning of the class we are building. A
    # blanket `re.escape` cannot be used here: it escapes `-`, which would turn every range into
    # three literals.
    body = body.replace("\\", "\\\\").replace("^", "\\^")
    atom = f"[^{body}]" if negated else f"[{body}]"
    return atom, close + 1


def compile_pattern(pattern: str) -> re.Pattern[str]:
    """Compile *pattern* into a :class:`re.Pattern` that matches a whole path.

    :raises PatternError: if *pattern* is malformed.
    """
    return re.compile(translate(pattern))
