"""
check_tables.py

工具：检查后端数据库（基于项目配置的 DATABASE_URL），输出 public schema 的表、字段、主键、外键和索引关系。

用法示例：
  # 在项目 backend 目录下运行（PowerShell / cmd）
  python tools\check_tables.py
  python tools\check_tables.py --format json
  python tools\check_tables.py --table link_resources

注意：脚本会把 `backend` 目录加入 sys.path 以便导入 `app.core.config.settings`。
"""

import sys
from pathlib import Path
import argparse
import json
from typing import Any, Dict, List

# Ensure project package import works when run from backend directory
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from app.core.config import settings
except Exception as e:
    print(f"Failed to import project settings: {e}")
    sys.exit(2)

try:
    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.engine import Engine
except Exception as e:
    print(f"Missing SQLAlchemy dependency: {e}")
    print("Ensure SQLAlchemy is installed in your environment")
    sys.exit(3)


def get_engine(url: str) -> Engine:
    return create_engine(url)


def list_tables(engine: Engine) -> List[str]:
    inspector = inspect(engine)
    return inspector.get_table_names(schema='public')


def get_columns(engine: Engine, table: str) -> List[Dict[str, Any]]:
    inspector = inspect(engine)
    cols = inspector.get_columns(table, schema='public')
    # Normalize types to simple dicts
    out = []
    for c in cols:
        out.append({
            'column_name': c.get('name'),
            'data_type': str(c.get('type')),
            'is_nullable': c.get('nullable'),
            'column_default': c.get('default'),
            'character_maximum_length': c.get('type').length if hasattr(c.get('type'), 'length') else None,
        })
    return out


def get_primary_key(engine: Engine, table: str) -> List[str]:
    inspector = inspect(engine)
    pk = inspector.get_pk_constraint(table, schema='public')
    return pk.get('constrained_columns', [])


def get_foreign_keys(engine: Engine, table: str) -> List[Dict[str, Any]]:
    inspector = inspect(engine)
    fks = inspector.get_foreign_keys(table, schema='public')
    out = []
    for fk in fks:
        # fk dict contains: constrained_columns, referred_table, referred_columns, name
        cols = fk.get('constrained_columns', [])
        refs = fk.get('referred_columns', [])
        for i, col in enumerate(cols):
            out.append({
                'constraint': fk.get('name'),
                'column': col,
                'foreign_table': fk.get('referred_table'),
                'foreign_column': refs[i] if i < len(refs) else None,
            })
    return out


def get_indexes(engine: Engine, table: str) -> List[Dict[str, Any]]:
    inspector = inspect(engine)
    idxs = inspector.get_indexes(table, schema='public')
    return [{'name': i.get('name'), 'column_names': i.get('column_names'), 'unique': i.get('unique')} for i in idxs]


def inspect_db(url: str, target_table: str | None = None) -> Dict[str, Any]:
    out: Dict[str, Any] = {"database_url": url, "tables": {}}
    try:
        engine = get_engine(url)
    except Exception as e:
        out["error"] = f"Failed to create engine: {e}"
        return out

    try:
        tables = list_tables(engine)
        if target_table:
            if target_table not in tables:
                out["error"] = f"Table '{target_table}' not found in public schema"
                engine.dispose()
                return out
            tables = [target_table]

        for t in tables:
            cols = get_columns(engine, t)
            pk = get_primary_key(engine, t)
            fks = get_foreign_keys(engine, t)
            idxs = get_indexes(engine, t)
            out["tables"][t] = {"columns": cols, "primary_key": pk, "foreign_keys": fks, "indexes": idxs}

        # Build simple relationship map (which table -> referenced tables)
        relations = {}
        for t, data in out["tables"].items():
            refs = []
            for fk in data["foreign_keys"]:
                refs.append({"column": fk["column"], "references": f"{fk['foreign_table']}.{fk['foreign_column']}"})
            relations[t] = refs
        out["relations"] = relations

    finally:
        try:
            engine.dispose()
        except Exception:
            pass

    return out


def print_human(out: Dict[str, Any]):
    if "error" in out:
        print("ERROR:", out["error"])
        return
    print("Database:", out.get("database_url", "-"))
    print()
    for t, data in out["tables"].items():
        print(f"Table: {t}")
        print("  Columns:")
        for c in data["columns"]:
            name = c.get("column_name")
            dtype = c.get("data_type")
            nullable = c.get("is_nullable")
            default = c.get("column_default")
            length = c.get("character_maximum_length")
            extras = []
            if length:
                extras.append(f"len={length}")
            if default:
                extras.append(f"default={default}")
            print(f"    - {name}: {dtype} nullable={nullable} {' '.join(extras)}")
        if data.get("primary_key"):
            print("  Primary Key:", ", ".join(data.get("primary_key", [])))
        if data.get("foreign_keys"):
            print("  Foreign Keys:")
            for fk in data.get("foreign_keys", []):
                print(f"    - {fk['constraint']}: {fk['column']} -> {fk['foreign_table']}.{fk['foreign_column']}")
        if data.get("indexes"):
            print("  Indexes:")
            for idx in data.get("indexes", []):
                cols = idx.get('column_names') or []
                uniq = 'unique' if idx.get('unique') else ''
                print(f"    - {idx['name']}: columns={cols} {uniq}")
        print()

    print("Relations summary:")
    for t, refs in out.get("relations", {}).items():
        if not refs:
            print(f"  {t}: (no outgoing FKs)")
        else:
            print(f"  {t} -> {', '.join(r['references'] for r in refs)}")


def main():
    parser = argparse.ArgumentParser(description="Inspect database tables and relationships (public schema)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--table", help="Only inspect a single table")
    args = parser.parse_args()

    url = getattr(settings, "DATABASE_URL", None)
    if not url:
        print("DATABASE_URL not found in app.core.config.settings")
        sys.exit(1)

    result = inspect_db(url, target_table=args.table)
    if args.format == "json":
        print(json.dumps(result, default=str, indent=2, ensure_ascii=False))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
