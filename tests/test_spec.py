"""PathSpec — ordering, negation, and the parts of a spec file that are not patterns."""

from __future__ import annotations

import pytest

from pathspec_lite import PathSpec, PatternError


def test_last_match_wins() -> None:
    spec = PathSpec(["*.log", "!keep.log"])
    assert spec.match_file("debug.log")
    assert not spec.match_file("keep.log")


def test_order_matters() -> None:
    """The same two lines the other way round: the negation is overridden, not remembered."""
    assert PathSpec(["!keep.log", "*.log"]).match_file("keep.log")


def test_comments_and_blank_lines_are_skipped() -> None:
    spec = PathSpec(["# build output", "", "   ", "*.log"])
    assert len(spec) == 1
    assert spec.match_file("a.log")


def test_an_empty_spec_matches_nothing() -> None:
    spec = PathSpec([])
    assert len(spec) == 0
    assert not spec.match_file("anything")


def test_match_files_preserves_the_order_given() -> None:
    spec = PathSpec(["*.log"])
    assert spec.match_files(["b.log", "a.txt", "a.log"]) == ("b.log", "a.log")


def test_a_globstar_spec_selects_nested_paths() -> None:
    spec = PathSpec(["**/*.pyc"])
    assert spec.match_file("a/b/c.pyc")
    assert not spec.match_file("c.pyc")


def test_iterating_a_spec_yields_its_compiled_source_lines() -> None:
    spec = PathSpec(["*.log", "# skipped", "!keep.log"])
    assert list(spec) == ["*.log", "!keep.log"]


def test_repr_names_the_rules() -> None:
    assert repr(PathSpec(["*.log"])) == "PathSpec(['*.log'])"


def test_a_malformed_pattern_refuses_the_whole_spec() -> None:
    with pytest.raises(PatternError):
        PathSpec(["*.log", "a[bc"])
