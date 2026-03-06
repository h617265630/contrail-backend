#!/usr/bin/env python3
"""Translate existing categories.name (Chinese -> English) and write back to DB.

Notes:
- Safe by default: run with --dry-run to preview.
- Updates rows in-place (does NOT insert duplicates) because categories.name is unique.
- Only updates names that match the built-in mapping. Unmapped names are reported.

Example:
  python backend/scripts/translate_category_names_to_english.py --dry-run
  python backend/scripts/translate_category_names_to_english.py --apply
"""

import argparse
import re
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from sqlalchemy import create_engine, text


ZH_TO_EN = {
    "设计": "Design",
    "前端": "Frontend",
    "后端": "Backend",
    "手工": "Handmade",
    "其他": "Other",
    "人工智能": "AI",
    "产品": "Product",
    "运营": "Operations",
    "市场": "Marketing",
    "数据": "Data",
    "数据分析": "Data Analysis",
    "管理": "Management",
    "写作": "Writing",
    "英语": "English",
    "日语": "Japanese",
    "韩语": "Korean",
}

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def looks_chinese(s: str) -> bool:
    return bool(CJK_RE.search(s or ""))


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate category names to English")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--apply", action="store_true", help="Apply changes to database")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        args.dry_run = True

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, code, name, description, is_system, owner_user_id
                FROM categories
                ORDER BY id
                """
            )
        ).fetchall()

        to_update = []
        unmapped = []

        for r in rows:
            name = (r.name or "").strip()
            if not name:
                continue
            if not looks_chinese(name):
                continue

            translated = ZH_TO_EN.get(name)
            if translated:
                to_update.append(
                    {
                        "id": int(r.id),
                        "code": r.code,
                        "old": name,
                        "new": translated,
                    }
                )
            else:
                unmapped.append({"id": int(r.id), "code": r.code, "name": name})

        print("=" * 60)
        print(f"Total categories: {len(rows)}")
        print(f"Chinese-looking names: {len(to_update) + len(unmapped)}")
        print(f"Mappable: {len(to_update)}")
        print(f"Unmapped: {len(unmapped)}")
        print("=" * 60)

        if to_update:
            print("Planned updates:")
            for u in to_update:
                print(f"- id={u['id']}, code={u['code']}: '{u['old']}' -> '{u['new']}'")
        if unmapped:
            print("\nUnmapped (no change):")
            for u in unmapped:
                print(f"- id={u['id']}, code={u['code']}: '{u['name']}'")

        if args.dry_run:
            print("\nDRY RUN: no changes applied.")
            return

        # Apply
        updated = 0
        for u in to_update:
            res = conn.execute(
                text("UPDATE categories SET name = :new WHERE id = :id"),
                {"id": u["id"], "new": u["new"]},
            )
            updated += int(res.rowcount or 0)

        conn.commit()
        print("\n=" * 60)
        print(f"✅ Updated rows: {updated}")


if __name__ == "__main__":
    main()
