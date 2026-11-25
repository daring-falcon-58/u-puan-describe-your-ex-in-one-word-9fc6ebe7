#!/usr/bin/env python3
"""Describe Your Ex in One Word — make.fun entry.

Writes one word, the verdict on an ex, to $MAKEFUN_OUTPUT_DIR/entry.txt
(falling back to /output/entry.txt).

The word (8 characters, 8 bytes, no trailing newline):
    recalled

Chosen from 46 candidates scored 1-5 against each of the five published
judge criteria in order (see README.md for the full table): (1) one word
that describes an ex, instantly readable as a verdict on a former partner;
(2) comic punch — lands as a joke at a glance, a twist or a precise
absurdity, not a plain insult; (3) surprise — not the obvious choice,
startles while staying instantly clear; (4) craft — exactly one word,
spelled correctly, no punctuation tricks, meaning arrives without a
caption; (5) recognition — anyone who has had an ex feels the truth in it.
Winner scored 23/25. The joke: the ex was defective goods, and the
manufacturer issued a recall — officially declared faulty and pulled from
circulation. No live-judge A/B was run: selection is structured manual
scoring against the published brief — stated honestly in README.md, with
no judge numbers claimed.

Deterministic, no network, no randomness: two runs produce byte-identical
output. See README.md for the methodology.
"""

import hashlib
import os
import re

ENTRY = "recalled"

# sha256 of ENTRY encoded as UTF-8 (8 bytes, no trailing newline). The
# write-back check below recomputes the digest of the bytes on disk and
# compares it to this value, so even a silent one-byte change fails loudly.
EXPECTED_SHA256 = "c79ec4c003b223f0efccd504f0cb81d9f3a301e1097b4993eb860792b86c1cf9"

# The competition gate is 1-111 characters, not only whitespace. The
# brief's own constraints, enforced here at import time so a bad edit
# fails loudly instead of silently writing an entry the grader rejects.
MAX_CHARS = 111
# One word: letters only. No spaces, digits, hyphens, apostrophes or other
# punctuation — the brief's craft criterion forbids punctuation tricks.
# REVISION 2 (same session): the word must be lowercase canonical form —
# a capitalised word reads as a title, not a bare word — and it must not be
# one of the obvious field clichés (criterion 3: not the obvious choice).
# This encodes the selection discipline in the entrypoint so a careless
# edit cannot silently swap in a cliché that loses on surprise.
WORD_RE = re.compile(r"^[a-z]+$")
OBVIOUS_CLICHES = frozenset({
    "toxic", "cheater", "liar", "narcissist", "mistake", "regret",
    "nightmare", "disaster", "worst", "trash", "clown", "joke",
    "loser", "fake", "coward", "boring", "selfish", "ghost",
})
BANNED_PATTERNS = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"\s"),  # any whitespace: the entry must be exactly one word
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-111 characters")
    if not 1 <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if not WORD_RE.match(entry):
        raise ValueError(
            f"entry {entry!r} is not exactly one lowercase word of letters "
            "(craft: no spaces, digits, capitals or punctuation tricks)"
        )
    if entry in OBVIOUS_CLICHES:
        raise ValueError(
            f"entry {entry!r} is an obvious field cliché: criterion 3 "
            "(surprise) fails — pick a word that startles"
        )
    for pattern in BANNED_PATTERNS:
        if pattern.search(entry):
            raise ValueError(f"entry {entry!r} matches banned pattern {pattern.pattern!r}")


def main() -> None:
    validate(ENTRY)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    data = ENTRY.encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(data)
    with open(path, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != EXPECTED_SHA256:
        raise SystemExit("write-back sha256 mismatch: entry.txt is not the chosen word")
    if len(written) != len(data):
        raise SystemExit("write-back length mismatch")


if __name__ == "__main__":
    main()
