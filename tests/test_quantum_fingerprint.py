from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quantum_fingerprint import generate_sbom


def test_generate_sbom(tmp_path, monkeypatch):
    req = tmp_path / 'requirements.txt'
    req.write_text('flask==2.0.0')
    monkeypatch.chdir(tmp_path)
    out = generate_sbom('out.json')
    assert Path(out).exists()
