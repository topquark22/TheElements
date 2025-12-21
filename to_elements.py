#!/usr/bin/env python3

"""
Convert text into sequences of chemical element symbols or atomic IDs.

Default behavior uses standard element symbols only.
Use --isotopes (or -i) to enable Hydrogen isotopes:
  H -> 1
  D -> 1.2
  T -> 1.3

Important: when isotopes are enabled, the algorithm DISCOURAGES using D/T.
It will prefer solutions that avoid D and T when possible (minimizes isotope usage).

Examples:
    ./element_text_converter.py Geoffrey
    ./element_text_converter.py --full Geoffrey
    ./element_text_converter.py -i --full HDT
    ./element_text_converter.py -i Dsra      # prefers Ds Ra over D Ar + failure
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence


@dataclass(frozen=True)
class Element:
    symbol: str
    name: str
    atomic_id: str  # string to support isotope IDs like "1.2"


STANDARD_ELEMENTS: Sequence[Element] = (
    Element("H", "Hydrogen", "1"),
    Element("He", "Helium", "2"),
    Element("Li", "Lithium", "3"),
    Element("Be", "Beryllium", "4"),
    Element("B", "Boron", "5"),
    Element("C", "Carbon", "6"),
    Element("N", "Nitrogen", "7"),
    Element("O", "Oxygen", "8"),
    Element("F", "Fluorine", "9"),
    Element("Ne", "Neon", "10"),
    Element("Na", "Sodium", "11"),
    Element("Mg", "Magnesium", "12"),
    Element("Al", "Aluminium", "13"),
    Element("Si", "Silicon", "14"),
    Element("P", "Phosphorus", "15"),
    Element("S", "Sulfur", "16"),
    Element("Cl", "Chlorine", "17"),
    Element("Ar", "Argon", "18"),
    Element("K", "Potassium", "19"),
    Element("Ca", "Calcium", "20"),
    Element("Sc", "Scandium", "21"),
    Element("Ti", "Titanium", "22"),
    Element("V", "Vanadium", "23"),
    Element("Cr", "Chromium", "24"),
    Element("Mn", "Manganese", "25"),
    Element("Fe", "Iron", "26"),
    Element("Co", "Cobalt", "27"),
    Element("Ni", "Nickel", "28"),
    Element("Cu", "Copper", "29"),
    Element("Zn", "Zinc", "30"),
    Element("Ga", "Gallium", "31"),
    Element("Ge", "Germanium", "32"),
    Element("As", "Arsenic", "33"),
    Element("Se", "Selenium", "34"),
    Element("Br", "Bromine", "35"),
    Element("Kr", "Krypton", "36"),
    Element("Rb", "Rubidium", "37"),
    Element("Sr", "Strontium", "38"),
    Element("Y", "Yttrium", "39"),
    Element("Zr", "Zirconium", "40"),
    Element("Nb", "Niobium", "41"),
    Element("Mo", "Molybdenum", "42"),
    Element("Tc", "Technetium", "43"),
    Element("Ru", "Ruthenium", "44"),
    Element("Rh", "Rhodium", "45"),
    Element("Pd", "Palladium", "46"),
    Element("Ag", "Silver", "47"),
    Element("Cd", "Cadmium", "48"),
    Element("In", "Indium", "49"),
    Element("Sn", "Tin", "50"),
    Element("Sb", "Antimony", "51"),
    Element("Te", "Tellurium", "52"),
    Element("I", "Iodine", "53"),
    Element("Xe", "Xenon", "54"),
    Element("Cs", "Cesium", "55"),
    Element("Ba", "Barium", "56"),
    Element("La", "Lanthanum", "57"),
    Element("Ce", "Cerium", "58"),
    Element("Pr", "Praseodymium", "59"),
    Element("Nd", "Neodymium", "60"),
    Element("Pm", "Promethium", "61"),
    Element("Sm", "Samarium", "62"),
    Element("Eu", "Europium", "63"),
    Element("Gd", "Gadolinium", "64"),
    Element("Tb", "Terbium", "65"),
    Element("Dy", "Dysprosium", "66"),
    Element("Ho", "Holmium", "67"),
    Element("Er", "Erbium", "68"),
    Element("Tm", "Thulium", "69"),
    Element("Yb", "Ytterbium", "70"),
    Element("Lu", "Lutetium", "71"),
    Element("Hf", "Hafnium", "72"),
    Element("Ta", "Tantalum", "73"),
    Element("W", "Tungsten", "74"),
    Element("Re", "Rhenium", "75"),
    Element("Os", "Osmium", "76"),
    Element("Ir", "Iridium", "77"),
    Element("Pt", "Platinum", "78"),
    Element("Au", "Gold", "79"),
    Element("Hg", "Mercury", "80"),
    Element("Tl", "Thallium", "81"),
    Element("Pb", "Lead", "82"),
    Element("Bi", "Bismuth", "83"),
    Element("Po", "Polonium", "84"),
    Element("At", "Astatine", "85"),
    Element("Rn", "Radon", "86"),
    Element("Fr", "Francium", "87"),
    Element("Ra", "Radium", "88"),
    Element("Ac", "Actinium", "89"),
    Element("Th", "Thorium", "90"),
    Element("Pa", "Protactinium", "91"),
    Element("U", "Uranium", "92"),
    Element("Np", "Neptunium", "93"),
    Element("Pu", "Plutonium", "94"),
    Element("Am", "Americium", "95"),
    Element("Cm", "Curium", "96"),
    Element("Bk", "Berkelium", "97"),
    Element("Cf", "Californium", "98"),
    Element("Es", "Einsteinium", "99"),
    Element("Fm", "Fermium", "100"),
    Element("Md", "Mendelevium", "101"),
    Element("No", "Nobelium", "102"),
    Element("Lr", "Lawrencium", "103"),
    Element("Rf", "Rutherfordium", "104"),
    Element("Db", "Dubnium", "105"),
    Element("Sg", "Seaborgium", "106"),
    Element("Bh", "Bohrium", "107"),
    Element("Hs", "Hassium", "108"),
    Element("Mt", "Meitnerium", "109"),
    Element("Ds", "Darmstadtium", "110"),
    Element("Rg", "Roentgenium", "111"),
    Element("Cn", "Copernicium", "112"),
    Element("Nh", "Nihonium", "113"),
    Element("Fl", "Flerovium", "114"),
    Element("Mc", "Moscovium", "115"),
    Element("Lv", "Livermorium", "116"),
    Element("Ts", "Tennessine", "117"),
    Element("Og", "Oganesson", "118"),
)

ISOTOPE_ELEMENTS: Sequence[Element] = (
    Element("D", "Deuterium", "1.2"),
    Element("T", "Tritium", "1.3"),
)


def build_element_lookup(enable_isotopes: bool) -> Dict[str, Element]:
    elements: List[Element] = list(STANDARD_ELEMENTS)
    if enable_isotopes:
        elements.extend(ISOTOPE_ELEMENTS)
    return {e.symbol: e for e in elements}


def normalize_text(text: str) -> str:
    """Remove all whitespace characters (spaces, tabs, newlines, etc.)."""
    return "".join(text.split())


def find_symbol_sequence(
    text: str, lookup: Dict[str, Element], enable_isotopes: bool
) -> Optional[List[str]]:
    """
    Return a list of element symbols that spell out `text`, or None if impossible.

    When isotopes are enabled, D and T are allowed but discouraged:
    the algorithm prefers solutions that use fewer D/T tokens.
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


def convert_text(text: str, show_full: bool, enable_isotopes: bool) -> str:
    lookup = build_element_lookup(enable_isotopes)
    symbols = find_symbol_sequence(text, lookup, enable_isotopes)
    if symbols is None:
        return explain_failure(text, lookup)

    if not show_full:
        return format_atomic_ids(symbols, lookup)

    return (
        f"{format_symbols(symbols)}\n"
        f"{format_element_names(symbols, lookup)}\n"
        f"{format_atomic_ids(symbols, lookup)}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert text to chemical element symbols or atomic IDs."
    )
    parser.add_argument(
        "-f",
        "--full",
        action="store_true",
        help="Output symbols, element names, and atomic IDs.",
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
    result = convert_text(args.text, args.full, args.isotopes)
    print(result)


if __name__ == "__main__":  # pragma: no cover
    main()
