"""Pattern translation and single-pattern matching."""

from __future__ import annotations

import re

import pytest

from pathspec_lite import PatternError, match, translate


# ── stars ────────────────────────────────────────────────────────────────────────────────────
def test_star_matches_within_a_segment() -> None:
    assert match("*.txt", "readme.txt")


def test_star_does_not_cross_a_separator() -> None:
    """A `*` is segment-local: `*.txt` is "a .txt file *here*", not "anywhere below here".

    Reported against 0.1.0: a spec built from `*.log` was excluding `build/output.log`, which no
    reading of the syntax table permits. `**/*.log` is how that is asked for.
    """
    assert not match("*.txt", "docs/readme.txt")


def test_globstar_crosses_separators() -> None:
    assert match("src/**/test_*.py", "src/a/b/test_io.py")


def test_globstar_still_requires_its_literal_separators() -> None:
    assert not match("a/**/b", "a/b")


# ── single characters ────────────────────────────────────────────────────────────────────────
def test_question_mark_matches_exactly_one_character() -> None:
    assert match("a?c", "abc")


def test_question_mark_does_not_match_two() -> None:
    assert not match("a?c", "abbc")


# ── character classes ────────────────────────────────────────────────────────────────────────
def test_character_class_matches_a_member() -> None:
    assert match("[abc]x", "bx")


def test_character_class_rejects_a_non_member() -> None:
    assert not match("[abc]x", "dx")


def test_character_class_range() -> None:
    assert match("file[0-9].txt", "file7.txt")
    assert not match("file[0-9].txt", "fileA.txt")


def test_negated_character_class_excludes_its_members() -> None:
    assert not match("[!abc]x", "bx")


def test_negated_character_class_admits_everything_else() -> None:
    assert match("[!abc]x", "dx")


# ── literals and anchoring ───────────────────────────────────────────────────────────────────
def test_a_dot_is_a_literal_not_a_wildcard() -> None:
    assert not match("a.c", "abc")


def test_the_whole_path_must_match() -> None:
    assert not match("readme", "readme.txt")
    assert not match("readme.txt", "docs/readme.txt")


def test_a_path_containing_a_newline_still_matches() -> None:
    assert match("a*c", "a\nc")


# ── translation ──────────────────────────────────────────────────────────────────────────────
def test_translate_produces_a_compilable_expression() -> None:
    re.compile(translate("src/**/*.py"))


# ── refusals ─────────────────────────────────────────────────────────────────────────────────
def test_an_empty_pattern_is_refused() -> None:
    with pytest.raises(PatternError):
        match("", "anything")


def test_an_unclosed_character_class_is_refused() -> None:
    with pytest.raises(PatternError):
        match("a[bc", "abc")


def test_an_empty_character_class_is_refused() -> None:
    with pytest.raises(PatternError):
        match("a[]c", "abc")


def test_a_negated_class_with_no_members_is_refused() -> None:
    with pytest.raises(PatternError):
        match("a[!]c", "abc")
