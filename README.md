# pathspec-lite

Gitignore-style path pattern matching, small enough to read in one sitting. No dependencies.

```python
from pathspec_lite import PathSpec, match

match("*.txt", "readme.txt")          # True
match("src/**/test_*.py", "src/a/b/test_io.py")   # True

spec = PathSpec(["*.log", "!keep.log"])
spec.match_file("debug.log")          # True
spec.match_file("keep.log")           # False
```

## Install

```
pip install -e .
```

## Paths

Patterns are matched against **relative POSIX paths** — `docs/readme.txt`, not `./docs/readme.txt`
and not `docs\readme.txt`. The whole path must match; there is no "matches somewhere inside" mode.

## Pattern syntax

| token | matches |
|---|---|
| `*` | any run of characters **within a single path segment** — a `*` never spans a `/` |
| `**` | any run of characters, separators included |
| `?` | exactly one character |
| `[abc]` | one character from the set; ranges such as `[a-z]` work |
| `[!abc]` | one character not in the set |

Everything else is a literal — including `.`, which is not a wildcard here however much regular
expressions have trained you to expect one.

The distinction between `*` and `**` is the whole reason this library exists rather than a call to
`fnmatch`: `fnmatch` has no notion of a path separator, so `*.txt` there happily matches
`docs/readme.txt`. Here it does not, and `**/*.txt` is how you ask for that.

### `**` is a run of characters, not a run of segments

`a/**/b` matches `a/x/b` and `a/x/y/b`. It does **not** match `a/b` — the two literal separators in
the pattern are still literal, so at least one intervening character is required. If you want both,
write two patterns. This is a deliberate simplification and the reason for the word *lite*.

## Specs

`PathSpec` holds an ordered list of patterns and applies **last match wins**, which is what makes
`!` negation work:

```python
PathSpec(["*.log", "!keep.log"]).match_files(["a.log", "keep.log", "b.txt"])
# ('a.log',)
```

Blank lines and `#` comments are skipped, so a spec can be built straight from a file's lines.

## Tests

```
python -m pytest
```

## Licence

MIT — see [LICENSE](LICENSE).
