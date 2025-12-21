# Element Text Converter

This repository contains two small, complementary Python command-line utilities for converting between **text**, **chemical element symbols**, and **atomic IDs**.

Together, they allow round-trip conversion:

Text ⇄ Element symbols ⇄ Atomic IDs

Both scripts are standalone, dependency-free, and compatible with Python 3.9+.

---

## Atomic IDs and optional Hydrogen isotopes

By default, atomic IDs are the standard integers:

- `1` through `118`

Optionally, you can enable Hydrogen isotopes with `--isotopes`:

- Hydrogen: `H` → `1`
- Deuterium: `D` → `1.2`
- Tritium: `T` → `1.3`

**Important:** `D` and `T` are only recognized/accepted when `--isotopes` is provided.

---

## Script 1: `to_elements.py`

### Purpose

Convert an input string into a sequence of **chemical element symbols** (if possible), and optionally display the corresponding **element names** and **atomic IDs**.

Whitespace in the input is ignored.

### How it works

The script attempts to decompose the input text into valid 1- or 2-letter chemical element symbols using a dynamic-programming approach. If no valid decomposition exists, a clear error message is produced indicating where the conversion fails.

### Usage

```bash
./to_elements.py [--isotopes] [--full] TEXT
