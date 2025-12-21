#!/usr/bin/env bash
set -euo pipefail

# Simple test runner for:
#   element_text_converter.py
#   atomic_to_symbols.py
#
# Usage:
#   bash test.sh
#
# Assumes scripts are in the current directory.

PYTHON="${PYTHON:-python3}"

TO="./to_elements.py"
FROM="./from_elements.py"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_eq() {
  local got="$1"
  local expected="$2"
  local msg="${3:-}"
  if [[ "$got" != "$expected" ]]; then
    echo "---- GOT ----"
    printf "%s\n" "$got"
    echo "---- EXPECTED ----"
    printf "%s\n" "$expected"
    [[ -n "$msg" ]] && echo "---- CONTEXT ----" && echo "$msg"
    fail "assert_eq failed"
  fi
}

assert_contains() {
  local hay="$1"
  local needle="$2"
  local msg="${3:-}"
  if [[ "$hay" != *"$needle"* ]]; then
    echo "---- OUTPUT ----"
    printf "%s\n" "$hay"
    echo "---- EXPECTED TO CONTAIN ----"
    printf "%s\n" "$needle"
    [[ -n "$msg" ]] && echo "---- CONTEXT ----" && echo "$msg"
    fail "assert_contains failed"
  fi
}

run_ok() {
  # Run command, capture stdout, ensure exit code 0
  local out
  out="$("$@")"
  printf "%s" "$out"
}

run_fail() {
  # Run command, capture stderr+stdout, ensure exit code nonzero
  local out
  set +e
  out="$("$@" 2>&1)"
  local code=$?
  set -e
  if [[ $code -eq 0 ]]; then
    echo "---- OUTPUT ----"
    printf "%s\n" "$out"
    fail "expected failure exit code, got 0"
  fi
  printf "%s" "$out"
}

echo "== Sanity: python and files exist =="
command -v "$PYTHON" >/dev/null || fail "python not found: $PYTHON"
[[ -f "$TO" ]] || fail "missing $TO"
[[ -f "$FROM" ]] || fail "missing $FROM"
[[ -f "./elements_data.py" ]] || fail "missing ./elements_data.py"

echo "== Ensure scripts are executable (optional) =="
chmod +x "$TO" "$FROM" || true

echo "== Test: whitespace ignored (basic) =="
# "Geoffrey" example from earlier: expect specific output in default mode (atomic IDs)
out="$(run_ok "$PYTHON" "$TO" Geoffrey)"
# The exact decomposition can vary depending on DP tie-breaks; but with current DP (1/2-letter)
# it should consistently find: Ge O F F Re Y -> 32 8 9 9 75 39
assert_eq "$out" "32 8 9 9 75 39"

out="$(run_ok "$PYTHON" "$TO" "Ge  off   rey")"
assert_eq "$out" "32 8 9 9 75 39"

echo "== Test: full mode outputs symbols + names + atomic IDs =="
out="$(run_ok "$PYTHON" "$TO" --full Geoffrey)"
# Expect 3 lines.
# 1) symbols  2) names  3) atomic IDs
expected=$'Ge O F F Re Y\nGermanium Oxygen Fluorine Fluorine Rhenium Yttrium\n32 8 9 9 75 39'
assert_eq "$out" "$expected"

echo "== Test: isotopes OFF rejects 1.2/1.3 in atomic_to_symbols =="
out="$(run_fail "$PYTHON" "$FROM" 1.2 8)"
assert_contains "$out" "Error:" "should reject isotope id without -i/--isotopes"

echo "== Test: isotopes ON accepts 1.2/1.3 in atomic_to_symbols =="
out="$(run_ok "$PYTHON" "$FROM" -i 1 1.2 1.3 8)"
assert_eq "$out" "HDTO"

echo "== Test: isotopes OFF does not match D/T as symbols in text converter =="
# Without -i, "HDT" should fail because D and T aren't in the symbol table.
out="$(run_ok "$PYTHON" "$TO" HDT)"
assert_contains "$out" "Conversion not possible" "D/T should be unavailable without -i"

echo "== Test: isotopes ON matches D/T and prints correct atomic IDs =="
out="$(run_ok "$PYTHON" "$TO" -i HDT)"
assert_eq "$out" "1 1.2 1.3"

out="$(run_ok "$PYTHON" "$TO" -i --full HDT)"
expected=$'H D T\nHydrogen Deuterium Tritium\n1 1.2 1.3'
assert_eq "$out" "$expected"

echo "== Test: 'Dara' should FAIL with isotopes enabled (negative test) =="
out="$(run_ok "$PYTHON" "$TO" -i Dara)"
assert_contains "$out" "Conversion not possible" "Expected Dara to fail when parsed as D + Ar + ..."

echo "== Test: 'Dsra' should PASS (Ds + Ra) =="
out="$(run_ok "$PYTHON" "$TO" -i --full Dsra)"
first_line="${out%%$'\n'*}"
assert_eq "$first_line" "Ds Ra" "Expected Darmstadtium + Radium decomposition"

echo "== Test: atomic_to_symbols basic round-trip =="
ids="$(run_ok "$PYTHON" "$TO" Geoffrey)"
sym="$(run_ok "$PYTHON" "$FROM" $ids)"
assert_eq "$sym" "GeOFFReY"

echo "== Test: range validation =="
out="$(run_fail "$PYTHON" "$FROM" 0)"
assert_contains "$out" "out of range" "0 should be rejected"
out="$(run_fail "$PYTHON" "$FROM" 119)"
assert_contains "$out" "out of range" "119 should be rejected"

echo "== Test: non-decimal token rejection =="
out="$(run_fail "$PYTHON" "$FROM" 12x 3)"
assert_contains "$out" "not a valid atomic ID" "12x should be rejected"

echo "== Test: empty/whitespace token should fail as 'No atomic IDs provided.' =="
out="$(run_fail "$PYTHON" "$FROM" "")"
assert_contains "$out" "No atomic IDs provided." "empty token should be treated as no input"

echo "== Test: only-whitespace input to text converter (ignored whitespace) =="
out="$(run_ok "$PYTHON" "$TO" "   ")"
# find_symbol_sequence returns [] => output is empty line in atomic-id-only mode.
# print(result) prints a blank line; captured output will be empty string.
assert_eq "$out" ""

echo "== Test: does converter fail cleanly on impossible string =="
out="$(run_ok "$PYTHON" "$TO" "zzzz")"
assert_contains "$out" "Conversion not possible" "impossible conversion should explain failure"

echo
echo "ALL TESTS PASSED"
