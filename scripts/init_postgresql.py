"""Create and seed the DATALAN PostgreSQL database schema."""

import os
import sys
from pathlib import Path

import psycopg

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / 'DATALAN'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DATALAN.settings')
import django

django.setup()
from DATALAN.auth_service import DEMO_USERS  # pyright: ignore[reportMissingImports]
from DATALAN.workflow_service import demo_requests, save_requests  # pyright: ignore[reportMissingImports]


schema = (BASE_DIR / 'docs' / 'postgresql_schema.sql').read_text(encoding='utf-8')
connection_kwargs = {
    'dbname': os.environ.get('DATALAN_DB_NAME', 'datalan'),
    'user': os.environ.get('DATALAN_DB_USER', 'postgres'),
    'password': os.environ.get('DATALAN_DB_PASSWORD', ''),
    'host': os.environ.get('DATALAN_DB_HOST', '127.0.0.1'),
    'port': os.environ.get('DATALAN_DB_PORT', '5432'),
}

with psycopg.connect(**connection_kwargs) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('datalan.solicitudes')")
        if cursor.fetchone()[0] is None:
            cursor.execute(schema)
        cursor.execute("ALTER TABLE datalan.solicitudes ADD COLUMN IF NOT EXISTS extra_data JSONB NOT NULL DEFAULT '{}'::jsonb")
        cursor.execute("ALTER TABLE datalan.usuarios ADD COLUMN IF NOT EXISTS identity_number VARCHAR(80) NOT NULL DEFAULT ''")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datalan.role_access_settings (
                role_id BIGINT PRIMARY KEY REFERENCES datalan.roles(role_id) ON DELETE CASCADE,
                modules JSONB NOT NULL DEFAULT '[]'::jsonb,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)
        cursor.execute("""
            INSERT INTO datalan.estados_solicitud (status_key, label, area_key, is_terminal)
            VALUES ('RECHAZADA_COMERCIAL', 'Rechazada por Comercial', 'COMERCIAL', TRUE)
            ON CONFLICT (status_key) DO NOTHING
        """)
        for user in DEMO_USERS:
            cursor.execute(
                """
                INSERT INTO datalan.usuarios (username, full_name, email, password_hash)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (username) DO UPDATE SET full_name = EXCLUDED.full_name,
                    email = EXCLUDED.email, is_active = TRUE
                RETURNING user_id
                """,
                [user['username'], user['full_name'], user['email'], user['password']],
            )
            user_id = cursor.fetchone()[0]
            cursor.execute("SELECT role_id FROM datalan.roles WHERE role_key = %s", [user['role']])
            role_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO datalan.usuarios_roles (user_id, role_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                [user_id, role_id],
            )
    connection.commit()

save_requests(None, demo_requests())

print('DATALAN PostgreSQL schema and demo users initialized.')