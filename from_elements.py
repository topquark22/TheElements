#!/usr/bin/env python3

"""
Convert a whitespace-separated sequence of atomic IDs into concatenated
element symbols.

Standard atomic numbers 1..118 are accepted.
Also, the values of the isotopes of Hydrogen are accepted:
  "1.2" -> D (Deuterium)
  "1.3" -> T (Tritium)
"""

from __future__ import annotations

import argparse
from typing import Dict, List, Sequence

from elements_data import atomic_id_to_symbol


def parse_atomic_ids(tokens: Sequence[str], enable_isotopes: bool) -> List[str]:
    if not tokens:
        raise ValueError("No atomic IDs provided.")

    ids: List[str] = []
    allowed_isotope_ids = {"1.2", "1.3"} if enable_isotopes else set()

    for idx, raw in enumerate(tokens, start=1):
        s = raw.strip()
        if not s:
            continue

        if s.isdigit():
            value = int(s, 10)
            if value < 1 or value > 118:
                raise ValueError(f"Token #{idx} value {value} is out of range (1..118).")
            ids.append(str(value))
            continue

        if s in allowed_isotope_ids:
            ids.append(s)
            continue

        extra = ' (enable --isotopes / -i for "1.2" / "1.3")' if not enable_isotopes else ""
        raise ValueError(
            f'Token #{idx} "{raw}" is not a valid atomic ID. Use 1..118{extra}.'
        )

    if not ids:
        raise ValueError("No atomic IDs provided.")

    return ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert atomic IDs to concatenated element symbols."
    )
    parser.add_argument(
        "-i",
        "--isotopes",
        action="store_true",
        help='Enable Hydrogen isotope IDs: "1.2" (D) and "1.3" (T).',
    )
    parser.add_argument(
        "ids",
        nargs="+",
        help='Atomic IDs: 1..118 (and optionally "1.2"/"1.3" with --isotopes).',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    id_to_symbol: Dict[str, str] = atomic_id_to_symbol(args.isotopes)

    try:
        ids = parse_atomic_ids(args.ids, args.isotopes)
        print("".join(id_to_symbol[a] for a in ids))
    except ValueError as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":  # pragma: no cover
    main()
