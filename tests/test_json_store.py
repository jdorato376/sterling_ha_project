import json
import os
import shutil
from pathlib import Path
import pytest
from json_store import JSONStore, JSONStoreError


def test_read_missing(tmp_path):
    store = JSONStore(tmp_path / "missing.json", default={"foo": 1})
    assert store.read() == {"foo": 1}


def test_read_invalid_json(tmp_path):
    file = tmp_path / "bad.json"
    file.write_text("{bad")
    store = JSONStore(file, default={"bar": 2})
    assert store.read() == {"bar": 2}


def test_read_permission_error(tmp_path, monkeypatch):
    file = tmp_path / "perm.json"
    file.write_text("{}")
    store = JSONStore(file, default={})

    def raiser(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr(Path, "open", raiser)
    assert store.read() == {}


def test_write_atomic(tmp_path, monkeypatch):
    file = tmp_path / "data.json"
    store = JSONStore(file, default={})
    called = {}

    real_replace = os.replace

    def fake_replace(src, dst):
        called["src"] = src
        called["dst"] = dst
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", fake_replace)

    store.write({"x": 1})
    assert json.loads(file.read_text()) == {"x": 1}
    assert Path(called.get("dst")) == file


def test_read_empty_file(tmp_path):
    file = tmp_path / "empty.json"
    file.write_text("")
    store = JSONStore(file, default={"v": 3})
    assert store.read() == {"v": 3}


def test_write_permission_error(tmp_path, monkeypatch):
    file = tmp_path / "data.json"
    store = JSONStore(file, default={})

    def raiser(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr(Path, "open", raiser)
    with pytest.raises(JSONStoreError):
        store.write({"a": 1})


def test_atomic_write_cleanup(tmp_path, monkeypatch):
    file = tmp_path / "data.json"
    store = JSONStore(file, default={})
    tmp_file = file.with_suffix(".json.tmp")

    def bad_replace(src, dst):
        raise OSError("boom")

    monkeypatch.setattr(os, "replace", bad_replace)

    def bad_move(src, dst):
        raise OSError("move fail")

    monkeypatch.setattr(shutil, "move", bad_move)

    with pytest.raises(JSONStoreError):
        store.write({"a": 1})
    assert not tmp_file.exists()


def test_rename_fallback(tmp_path, monkeypatch):
    file = tmp_path / "data.json"
    store = JSONStore(file, default={})
    moved = {}

    def bad_replace(src, dst):
        raise OSError("replace fail")

    real_move = shutil.move

    def good_move(src, dst):
        moved["done"] = True
        return real_move(src, dst)

    monkeypatch.setattr(os, "replace", bad_replace)
    monkeypatch.setattr(shutil, "move", good_move)

    store.write({"b": 2})
    assert json.loads(file.read_text()) == {"b": 2}
    assert moved.get("done")
