#!/usr/bin/env bash
# Run all test cases for Problem 1 and Problem 2

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
P1="$SCRIPT_DIR/problem1/threecsp.py"
P2="$SCRIPT_DIR/problem2/reduce.py"
TESTS="$SCRIPT_DIR/tests"

sep() { printf '%0.s-' {1..60}; echo; }

echo "========================================"
echo "  PROBLEM 1: 3-Color Shortest Path"
echo "========================================"
for i in 1 2 3 4 5; do
    sep
    echo "Test Case $i  ($(basename "$TESTS/p1_tc$i.txt"))"
    sep
    cat "$TESTS/p1_tc$i.txt"
    sep
    python3 "$P1" "$TESTS/p1_tc$i.txt"
    echo
done

echo
echo "========================================"
echo "  PROBLEM 2: DGSP -> 3CSP Reduction"
echo "========================================"
for i in 1 2 3 4 5; do
    sep
    echo "Test Case $i  ($(basename "$TESTS/p2_tc$i.txt"))"
    sep
    cat "$TESTS/p2_tc$i.txt"
    sep
    echo "[Reduced 3CSP instance]"
    python3 "$P2" "$TESTS/p2_tc$i.txt"
    sep
    echo "[Running threecsp on reduced instance]"
    python3 "$P2" "$TESTS/p2_tc$i.txt" | python3 "$P1"
    echo
done
