#!/usr/bin/env bash
set -euo pipefail

# Compare row counts between source DB and Supabase target DB.
#
# Usage:
#   SUPABASE_DB_PASSWORD='xxx' bash scripts/compare_table_counts.sh
#
# Optional envs:
#   SRC_DATABASE_URL='postgresql://user:pass@localhost:5432/db'
#   SUPABASE_DB_URL='postgresql://postgres.xxx@aws-1-xx.pooler.supabase.com:5432/postgres?sslmode=require'
#   OUTDIR=./tmp/supabase_migration

SRC_DATABASE_URL="${SRC_DATABASE_URL:-${DATABASE_URL:-postgresql://postgres:burnme@localhost/db}}"
SUPABASE_DB_URL="${SUPABASE_DB_URL:-}"
SUPABASE_DB_PASSWORD="${SUPABASE_DB_PASSWORD:-}"
OUTDIR="${OUTDIR:-./tmp/supabase_migration}"

if [[ -z "$SUPABASE_DB_URL" && -f "./supabase/.temp/pooler-url" ]]; then
  SUPABASE_DB_URL="$(cat ./supabase/.temp/pooler-url)"
fi

if [[ -z "$SUPABASE_DB_URL" ]]; then
  echo "[ERROR] 请设置 SUPABASE_DB_URL（或先执行 supabase link）" >&2
  exit 1
fi

if [[ "$SUPABASE_DB_URL" != *"sslmode="* ]]; then
  if [[ "$SUPABASE_DB_URL" == *"?"* ]]; then
    SUPABASE_DB_URL="${SUPABASE_DB_URL}&sslmode=require"
  else
    SUPABASE_DB_URL="${SUPABASE_DB_URL}?sslmode=require"
  fi
fi

if [[ "$SUPABASE_DB_URL" =~ ^postgres(ql)?://[^:/@]+@ ]] && [[ -z "$SUPABASE_DB_PASSWORD" ]]; then
  echo "[ERROR] 当前 SUPABASE_DB_URL 未包含密码，请设置 SUPABASE_DB_PASSWORD" >&2
  exit 1
fi

PG_DUMP_BIN="$(command -v pg_dump || true)"
PSQL_BIN="$(command -v psql || true)"
if [[ -z "$PG_DUMP_BIN" || -z "$PSQL_BIN" ]]; then
  if [[ -x "/opt/homebrew/opt/libpq/bin/pg_dump" && -x "/opt/homebrew/opt/libpq/bin/psql" ]]; then
    PG_DUMP_BIN="/opt/homebrew/opt/libpq/bin/pg_dump"
    PSQL_BIN="/opt/homebrew/opt/libpq/bin/psql"
  fi
fi
[[ -n "$PSQL_BIN" ]] || { echo "[ERROR] 找不到 psql（可安装: brew install libpq）" >&2; exit 1; }

mkdir -p "$OUTDIR"
LOCAL_TSV="$OUTDIR/local_counts.tsv"
SUPA_TSV="$OUTDIR/supabase_counts.tsv"
MERGED_TSV="$OUTDIR/counts_compare.tsv"

collect_counts() {
  local db_url="$1"
  local pass="$2"
  local out_tsv="$3"

  : > "$out_tsv"

  while IFS=$'\t' read -r schema table; do
    [[ -z "$schema" || -z "$table" ]] && continue
    count=$(PGPASSWORD="$pass" "$PSQL_BIN" "$db_url" -At -c "SELECT COUNT(*)::bigint FROM \"$schema\".\"$table\";" 2>/dev/null || echo "ERR")
    echo -e "${table}\t${count}" >> "$out_tsv"
  done < <(PGPASSWORD="$pass" "$PSQL_BIN" "$db_url" -At -F $'\t' -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;")
}

echo "[1/3] 统计本地数据库行数..."
collect_counts "$SRC_DATABASE_URL" "" "$LOCAL_TSV"

echo "[2/3] 统计 Supabase 数据库行数..."
collect_counts "$SUPABASE_DB_URL" "$SUPABASE_DB_PASSWORD" "$SUPA_TSV"

sort "$LOCAL_TSV" -o "$LOCAL_TSV"
sort "$SUPA_TSV" -o "$SUPA_TSV"

echo "[3/3] 生成对比报告..."
join -a 1 -a 2 -e "MISSING" -o '0,1.2,2.2' "$LOCAL_TSV" "$SUPA_TSV" \
| awk 'BEGIN{FS=OFS="\t"; print "table\tlocal\tsupabase\tstatus"} NR>0 {status=($2==$3?"OK":"DIFF"); print $1,$2,$3,status}' \
> "$MERGED_TSV"

cat "$MERGED_TSV"

echo "\n[DONE] 对比文件已生成: $MERGED_TSV"
