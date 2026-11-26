from pathlib import Path

from fse.config import get_settings


def test_settings_defaults(monkeypatch):
    for var in (
        "FSE_DATA_ROOT",
        "FSE_DB_HOST",
        "FSE_DB_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ):
        monkeypatch.delenv(var, raising=False)
    s = get_settings()
    assert s.data_root == Path("~/Documents/data-sc").expanduser()
    assert s.conninfo == "host=localhost port=5432 dbname=fse user=fse"


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("FSE_DATA_ROOT", "/tmp/data")
    monkeypatch.setenv("FSE_DB_PORT", "5433")
    monkeypatch.setenv("POSTGRES_PASSWORD", "x")
    s = get_settings()
    assert s.data_root == Path("/tmp/data")
    assert "port=5433" in s.conninfo
    assert s.conninfo.endswith("password=x")
