import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

# Ensure backend dir is on sys.path so we can import project modules
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.db.database import SessionLocal
# Import users model so SQLAlchemy can resolve ForeignKey('users.id')
import app.models.rbac.user  # noqa: F401
from app.models.user_file import UserFile


_ALLOWED_EXTS = {".md": "md", ".txt": "txt"}


def _sanitize_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "file"


def _sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _default_sources(repo_root: Path) -> list[Path]:
    candidates = [
        repo_root / "backend" / "readme.md",
        repo_root / "database_structure.md",
        repo_root / "frontend" / "app" / "README.md",
        repo_root / "skills" / "ui-ux-pro-max" / "SKILL.md",
        repo_root / "api清单.txt",
        repo_root / "backend" / "整体项目流程.txt",
    ]
    # Only include existing files.
    return [p for p in candidates if p.exists() and p.is_file()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import existing static .md/.txt files into user_files table (copy into backend/static/user_files)."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write files + insert DB rows. Without this flag, runs in dry-run mode.",
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=1,
        help="Owner user_id to assign imported files to. Default: 1",
    )
    parser.add_argument(
        "--root",
        default=str(BASE_DIR.parent),
        help="Repo root path. Default: project root inferred from scripts dir.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional explicit file paths to import. If omitted, imports a small default set from repo.",
    )
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    user_id = int(args.user_id)

    if args.paths:
        sources = [Path(p).expanduser().resolve() for p in args.paths]
    else:
        sources = _default_sources(repo_root)

    sources = [p for p in sources if p.exists() and p.is_file()]
    if not sources:
        print("No source files found to import.")
        return 0

    static_dir = BASE_DIR / "static" / "user_files"
    print(f"Target static dir: {static_dir}")
    print(f"User id: {user_id}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")

    db = SessionLocal()
    try:
        imported = 0
        skipped = 0

        for src in sources:
            ext = src.suffix.lower()
            file_type = _ALLOWED_EXTS.get(ext)
            if not file_type:
                print(f"SKIP (unsupported ext): {src}")
                skipped += 1
                continue

            data = src.read_bytes()
            try:
                content_text = data.decode('utf-8')
            except Exception:
                content_text = data.decode('utf-8', errors='replace')
            digest = _sha256_hex(data)
            slug = _sanitize_slug(src.stem)
            dest_name = f"seed_{user_id}_{digest[:12]}_{slug}{ext}"
            dest_path = static_dir / dest_name
            file_url = f"http://localhost:8000/static/user_files/{dest_name}"

            # Dedup: same user, same original filename, same size, same type.
            size_bytes = len(data)
            existing = (
                db.query(UserFile)
                .filter(
                    UserFile.user_id == user_id,
                    UserFile.original_filename == src.name,
                    UserFile.size_bytes == size_bytes,
                    UserFile.file_type == file_type,
                )
                .first()
            )
            if existing:
                print(f"SKIP (already imported): {src} -> id={existing.id} url={existing.file_url}")
                skipped += 1
                continue

            print(f"IMPORT: {src} -> {dest_path} ({file_type}, {size_bytes} bytes)")

            if args.apply:
                static_dir.mkdir(parents=True, exist_ok=True)
                if not dest_path.exists():
                    dest_path.write_bytes(data)

                row = UserFile(
                    user_id=user_id,
                    title=src.stem,
                    file_type=file_type,
                    original_filename=src.name,
                    content_type="text/markdown" if file_type == "md" else "text/plain",
                    size_bytes=size_bytes,
                    content=content_text,
                    file_url=file_url,
                )
                db.add(row)
                db.commit()
                db.refresh(row)
                imported += 1
                print(f"  -> inserted user_files.id={row.id}")

        if not args.apply:
            print("\nDry-run only. Re-run with --apply to perform the import.")

        print(f"\nDone. imported={imported} skipped={skipped}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"Error: {e!r}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
