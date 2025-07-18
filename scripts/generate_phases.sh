#!/usr/bin/env bash
set -euo pipefail

# generate_phases.sh — scaffold modules & tests for phases 1–200 in steps of 10

MODULES_DIR="modules"
TESTS_DIR="tests"

for start in $(seq 1 10 191); do
  end=$((start + 9))
  mod="phase_${start}_${end}"
  mod_dir="$MODULES_DIR/$mod"
  test_file="$TESTS_DIR/test_${mod}.py"

  mkdir -p "$mod_dir"
  cat > "$mod_dir/__init__.py" <<EOPY
# stub for ${mod}

def run():
    """
    Phase ${start}–${end} stub
    """
    return None
EOPY

  cat > "$mod_dir/${mod}.py" <<EOPY
"""
Module stub for ${mod}.
"""

def run():
    # TODO: implement phase ${start}–${end}
    return None
EOPY

  mkdir -p "$TESTS_DIR"
  cat > "$test_file" <<EOPY
from modules.${mod}.${mod} import run

def test_phase_${start}_${end}():
    assert run() is None
EOPY

  echo "Created stub $mod_dir/ and test $test_file"
done

echo "✅ All phase stubs generated."
