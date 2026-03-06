"""
validate_tables.py

检查数据库表结构是否符合若干最佳实践与简单的范式规则，并给出可执行建议。

检查项（非穷尽）：
- 检查以 `_id` 结尾的列是否存在外键约束
- 检查存在 `*_id` 外键同时又保留 `*_name` 文本字段（可能冗余）
- 检查关联表（有两个 FK）的主键设计（是否同时存在单独的自增 id，可能冗余）
- 检查布尔字段是否允许 NULL（通常应设为 NOT NULL 并有默认值）
- 检查可能的反范式（TEXT/JSON 列，可能存储结构化数据）
- 检查外键列是否有索引（建议为 FK 创建索引以优化 JOIN）

用法：在 `backend` 目录运行：
  conda run -n shortvid python tools\validate_tables.py --format json
或
  python tools\validate_tables.py

输出：人类可读文本或 JSON
"""

import sys
from pathlib import Path
import json
import argparse
from typing import Dict, Any, List

# Ensure project package import works
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from app.core.config import settings
except Exception as e:
    print(f"Failed to import settings: {e}")
    sys.exit(2)

try:
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.engine import Engine
except Exception as e:
    print(f"Missing SQLAlchemy: {e}")
    sys.exit(3)


def get_engine(url: str) -> Engine:
    return create_engine(url)


