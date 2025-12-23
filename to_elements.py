#!/usr/bin/env python3

"""
Convert text into sequences of chemical element symbols or atomic IDs.

Output control flags:

Use --symbols (or -s) to output symbols.
Use --numbers (or -n) to output atomic numbers.
Use --names (or -m) to output element names.

Default mode is -n.

Non-alphabetic characters in the input text are ignored.

Use --isotopes (or -i) to enable Hydrogen isotopes:
  D -> 1.2
  T -> 1.3

When isotopes are enabled, the algorithm prefers solutions that avoid D/T
(minimizes isotope usage), e.g. "Dara" -> "Da Ra" rather than "D Ar" + failure.
"""

from __future__ import annotations

import argparse
from typing import Dict, List, Optional, Sequence

from elements_data import Element, symbol_lookup


def normalize_text(text: str) -> str:
    """Remove all whitespace characters (spaces, tabs, newlines, etc.)."""
    return "".join(c for c in text if c.isalpha())


def find_symbol_sequence(
    text: str, lookup: Dict[str, Element], enable_isotopes: bool
) -> Optional[List[str]]:
    """
    Return a list of element symbols that spell out `text`, or None if impossible.

    When isotopes are enabled, D and T are allowed but discouraged:
    prefer solutions that use fewer D/T tokens.
    """
    cleaned = normalize_text(text)
    if not cleaned:
        return []

    target = cleaned.lower()
    length = len(target)

    # Best path and its isotope-cost at each index.
    paths: List[Optional[List[str]]] = [None] * (length + 1)
    costs: List[Optional[int]] = [None] * (length + 1)
    paths[0] = []
    costs[0] = 0

    isotope_symbols = {"D", "T"} if enable_isotopes else set()

    for index in range(length):
        if paths[index] is None:
            continue

        for size in (1, 2):
            end = index + size
            if end > length:
                continue

            candidate = target[index:end].capitalize()
            if candidate not in lookup:
                continue

            step_cost = 1 if candidate in isotope_symbols else 0
            new_cost = (costs[index] or 0) + step_cost
            new_path = paths[index] + [candidate]

            # Prefer fewer isotope uses; tie-breaker prefers fewer tokens.
            if costs[end] is None or new_cost < costs[end]:
                costs[end] = new_cost
                paths[end] = new_path
            elif new_cost == costs[end] and paths[end] is not None:
                if len(new_path) < len(paths[end]):
                    paths[end] = new_path

    return paths[length]


def explain_failure(text: str, lookup: Dict[str, Element]) -> str:
    normalized = normalize_text(text)
    target = normalized.lower()
    length = len(target)

    reachable = [False] * (length + 1)
    reachable[0] = True

    for index in range(length):
        if not reachable[index]:
            continue

        for size in (1, 2):
            end = index + size
            if end > length:
                continue

            candidate = target[index:end].capitalize()
            if candidate in lookup:
                reachable[end] = True

    if reachable[length]:
        return "Conversion not possible for unknown reasons."

    furthest = max(idx for idx, flag in enumerate(reachable) if flag)
    problematic = normalized[furthest:]
    human_position = furthest + 1
    return (
        f"Conversion not possible. Letters starting at position {human_position} "
        f'("{problematic}") cannot be matched with element symbols.'
    )


def format_symbols(symbols: Sequence[str]) -> str:
    return " ".join(symbols)


def format_element_names(symbols: Sequence[str], lookup: Dict[str, Element]) -> str:
    return " ".join(lookup[s].name for s in symbols)


def format_atomic_ids(symbols: Sequence[str], lookup: Dict[str, Element]) -> str:
    return " ".join(lookup[s].atomic_id for s in symbols)


def convert_text(
    text: str,
    show_numbers: bool,
    show_symbols: bool,
    show_names: bool,
    enable_isotopes: bool
) -> str:
    lookup = symbol_lookup(enable_isotopes)
    symbols = find_symbol_sequence(text, lookup, enable_isotopes)
    if symbols is None:
        return explain_failure(text, lookup)

    # Preserve legacy behavior: if no output flags are set, default to ids.
    if not (show_numbers or show_symbols or show_names):
        show_numbers = True

    out: list[str] = []
    if show_symbols:
        out.append(format_symbols(symbols))
    if show_numbers:
        out.append(format_atomic_ids(symbols, lookup))
    if show_names:
        out.append(format_element_names(symbols, lookup))

    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert text to chemical element symbols or atomic numbers."
    )
    parser.add_argument(
        "-n",
        "--numbers",
        action="store_true",
        help="Output atomic numbers",
    )
    parser.add_argument(
        "-m",
        "--names",
        action="store_true",
        help="Output element names",
    )
    parser.add_argument(
        "-s",
        "--symbols",
        action="store_true",
        help="Output symbols",
    )
    parser.add_argument(
        "-i",
        "--isotopes",
        action="store_true",
        help='Enable Hydrogen isotopes: D -> "1.2", T -> "1.3".',
    )
    parser.add_argument("text", help="The text to convert.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = convert_text(args.text, args.numbers, args.symbols, args.names, args.isotopes)
    print(result)


if __name__ == "__main__":  # pragma: no cover
    main()
