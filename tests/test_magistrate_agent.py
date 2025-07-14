from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from magistrate import review_scene


def test_review_scene(tmp_path, monkeypatch):
    log = tmp_path / "log.json"
    log.write_text(json.dumps({"scene_id": "a"}))
    ledger = tmp_path / "ledger.yaml"
    monkeypatch.setitem(review_scene.__globals__, "SCENE_LOG", log)
    monkeypatch.setitem(review_scene.__globals__, "VERDICT_LEDGER", ledger)

    verdict = review_scene("a")
    assert verdict["ruling"] == "UPHELD"
    assert ledger.exists()
