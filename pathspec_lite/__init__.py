"""pathspec-lite — gitignore-style path matching, small enough to read in one sitting.

>>> from pathspec_lite import match
>>> match("*.txt", "readme.txt")
True

For more than one pattern, use :class:`~pathspec_lite.spec.PathSpec`, which applies the
last-match-wins rule that makes ``!`` negation work.
"""

from __future__ import annotations

from pathspec_lite.pattern import PatternError, compile_pattern, translate
from pathspec_lite.spec import PathSpec

__all__ = ["PathSpec", "PatternError", "compile_pattern", "match", "translate"]
__version__ = "0.1.0"


def match(pattern: str, path: str) -> bool:
    """True if *path* matches *pattern* in full.

    A convenience over :func:`~pathspec_lite.pattern.compile_pattern` for the one-shot case; it
    compiles every call, so a pattern used in a loop should be compiled once instead.

    :raises PatternError: if *pattern* is malformed.
    """
    return compile_pattern(pattern).match(path) is not None