def analyze(url: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"database_url": url, "issues": [], "summary": {}}
    try:
        engine = get_engine(url)
    except Exception as e:
        out["error"] = f"Failed to create engine: {e}"
        return out

    insp = inspect(engine)
    tables = insp.get_table_names(schema='public')

    # gather schema info
    schema = {}
    for t in tables:
        cols = insp.get_columns(t, schema='public')
        pk = insp.get_pk_constraint(t, schema='public').get('constrained_columns', [])
        fks = insp.get_foreign_keys(t, schema='public')
        idxs = insp.get_indexes(t, schema='public')
        schema[t] = {"columns": cols, "primary_key": pk, "foreign_keys": fks, "indexes": idxs}

    # Helper lookups
    fk_map = {}  # table.column -> referred_table.referred_column
    fk_cols_by_table = {t: set() for t in tables}
    for t, data in schema.items():
        for fk in data['foreign_keys']:
            cols = fk.get('constrained_columns') or []
            refs = fk.get('referred_columns') or []
            for i, c in enumerate(cols):
                ref_col = refs[i] if i < len(refs) else None
                fk_map[f"{t}.{c}"] = f"{fk.get('referred_table')}.{ref_col}"
                fk_cols_by_table[t].add(c)

    # Rule A: _id columns without FK
    for t, data in schema.items():
        col_names = [c['name'] for c in data['columns']]
        for c in col_names:
            if c.endswith('_id'):
                key = f"{t}.{c}"
                if key not in fk_map:
                    out['issues'].append({
                        'severity': 'warning',
                        'table': t,
                        'column': c,
                        'rule': 'missing_foreign_key',
                        'message': f"Column {c} in {t} looks like a foreign key but has no FK constraint",
                        'suggestion': 'Add an explicit FOREIGN KEY constraint or document why this is denormalized.'
                    })

    # Rule B: redundant *_name when *_id exists (same table)
    for t, data in schema.items():
        col_names = set([c['name'] for c in data['columns']])
        for col in col_names:
            if col.endswith('_name'):
                base = col[:-5]
                id_col = base + '_id'
                if id_col in col_names:
                    out['issues'].append({
                        'severity': 'info',
                        'table': t,
                        'column': col,
                        'rule': 'redundant_name_with_id',
                        'message': f"Table {t} contains both {id_col} (FK) and {col} (textual name) - potential redundancy",
                        'suggestion': 'Prefer keeping only the foreign key and join to fetch the name, or ensure name is a snapshot with reason documented.'
                    })

    # Rule C: association tables with surrogate PK
    for t, data in schema.items():
        fk_count = len(data['foreign_keys'])
        has_id_pk = ('id' in data['primary_key'])
        # detect if table looks like pure association (exactly 2 FK columns)
        if fk_count == 2:
            fk_cols = set()
            for fk in data['foreign_keys']:
                fk_cols.update(fk.get('constrained_columns') or [])
            # if there's an 'id' column as PK in addition to composite fks, flag
            if has_id_pk and (len(data['primary_key']) == 1):
                out['issues'].append({
                    'severity': 'notice',
                    'table': t,
                    'rule': 'association_surrogate_pk',
                    'message': f"Table {t} appears to be an association table with 2 FKs but has a single-column surrogate PK {data['primary_key']}",
                    'suggestion': 'Consider using composite PK of the two FK columns or ensure unique constraint exists to prevent duplicates.'
                })

    # Rule D: boolean columns nullable
    for t, data in schema.items():
        for col in data['columns']:
            colname = col['name']
            dtype = str(col.get('type') or '').lower()
            if 'boolean' in dtype or dtype == 'bool':
                if col.get('nullable', True):
                    out['issues'].append({
                        'severity': 'warning',
                        'table': t,
                        'column': colname,
                        'rule': 'nullable_boolean',
                        'message': f"Boolean column {colname} in {t} allows NULL; consider NOT NULL with default",
                        'suggestion': 'Set NOT NULL and a sensible DEFAULT (e.g., false) to avoid tri-state logic.'
                    })

    # Rule E: potential denormalized TEXT/JSON columns
    for t, data in schema.items():
        for col in data['columns']:
            colname = col['name']
            dtype = str(col.get('type') or '').lower()
            if 'json' in dtype or 'text' in dtype or 'jsonb' in dtype:
                # Heuristic: if column name suggests structured content (chapters/metadata) flag it
                if any(k in colname for k in ('meta', 'metadata', 'chapters', 'data', 'payload', 'content')):
                    out['issues'].append({
                        'severity': 'info',
                        'table': t,
                        'column': colname,
                        'rule': 'denormalized_struct',
                        'message': f"Column {colname} in {t} is {dtype} and may contain structured/denormalized data",
                        'suggestion': 'Consider normalizing into related tables if you need to query individual elements, or keep as JSON for flexible metadata.'
                    })

    # Rule F: foreign key columns without index
    # collect indexes per table
    idx_map = {t: set() for t in tables}
    for t, data in schema.items():
        for idx in data['indexes']:
            for cn in idx.get('column_names') or []:
                idx_map[t].add(cn)

    for t, data in schema.items():
        for fk in data['foreign_keys']:
            for c in fk.get('constrained_columns') or []:
                if c not in idx_map.get(t, set()):
                    out['issues'].append({
                        'severity': 'notice',
                        'table': t,
                        'column': c,
                        'rule': 'fk_missing_index',
                        'message': f"Foreign key column {c} in {t} has no index; joins on this column may be slow",
                        'suggestion': 'Add an index on the foreign key column to improve JOIN performance.'
                    })

    out['summary']['table_count'] = len(tables)
    out['schema'] = schema

    try:
        engine.dispose()
    except Exception:
        pass
    return out


def print_human(report: Dict[str, Any]):
    if 'error' in report:
        print('ERROR:', report['error'])
        return
    print('Database:', report.get('database_url'))
    print('Tables:', report.get('summary', {}).get('table_count'))
    print('\nIssues found:')
    if not report.get('issues'):
        print('  (no issues detected)')
    for it in report.get('issues', []):
        print(f"- [{it['severity']}] {it.get('table')}:{it.get('column','')} {it.get('message')}")
        print(f"    Suggestion: {it.get('suggestion')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    url = getattr(settings, 'DATABASE_URL', None)
    if not url:
        print('DATABASE_URL not found in settings')
        sys.exit(1)

    report = analyze(url)
    if args.format == 'json':
        print(json.dumps(report, default=str, indent=2, ensure_ascii=False))
    else:
        print_human(report)


if __name__ == '__main__':
    main()
