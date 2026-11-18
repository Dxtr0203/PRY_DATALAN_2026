#!/usr/bin/env python
"""Create fictitious Iteration 5 accounts and technician profiles in the isolated DB."""

from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = ROOT / "DATALAN"
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DATALAN.settings")

import django  # noqa: E402

django.setup()

from django.db import connection  # noqa: E402
from DATALAN.auth_service import create_registered_user  # noqa: E402
from DATALAN.optimization_service import (  # noqa: E402
    CAPABILITY_GROUPS,
    INCIDENT_PROFILE_CAPABILITIES,
    _incident_profile_from_post,
    _operational_profile_from_post,
    get_technicians,
    register_technician_profile,
    update_incident_technician,
    update_technician,
)


TEST_DATABASE = "datalan_it5_test"
TEST_HOST = "127.0.0.1"
TEST_PORT = "55439"
TEST_PASSWORD = "IT5-Local-2026!"
ACCOUNTS = (
    ("it5.admin", "Administrador Simulado IT5", "admin"),
    ("it5.comercial", "Comercial Simulada IT5", "comercial"),
    ("it5.planta", "Encargada de Planta Simulada IT5", "planta_encargado"),
    ("it5.sistemas", "Encargado de Sistemas Simulado IT5", "sistemas_encargado"),
    ("it5.soporte", "Soporte Simulado IT5", "soporte_sistemas"),
    ("it5.tecnico1", "Técnico Simulado IT5 Uno", "tecnico"),
    ("it5.tecnico2", "Técnico Simulado IT5 Dos", "tecnico"),
    ("it5.tecnico3", "Técnico Simulado IT5 Tres", "tecnico"),
)


def assert_isolated_database():
    database = connection.settings_dict
    if (
        database["ENGINE"] != "django.db.backends.postgresql"
        or database["NAME"] != TEST_DATABASE
        or database["HOST"] not in {"127.0.0.1", "localhost"}
        or str(database["PORT"]) != TEST_PORT
    ):
        raise RuntimeError(
            "Se canceló la preparación: la conexión no apunta a "
            f"{TEST_DATABASE} en {TEST_HOST}:{TEST_PORT}."
        )


def operational_profile_post():
    profile = {
        "operational_status": "ACTIVO",
        "experience_years": "12",
        "experience_months": "0",
        "lead_installation": "SI",
        "lead_removal": "SI",
        "work_days": [
            "LUNES", "MARTES", "MIERCOLES", "JUEVES",
            "VIERNES", "SABADO", "DOMINGO",
        ],
        "work_start": "08:00",
        "work_end": "18:00",
        "absence_type": "",
        "absence_start": "",
        "absence_end": "",
    }
    for group, capabilities in CAPABILITY_GROUPS.items():
        for key, _label in capabilities:
            profile[f"capability_{group}_{key}"] = "SIN_APOYO"
    return profile


def incident_profile_post():
    profile = {"lead_incidents": "SI"}
    for key, _label in INCIDENT_PROFILE_CAPABILITIES:
        profile[f"incident_capability_{key}"] = "SIN_APOYO"
    return profile


def main():
    assert_isolated_database()
    created = []
    with connection.cursor() as cursor:
        for username, full_name, role in ACCOUNTS:
            cursor.execute(
                "SELECT u.user_id, r.role_key FROM datalan.usuarios u "
                "LEFT JOIN datalan.usuarios_roles ur ON ur.user_id = u.user_id "
                "LEFT JOIN datalan.roles r ON r.role_id = ur.role_id "
                "WHERE u.username = %s",
                [username],
            )
            existing = cursor.fetchone()
            if existing:
                if existing[1] != role:
                    raise RuntimeError(
                        f"La cuenta aislada {username} ya existe con otro rol."
                    )
                user_id = existing[0]
            else:
                user_id = create_registered_user({
                    "username": username,
                    "full_name": full_name,
                    "email": f"{username}@example.invalid",
                    "password": TEST_PASSWORD,
                    "role": role,
                    "identity_number": "",
                })
                created.append(username)
            if role == "tecnico":
                register_technician_profile(user_id, full_name)

    technicians = get_technicians()
    profiles = {technician["full_name"]: technician for technician in technicians}
    for _username, full_name, role in ACCOUNTS:
        if role != "tecnico":
            continue
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT technician_id FROM datalan.optimizacion_tecnicos "
                "WHERE full_name = %s",
                [full_name],
            )
            row = cursor.fetchone()
        if not row:
            raise RuntimeError(f"No se creó el perfil de {full_name}.")
        operational_post = operational_profile_post()
        incident_post = incident_profile_post()
        expected_operational = _operational_profile_from_post(operational_post)
        expected_incident = _incident_profile_from_post(incident_post)
        update_technician(row[0], operational_post)
        update_incident_technician(row[0], incident_post)
        if profiles[full_name]["staff_type"] != "TÉCNICO":
            raise RuntimeError(f"El perfil de {full_name} no tiene rol técnico.")
        refreshed = {
            technician["full_name"]: technician
            for technician in get_technicians()
        }[full_name]
        if refreshed["operational_profile"] != expected_operational:
            raise RuntimeError(f"No persistió el perfil operativo de {full_name}.")
        if refreshed["incident_profile"] != expected_incident:
            raise RuntimeError(f"No persistió el perfil de incidencias de {full_name}.")

    print(f"Base aislada verificada: {TEST_DATABASE}@{TEST_HOST}:{TEST_PORT}")
    print(f"Cuentas creadas ahora: {', '.join(created) if created else 'ninguna (ya existían)'}")
    print(f"Perfiles técnicos ficticios configurados: 3")
    print(f"Contraseña de prueba exclusivamente local: {TEST_PASSWORD}")


if __name__ == "__main__":
    main()
