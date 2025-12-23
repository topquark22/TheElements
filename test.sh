#!/usr/bin/env bash
set -euo pipefail

# Simple test runner for:
#   to_elements.py
#   from_elements.py
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

echo "== Test 1: whitespace ignored (basic) =="
# "Geoffrey" example from earlier: expect specific output in default mode (atomic IDs)
out="$(run_ok "$PYTHON" "$TO" Geoffrey)"
# The exact decomposition can vary depending on DP tie-breaks; but with current DP (1/2-letter)
# it should consistently find: Ge O F F Re Y -> 32 8 9 9 75 39
assert_eq "$out" "32 8 9 9 75 39"

echo "== Test 2: Ignore spaces =="
out="$(run_ok "$PYTHON" "$TO" "Ge  off    rey")"
assert_eq "$out" "32 8 9 9 75 39"

echo "== Test 3: Ignore all nonalphabetic characters =="
out="$(run_ok "$PYTHON" "$TO" "Ge.off?r:ey/")"
assert_eq "$out" "32 8 9 9 75 39"

echo "== Test 4: full mode outputs symbols + atomic IDs + names =="
# order of flags does not matter
out="$(run_ok "$PYTHON" "$TO" -s -m -n 'Geoffrey')"
# Expect 3 lines:
# 1) symbols  2) atomic numbers 3) element names
expected=$'Ge O F F Re Y\n32 8 9 9 75 39\nGermanium Oxygen Fluorine Fluorine Rhenium Yttrium'
assert_eq "$out" "$expected"

echo "== Test 5: Accept 1.2/1.3 in $FROM =="
out="$(run_ok "$PYTHON" "$FROM" 1 1.2 1.3 8)"
assert_eq "$out" "HDTO"

echo "== Test 6: isotopes OFF does not match D/T as symbols in text converter =="
# Without -t, "HDT" should fail because D and T aren't in the symbol table.
out="$(run_ok "$PYTHON" "$TO" HDT)"
assert_contains "$out" "Conversion not possible" "D/T should be unavailable without -t"

echo "== Test 7: isotopes ON matches D/T and prints correct atomic IDs =="
out="$(run_ok "$PYTHON" "$TO" -i HDT)"
assert_eq "$out" "1 1.2 1.3"

echo "== Test 8: isotopes ON matches D/T and prints correct full output =="
out="$(run_ok "$PYTHON" "$TO" -s -m -n -i HDT)"
expected=$'H D T\n1 1.2 1.3\nHydrogen Deuterium Tritium'
assert_eq "$out" "$expected"

echo "== Test 9: 'DsRa' should FAIL without isotopes enabled (negative test) =="
out="$(run_ok "$PYTHON" "$TO" DAr)"
assert_contains "$out" "Conversion not possible" "Expected DAr to fail when parsed as D + Ar"

echo "== Test 10: 'DsRa' should PASS (Ds + Ra) =="
out="$(run_ok "$PYTHON" "$TO" -s DsRa)"
first_line="${out%%$'\n'*}"
assert_eq "$first_line" "Ds Ra" "Expected Darmstadtium + Radium decomposition"

echo "== Test 11: atomic_to_symbols basic round-trip =="
ids="$(run_ok "$PYTHON" "$TO" Geoffrey)"
sym="$(run_ok "$PYTHON" "$FROM" $ids)"
assert_eq "$sym" "GeOFFReY"

echo "== Test 12: range validation =="
out="$(run_fail "$PYTHON" "$FROM" 0)"
assert_contains "$out" "out of range" "0 should be rejected"
out="$(run_fail "$PYTHON" "$FROM" 119)"
assert_contains "$out" "out of range" "119 should be rejected"

echo "== Test 13: invalid isotope token rejection =="
out="$(run_fail "$PYTHON" "$FROM" 1.4)"
assert_contains "$out" "not a valid atomic ID" "1.4 should be rejected"

echo "== Test 14: non-decimal token rejection =="
out="$(run_fail "$PYTHON" "$FROM" 12x 3)"
assert_contains "$out" "not a valid atomic ID" "12x should be rejected"

echo "== Test 15: empty/whitespace token should fail as 'No atomic IDs provided.' =="
out="$(run_fail "$PYTHON" "$FROM" "")"
assert_contains "$out" "No atomic IDs provided." "empty token should be treated as no input"

echo "== Test 16: does converter fail cleanly on impossible string =="
out="$(run_ok "$PYTHON" "$TO" "zzzz")"
assert_contains "$out" "Conversion not possible" "impossible conversion should explain failure"

echo
echo "ALL TESTS PASSED"
