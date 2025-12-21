#!/usr/bin/env python3

"""
Convert a whitespace-separated sequence of atomic IDs into concatenated
element symbols.

Valid atomic IDs:
  - integers 1..118
  - "1.2" (Deuterium)
  - "1.3" (Tritium)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class Element:
    symbol: str
    name: str
    atomic_id: str


ELEMENTS: Sequence[Element] = (
    Element("H", "Hydrogen", "1"),
    Element("D", "Deuterium", "1.2"),
    Element("T", "Tritium", "1.3"),
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

ATOMIC_ID_TO_SYMBOL: Dict[str, str] = {e.atomic_id: e.symbol for e in ELEMENTS}


def parse_atomic_ids(tokens: Sequence[str]) -> List[str]:
    if not tokens:
        raise ValueError("No atomic IDs provided.")

    ids: List[str] = []

    for idx, raw in enumerate(tokens, start=1):
        s = raw.strip()
        if not s:
            continue

        if s.isdigit():
            value = int(s)
            if not (1 <= value <= 118):
                raise ValueError(f"Token #{idx} value {value} is out of range (1..118).")
            ids.append(str(value))
            continue

        if s in ("1.2", "1.3"):
            ids.append(s)
            continue

        raise ValueError(
            f'Token #{idx} "{raw}" is not a valid atomic ID. '
            'Use 1..118, "1.2", or "1.3".'
        )

    if not ids:
        raise ValueError("No atomic IDs provided.")

    return ids


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert atomic IDs to concatenated element symbols."
    )
    parser.add_argument("ids", nargs="+")
    args = parser.parse_args()

    try:
        ids = parse_atomic_ids(args.ids)
        print("".join(ATOMIC_ID_TO_SYMBOL[i] for i in ids))
    except ValueError as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
