#!/usr/bin/env python3
"""Command-line helper for generating Quantum Fingerprints."""
import argparse
import json
import sys
from pathlib import Path

# Ensure repository root is on the Python path when executed via relative path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from advanced_phases import QuantumFingerprint, DecentralizedBackupManager


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Quantum Fingerprint for a file"
    )
    parser.add_argument("artifact", help="Path to artifact to fingerprint")
    parser.add_argument(
        "--version", default="1.0.0", help="Version label for the artifact"
    )
    parser.add_argument(
        "--backup", action="store_true", help="Backup the file after fingerprinting"
    )
    args = parser.parse_args()

    qf = QuantumFingerprint(args.artifact, args.version)
    result = qf.mint()
    print(json.dumps(result, indent=2))

    if args.backup:
        mgr = DecentralizedBackupManager()
        dest = mgr.backup_file(args.artifact)
        print(f"Backup saved to {dest}")


if __name__ == "__main__":
    main()
