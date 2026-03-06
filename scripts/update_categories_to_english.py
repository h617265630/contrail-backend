#!/usr/bin/env python3
"""Update default *system* category names/descriptions to English.

- Safe by default: use --dry-run to preview.
- Only updates system categories (owner_user_id IS NULL) for known codes.
- Does NOT change id/code.
"""

import argparse
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from sqlalchemy import create_engine, text


DEFAULT_CATEGORY_EN = {
    "ai": ("AI", "AI related resources"),
    "design": ("Design", "Design related resources"),
    "ui": ("UI", "UI design related resources"),
    "frontend": ("Frontend", "Frontend development related resources"),
    "backend": ("Backend", "Backend development related resources"),
    "handmade": ("Handmade", "Handmade / craft related resources"),
    "other": ("Other", "Other resources"),
}


def fetch_categories(conn):
    rows = conn.execute(
        text(
            """
            SELECT id, code, name, description, is_system, owner_user_id
            FROM categories
            WHERE code = ANY(:codes)
            ORDER BY id
            """
        ),
        {"codes": list(DEFAULT_CATEGORY_EN.keys())},
    ).fetchall()
    return rows


def main():
    parser = argparse.ArgumentParser(description="Update default system category names to English")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        before = fetch_categories(conn)
        print("=" * 60)
        print(f"Found {len(before)} matching categories (by code)")
        print("=" * 60)
        for row in before:
            owner = row.owner_user_id
            owner_info = f"owner_user_id={owner}" if owner is not None else "system(owner_user_id=NULL)"
            print(
                f"- id={row.id}, code={row.code}, name={row.name}, description={row.description}, is_system={row.is_system} ({owner_info})"
            )

        updates = []
        for code, (en_name, en_desc) in DEFAULT_CATEGORY_EN.items():
            updates.append({"code": code, "name": en_name, "description": en_desc})

        if args.dry_run:
            print("\nDRY RUN: no changes applied.")
            print("Planned updates (system categories only):")
            for u in updates:
                print(f"- code={u['code']}: name -> {u['name']}, description -> {u['description']}")
            return

        total = 0
        for u in updates:
            res = conn.execute(
                text(
                    """
                    UPDATE categories
                    SET name = :name,
                        description = :description,
                        is_system = TRUE
                    WHERE code = :code
                      AND owner_user_id IS NULL
                    """
                ),
                u,
            )
            total += int(res.rowcount or 0)

        conn.commit()

        print("\n=" * 60)
        print(f"✅ Updated rows: {total}")

        after = fetch_categories(conn)
        print("\nAfter:")
        for row in after:
            owner = row.owner_user_id
            owner_info = f"owner_user_id={owner}" if owner is not None else "system(owner_user_id=NULL)"
            print(
                f"- id={row.id}, code={row.code}, name={row.name}, description={row.description}, is_system={row.is_system} ({owner_info})"
            )


if __name__ == "__main__":
    main()
