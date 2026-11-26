"""Static checks on the SQL DDL (no database needed)."""

import re

from fse.db import schema_files
from fse.ingest.transfermarkt import CSV_FILES, table_for
from fse.ingest.wyscout import COLUMNS


def _ddl() -> str:
    return "\n".join(p.read_text() for p in schema_files())


def test_schema_files_are_ordered_and_start_with_schemas():
    names = [p.name for p in schema_files()]
    assert names == sorted(names)
    assert names[0] == "001_schemas.sql"


def test_every_transfermarkt_csv_has_a_raw_table():
    ddl = _ddl()
    for stem in CSV_FILES:
        assert f"CREATE TABLE IF NOT EXISTS raw.{table_for(stem)} (" in ddl


def test_wyscout_copy_columns_match_ddl():
    ddl = _ddl()
    for table, cols in COLUMNS.items():
        block = re.search(rf"CREATE TABLE IF NOT EXISTS {re.escape(table)} \((.*?)\n\);", ddl, re.S)
        assert block, table
        ddl_cols = [
            line.split()[0]
            for line in block.group(1).splitlines()
            if line.strip() and not line.strip().startswith("--")
        ]
        assert ddl_cols == [c.strip() for c in cols.split(",")], table
