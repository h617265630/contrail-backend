import sys
from pathlib import Path

# Ensure backend dir is on sys.path so we can import project modules
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings
import psycopg2

url = getattr(settings, 'DATABASE_URL', None)
print('DATABASE_URL:', url)
if not url:
    print('No DATABASE_URL available')
    sys.exit(1)

try:
    conn = psycopg2.connect(url)
    conn.autocommit = True
    cur = conn.cursor()

    print('\n-- public schema tables:')
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
    rows = cur.fetchall()
    for r in rows:
        print(' -', r[0])

    print('\n-- check link_resources exists:')
    cur.execute("SELECT to_regclass('public.link_resources')")
    exists = cur.fetchone()[0]
    print('link_resources:', exists)

    print('\n-- alembic_version contents:')
    try:
        cur.execute('SELECT * FROM alembic_version')
        for r in cur.fetchall():
            print(r)
    except Exception as e:
        print('Could not read alembic_version:', e)

    print('\n-- recent webhook_events:')
    try:
        cur.execute(
            """
            SELECT id, provider, event_type, processed,
                   COALESCE(NULLIF(error, ''), '-') AS error,
                   received_at
            FROM webhook_events
            ORDER BY id DESC
            LIMIT 5
            """
        )
        rows = cur.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print('Could not read webhook_events:', e)

    print('\n-- latest webhook_event payload/header snippet:')
    try:
        cur.execute(
            """
            SELECT id,
                   LENGTH(COALESCE(payload_json, '')) AS payload_len,
                   SUBSTRING(COALESCE(payload_json, '') FROM 1 FOR 400) AS payload_head,
                   SUBSTRING(COALESCE(headers_json, '') FROM 1 FOR 400) AS headers_head
            FROM webhook_events
            ORDER BY id DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        print(row)
    except Exception as e:
        print('Could not read latest webhook_event payload/header:', e)

    print('\n-- recent subscriptions:')
    try:
        cur.execute(
            """
            SELECT id, user_id, provider, provider_subscription_id, plan_code, status,
                   current_period_end, cancel_at_period_end, updated_at
            FROM subscriptions
            ORDER BY id DESC
            LIMIT 5
            """
        )
        rows = cur.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print('Could not read subscriptions:', e)

    cur.close()
    conn.close()
except Exception as e:
    print('DB connection error:', repr(e))
    sys.exit(2)
