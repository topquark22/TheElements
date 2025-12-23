# Element Text Converter

This repository contains two small, complementary Python command-line utilities for converting between **text**, **chemical element symbols**, and **atomic numbers**.

Together, they allow round-trip conversion:

Text ⇄ Element symbols ⇄ Atomic numbers

Both scripts are standalone, dependency-free, and compatible with Python 3.9+.

---

## Script 1: `to_elements.py`

### Purpose

Convert an input string into a sequence of **chemical element symbols** (if possible), and optionally display the corresponding **element names** and **atomic numbers**.

Whitespace in the input is ignored.

### How it works

The script attempts to decompose the input text into valid 1- or 2-letter chemical element symbols using a dynamic-programming approach. If no valid decomposition exists, a clear error message is produced indicating where the conversion fails.

### Usage

```
./to_elements.py [--full | -f] [--isotopes | -i] TEXT
```

### Options

|Option|Description|Default|
|------|----------|-------|
|--full, -f|Output symbols, element names, and atomic numbers|Output atomic numbers only|
|--isotopes, -i|Availability of the symbols D (Deuterium), T (Tritium)|D, T not available|

If the latter option is enabled, then D is represented by 1.2, and T by 1.3.

### Examples

Convert text to atomic numbers (default mode):

```
$ ./to_elements.py Geoffrey
32 8 9 9 75 39
```

Full output mode:

```
$ ./to_elements.py --full Geoffrey
Ge O F F Re Y
Germanium Oxygen Fluorine Fluorine Rhenium Yttrium
32 8 9 9 75 39
```

Whitespace is ignored in the input string.

If the conversion is not possible (because element symbols do not exist for those letters, then:

```
$ ./to_elements.py Hello
Conversion not possible. Letters starting at position 3 ("llo") cannot be matched with element symbols.
```
---

## Script 2: `from_elements.py`

### Purpose

Convert a whitespace-separated sequence of atomic numbers (decimal) into a concatenated string of element symbols.

This is the inverse operation of the first script’s atomic-number output.

### Validation Rules

The script rejects input if any token:
- Is not a valid decimal integer, or one of the special isotope values "1.2" or "1.3"
- Is outside the range 1–118
- Is missing or empty

### Usage
```
./from_elements.py NUMBER [NUMBER ...]
```

## For reference

[Periodic table of the elements](Elements.md) as used in the context of this project.

## *Footnote*

*Dedicated to Tom Lehrer, and his amazing song "The Elements." Unfortunately, Tom's name does not pass the algorithm, because there's no element with name T or To, and not even Thomas works, unfortunately. Does your name work? My name does (but not my middle name.) Let me know in the discussions.*

*Here's an interesting question: We know that not every name will work. But, what is the percentage that does? It seems to be pretty small.*

*32 8 9 9 75 39 9 13 19*

