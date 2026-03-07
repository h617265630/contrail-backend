#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   SRC_DATABASE_URL='postgresql://user:pass@localhost:5432/db' \
#   SUPABASE_DB_URL='postgresql://postgres.xxxx:pass@aws-0-xx.pooler.supabase.com:5432/postgres?sslmode=require' \
#   bash scripts/migrate_to_supabase.sh
#
# Optional envs:
#   WORKDIR=./tmp/supabase_migration
#   KEEP_DUMPS=1
#   FORCE=1                # skip supabase host safety check

SRC_DATABASE_URL="${SRC_DATABASE_URL:-${DATABASE_URL:-postgresql://postgres:burnme@localhost/db}}"
SUPABASE_DB_URL="${SUPABASE_DB_URL:-}"
SUPABASE_DB_PASSWORD="${SUPABASE_DB_PASSWORD:-}"
WORKDIR="${WORKDIR:-./tmp/supabase_migration}"
KEEP_DUMPS="${KEEP_DUMPS:-0}"
FORCE="${FORCE:-0}"

if [[ -z "$SUPABASE_DB_URL" && -f "./supabase/.temp/pooler-url" ]]; then
  SUPABASE_DB_URL="$(cat ./supabase/.temp/pooler-url)"
fi

if [[ -z "$SUPABASE_DB_URL" ]]; then
  echo "[ERROR] 请设置 SUPABASE_DB_URL（或先执行 supabase link 并确保存在 supabase/.temp/pooler-url）" >&2
  exit 1
fi

if [[ "$FORCE" != "1" ]]; then
  if [[ "$SUPABASE_DB_URL" != *"supabase"* && "$SUPABASE_DB_URL" != *"pooler"* ]]; then
    echo "[ERROR] SUPABASE_DB_URL 看起来不像 Supabase 地址。若确认无误，请设置 FORCE=1" >&2
    exit 1
  fi
fi

PG_DUMP_BIN="$(command -v pg_dump || true)"
PSQL_BIN="$(command -v psql || true)"

if [[ -z "$PG_DUMP_BIN" || -z "$PSQL_BIN" ]]; then
  if [[ -x "/opt/homebrew/opt/libpq/bin/pg_dump" && -x "/opt/homebrew/opt/libpq/bin/psql" ]]; then
    PG_DUMP_BIN="/opt/homebrew/opt/libpq/bin/pg_dump"
    PSQL_BIN="/opt/homebrew/opt/libpq/bin/psql"
  fi
fi

[[ -n "$PG_DUMP_BIN" ]] || { echo "[ERROR] 找不到 pg_dump（可安装: brew install libpq）" >&2; exit 1; }
[[ -n "$PSQL_BIN" ]] || { echo "[ERROR] 找不到 psql（可安装: brew install libpq）" >&2; exit 1; }

# Supabase 强制 SSL
if [[ "$SUPABASE_DB_URL" != *"sslmode="* ]]; then
  if [[ "$SUPABASE_DB_URL" == *"?"* ]]; then
    SUPABASE_DB_URL="${SUPABASE_DB_URL}&sslmode=require"
  else
    SUPABASE_DB_URL="${SUPABASE_DB_URL}?sslmode=require"
  fi
fi

# 如果 URL 不含密码，要求通过 SUPABASE_DB_PASSWORD 提供
if [[ "$SUPABASE_DB_URL" =~ ^postgres(ql)?://[^:/@]+@ ]] && [[ -z "$SUPABASE_DB_PASSWORD" ]]; then
  echo "[ERROR] 当前 SUPABASE_DB_URL 未包含密码，请设置 SUPABASE_DB_PASSWORD" >&2
  exit 1
fi

mkdir -p "$WORKDIR"
SCHEMA_DUMP="$WORKDIR/schema.sql"
DATA_DUMP="$WORKDIR/data.sql"

echo "[1/5] 导出 schema..."
"$PG_DUMP_BIN" "$SRC_DATABASE_URL" \
  --schema-only \
  --no-owner \
  --no-privileges \
  --clean \
  --if-exists \
  --quote-all-identifiers \
  -f "$SCHEMA_DUMP"

echo "[2/5] 导出 data..."
"$PG_DUMP_BIN" "$SRC_DATABASE_URL" \
  --data-only \
  --no-owner \
  --no-privileges \
  --inserts \
  --rows-per-insert=100 \
  --quote-all-identifiers \
  -f "$DATA_DUMP"

echo "[3/5] 导入 schema 到 Supabase..."
PGPASSWORD="$SUPABASE_DB_PASSWORD" "$PSQL_BIN" "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f "$SCHEMA_DUMP"

echo "[4/5] 导入 data 到 Supabase..."
PGPASSWORD="$SUPABASE_DB_PASSWORD" "$PSQL_BIN" "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f "$DATA_DUMP"

echo "[5/5] 校验导入结果（查看 public schema 表数量）..."
PGPASSWORD="$SUPABASE_DB_PASSWORD" "$PSQL_BIN" "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 <<'SQL'
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
SQL

if [[ "$KEEP_DUMPS" != "1" ]]; then
  rm -f "$SCHEMA_DUMP" "$DATA_DUMP"
fi

echo "[DONE] 数据库结构与数据已迁移到 Supabase。"
