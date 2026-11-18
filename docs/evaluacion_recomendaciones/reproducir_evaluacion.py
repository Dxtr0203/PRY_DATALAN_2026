#!/usr/bin/env python
"""Reproduce controlled DATALAN optimizer runs and render result-only PNG charts."""

from __future__ import annotations

import copy
import json
import math
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
PROJECT_ROOT = REPOSITORY_ROOT / "DATALAN"
sys.path.insert(0, str(PROJECT_ROOT))

from DATALAN.optimization_service import (  # noqa: E402
    CAPABILITY_GROUPS,
    DEFAULT_INCIDENT_NSGA2_CONFIG,
    DEFAULT_OPTIMIZATION_CONFIG,
    INCIDENT_PROFILE_CAPABILITIES,
    run_genetic_optimization,
    run_genetic_team_optimization,
    run_incident_nsga2,
    run_incident_team_nsga2,
)


SEEDS = (101, 202, 303)
DATASET_ID = "DATALAN-SIM-20261027-A"
INCIDENT_CLOCK = "2026-10-27T08:30:00"
FIXED_TEAM_SCHEDULE = "2026-10-28T10:00:00"

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "00110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000",) * 7,
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    ",": ("00000", "00000", "00000", "00000", "00110", "00100", "01000"),
    ":": ("00000", "00110", "00110", "00000", "00110", "00110", "00000"),
    ";": ("00000", "00110", "00110", "00000", "00110", "00100", "01000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00100", "01000", "10110", "00110", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "11111", "00000", "11111", "00000", "00000", "00000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}
COLORS = ("#2067a8", "#cf5b28", "#3b9363")
GRID = "#e3e8ef"
INK = "#26354a"
MUTED = "#65738a"


def fake_dataset():
    technicians = []
    names = (
        "Tecnico SIM 01", "Tecnico SIM 02", "Tecnico SIM 03",
        "Tecnico SIM 04", "Tecnico SIM 05", "Tecnico SIM 06",
        "Tecnico SIM 07", "Tecnico SIM 08",
    )
    distances = (3.0, 5.5, 8.0, 11.0, 14.0, 17.0, 20.0, 24.0)
    starts = ("08:00", "08:00", "09:00", "09:00", "10:00", "10:00", "11:00", "12:00")
    for index, name in enumerate(names):
        capabilities = {}
        for group_index, (group, entries) in enumerate(CAPABILITY_GROUPS.items()):
            capabilities[group] = {
                key: (
                    "SIN_APOYO"
                    if (index + key_index + group_index) % 3 == 0
                    else "CON_APOYO"
                )
                for key_index, (key, _label) in enumerate(entries)
            }
        incident_capabilities = {
            key: (
                "SIN_APOYO" if (index + key_index) % 2 == 0 else "CON_APOYO"
            )
            for key_index, (key, _label) in enumerate(INCIDENT_PROFILE_CAPABILITIES)
        }
        technicians.append({
            "technician_id": f"SIM-TEC-{index + 1:02d}",
            "full_name": name,
            "staff_type": "TÉCNICO",
            "available": True,
            "workload": index % 4,
            "current_location": ("Centro", "Norte", "Sur", "Este")[index % 4],
            "travel_distance_km": distances[index],
            "operational_profile": {
                "operational_status": "ACTIVO",
                "experience_years": 2 + index * 2,
                "experience_months": index % 12,
                "lead_installation": "SI" if index in {0, 3, 6} else "NO",
                "lead_removal": "SI" if index in {1, 4, 7} else "NO",
                "capabilities": capabilities,
                "work_days": ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES"],
                "work_start": starts[index],
                "work_end": "18:00",
                "absences": [],
            },
            "incident_profile": {
                "lead_incidents": "SI" if index in {1, 4, 6} else "NO",
                "capabilities": incident_capabilities,
            },
        })

    requirements = (
        "Instalacion de equipos; medicion OTDR.",
        "Fusiones de fibra y empalmes.",
        "Tendido de cable aereo.",
        "Tendido subterraneo y mediciones OTDR.",
        "Instalacion de equipos y fusion de fibra.",
        "Verificacion OTDR y reemplazo de equipos.",
    )
    priorities = ("Alta", "Media", "Baja", "Alta", "Media", "Baja")
    requests = []
    for index, (requirement, priority) in enumerate(zip(requirements, priorities), 1):
        item = {
            "cite": f"SIM-REQ-{index:02d}",
            "applicant": f"Solicitante ficticio {index:02d}",
            "type": "Instalación Punto a Punto",
            "status": "APROBADA",
            "priority": priority,
            "requirements": requirement,
            "equipment_enabled": "equipos" in requirement,
            "equipment_type": "SFP",
            "speed": "1 Gbps",
            "destination": f"Nodo SIM {index:02d}",
            "destination_location": ("Centro", "Norte", "Sur")[index % 3],
            "plant_evaluation": {
                "distance": str(8 + index * 2),
                "estimated_hours": 1.5 + index * 0.5,
            },
            "estimated_hours": 1.5 + index * 0.5,
        }
        requests.append(item)

    active_requests = [
        {
            "cite": f"SIM-ACTIVE-{index:02d}",
            "status": "EN EJECUCIÓN",
            "assignment": {
                "leader": technicians[(index * 2) % len(technicians)]["full_name"],
                "others": [],
            },
        }
        for index in range(1, 5)
    ]
    incident_texts = (
        ("Intermitencia del enlace y perdida de senal; revisar mediciones.", "ALTA"),
        ("Alarma OTDR y atenuacion detectada en el enlace.", "MEDIA"),
        ("Empalme de fibra danado; requiere fusion y reparacion.", "ALTA"),
        ("Cable de enlace cortado; diagnosticar y reparar el tramo.", "MEDIA"),
        ("Equipo de transmision falla; verificar y sustituir si corresponde.", "BAJA"),
        ("Intermitencia; verificar enlace y registrar la resolucion.", "BAJA"),
    )
    incidents = [
        {
            "incident_id": f"SIM-INC-{index:02d}",
            "incident_parent_cite": f"SIM-REQ-{index:02d}",
            "incident_client": f"Solicitante ficticio {index:02d}",
            "incident_status": "PENDIENTE DE ASIGNACIÓN",
            "incident_reported_at": f"{27 - index:02d}/10/2026 07:30",
            "incident_description": description,
            "severity": severity,
        }
        for index, (description, severity) in enumerate(incident_texts, 1)
    ]
    target_request = {
        **copy.deepcopy(requests[4]),
        "cite": "SIM-REQ-05",
        "priority": "Media",
        "status": "APROBADA",
        "delivery_workflow": {
            "installation": {
                "status": "ENVIADA",
                "points": {
                    "destination": {
                        "date": FIXED_TEAM_SCHEDULE[:10],
                        "time": FIXED_TEAM_SCHEDULE[11:16],
                        "description": "Instalacion ficticia para evaluar equipo.",
                    },
                },
                "work_descriptions": {
                    "destination": "Instalacion ficticia para evaluar equipo.",
                },
            },
        },
    }
    return {
        "dataset_id": DATASET_ID,
        "description": (
            "Datos completamente ficticios, creados para esta evaluación. "
            "No corresponden a clientes, incidencias ni personal real."
        ),
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "algorithm_clock_for_incident_assignment": INCIDENT_CLOCK,
        "fixed_schedule_for_incident_team": FIXED_TEAM_SCHEDULE,
        "requests": requests,
        "incidents": incidents,
        "technicians": technicians,
        "active_request_items_for_load_context": active_requests,
        "fixed_schedule_team_target": target_request,
    }


def workload_map(active_requests):
    counts = {}
    for item in active_requests:
        assignment = item.get("assignment") or {}
        for name in {assignment.get("leader", ""), *assignment.get("others", [])}:
            if name:
                counts[name] = counts.get(name, 0) + 1
    return counts


def execute(dataset):
    general_config = {
        **DEFAULT_OPTIMIZATION_CONFIG,
        "crossover_rate": DEFAULT_OPTIMIZATION_CONFIG["crossover_percent"] / 100,
        "mutation_rate": DEFAULT_OPTIMIZATION_CONFIG["mutation_percent"] / 100,
    }
    incident_config = {
        **DEFAULT_INCIDENT_NSGA2_CONFIG,
        "crossover_rate": DEFAULT_INCIDENT_NSGA2_CONFIG["crossover_percent"] / 100,
        "mutation_rate": DEFAULT_INCIDENT_NSGA2_CONFIG["mutation_percent"] / 100,
    }
    counts = {
        "requests": len(dataset["requests"]),
        "incidents": len(dataset["incidents"]),
        "technicians": len(dataset["technicians"]),
    }
    results = []
    for seed in SEEDS:
        runs = (
            (
                "IT2-EVAL-SOL",
                "GA solicitudes por permutación",
                lambda: run_genetic_optimization(
                    copy.deepcopy(dataset["requests"]),
                    copy.deepcopy(dataset["technicians"]),
                    population_size=general_config["population_size"],
                    generations=general_config["generations"],
                    mutation_rate=general_config["mutation_rate"],
                    crossover_rate=general_config["crossover_rate"],
                    random_seed=seed,
                    active_request_items=copy.deepcopy(
                        dataset["active_request_items_for_load_context"]
                    ),
                ),
                general_config,
            ),
            (
                "IT2-EVAL-INC",
                "NSGA-II asignación de incidencias",
                lambda: run_incident_nsga2(
                    copy.deepcopy(dataset["incidents"]),
                    copy.deepcopy(dataset["technicians"]),
                    base_workloads=workload_map(
                        dataset["active_request_items_for_load_context"]
                    ),
                    population_size=incident_config["population_size"],
                    generations=incident_config["generations"],
                    mutation_rate=incident_config["mutation_rate"],
                    crossover_rate=incident_config["crossover_rate"],
                    random_seed=seed,
                    current_time=datetime.fromisoformat(INCIDENT_CLOCK),
                ),
                incident_config,
            ),
            (
                "IT2-EVAL-EQ",
                "NSGA-II equipo de incidencia, horario fijo",
                lambda: run_incident_team_nsga2(
                    copy.deepcopy(dataset["incidents"][0]),
                    copy.deepcopy(dataset["technicians"]),
                    scheduled_at=datetime.fromisoformat(FIXED_TEAM_SCHEDULE),
                    base_workloads=workload_map(
                        dataset["active_request_items_for_load_context"]
                    ),
                    request_items=copy.deepcopy(
                        dataset["active_request_items_for_load_context"]
                    ),
                    population_size=incident_config["population_size"],
                    generations=incident_config["generations"],
                    mutation_rate=incident_config["mutation_rate"],
                    crossover_rate=incident_config["crossover_rate"],
                    random_seed=seed,
                ),
                incident_config,
            ),
            (
                "IT2-EVAL-TEAM",
                "GA equipo operativo para solicitud",
                lambda: run_genetic_team_optimization(
                    copy.deepcopy(dataset["fixed_schedule_team_target"]),
                    "installation",
                    copy.deepcopy(dataset["technicians"]),
                    copy.deepcopy(dataset["requests"])
                    + copy.deepcopy(dataset["active_request_items_for_load_context"]),
                    population_size=general_config["population_size"],
                    generations=general_config["generations"],
                    mutation_rate=general_config["mutation_rate"],
                    crossover_rate=general_config["crossover_rate"],
                    random_seed=seed,
                ),
                general_config,
            ),
        )
        for code, modality, call, config in runs:
            started = time.perf_counter()
            try:
                result = call()
            except Exception as error:
                elapsed = time.perf_counter() - started
                results.append({
                    "code": code,
                    "modality": modality,
                    "dataset_id": DATASET_ID,
                    **counts,
                    "population": config["population_size"],
                    "generations": config["generations"],
                    "crossover_rate": config["crossover_percent"],
                    "mutation_rate": config["mutation_percent"],
                    "seed": seed,
                    "elapsed_seconds": round(elapsed, 6),
                    "status": "FAILED",
                    "error": f"{type(error).__name__}: {error}",
                })
                continue
            elapsed = time.perf_counter() - started
            results.append({
                "code": code,
                "modality": modality,
                "dataset_id": DATASET_ID,
                **counts,
                "population": config["population_size"],
                "generations": config["generations"],
                "crossover_rate": config["crossover_percent"],
                "mutation_rate": config["mutation_percent"],
                "seed": seed,
                "elapsed_seconds": round(elapsed, 6),
                "status": "OK",
                "result": result,
            })
    return results


def fmt(value, digits=2):
    return f"{value:.{digits}f}".replace(".", ",")


def summarize_row(run):
    result = run["result"]
    code = run["code"]
    if code == "IT2-EVAL-SOL":
        solutions = result.get("top_solutions", [])
        alternatives = "; ".join(
            f"{index}: fitness {solution['fitness']}, cobertura "
            f"{solution['coverage']}%, sin asignar {solution['unassigned_count']}"
            for index, solution in enumerate(solutions, 1)
        )
        coverage = f"{result['coverage']}% / {result['unassigned_count']} sin asignar"
        objectives = f"Fitness mejor {result['fitness']} (mayor es mejor)"
        count = len(solutions)
    elif code == "IT2-EVAL-INC":
        alternatives_data = result.get("alternatives", [])
        alternatives = "; ".join(
            f"A{item['number']}: espera ponderada {item['weighted_wait_hours']} "
            f"h, desequilibrio {item['load_imbalance']}"
            for item in alternatives_data
        )
        coverage = (
            f"{result['incident_count']}/{result['incident_count']} incidencias "
            f"asignadas; {result['eligible_technicians']} técnicos elegibles"
        )
        objectives = (
            "Minimizar horas ponderadas por urgencia y suma de desviaciones "
            "cuadráticas de carga"
        )
        count = len(alternatives_data)
    elif code == "IT2-EVAL-EQ":
        alternatives_data = result.get("alternatives", [])
        alternatives = "; ".join(
            f"A{item['number']}: fitness {item['fitness']}, "
            f"objetivos ({100 - item['fitness']}, "
            f"{item['projected_mean_workload']})"
            for item in alternatives_data
        )
        coverage = (
            f"{result['eligible_technician_count']} técnicos elegibles; "
            "alternativas de 2-3 personas sin déficit de capacidades"
        )
        objectives = (
            "Minimizar 100 - fitness (puntos) y carga media proyectada "
            "(asignaciones por técnico)"
        )
        count = len(alternatives_data)
    else:
        proposals = result.get("proposals", [])
        alternatives = "; ".join(
            f"A{index}: fitness {item['fitness']}, equipo "
            f"{item['team_size']}/{result['recommended_team_size']}, "
            f"déficit {item['staffing_shortage']}"
            for index, item in enumerate(proposals, 1)
        )
        coverage = (
            f"{result['available_technician_count']} técnicos compatibles; "
            f"equipo {result['team_size']}/{result['recommended_team_size']}, "
            f"déficit {result['team_shortage']}"
        )
        objectives = f"Fitness mejor {proposals[0]['fitness']} (mayor es mejor)"
        count = len(proposals)
    return {
        "alternatives": count,
        "alternatives_summary": alternatives,
        "coverage": coverage,
        "objectives_summary": objectives,
    }


def write_markdown(dataset, results):
    rows = []
    for run in results:
        if run["status"] != "OK":
            summary = {
                "alternatives": 0,
                "alternatives_summary": f"FALLÓ: {run['error']}",
                "coverage": "No disponible",
                "objectives_summary": "No disponible",
            }
        else:
            summary = summarize_row(run)
        rows.append(
            f"| {run['code']}-{run['seed']} | {run['modality']} | "
            f"{run['dataset_id']} ({run['requests']} solicitudes, "
            f"{run['incidents']} incidencias, {run['technicians']} técnicos) | "
            f"{run['population']} | {run['generations']} | "
            f"{run['crossover_rate']}% | {run['mutation_rate']}% | "
            f"{run['seed']} | {summary['alternatives']} | "
            f"{summary['coverage']} | {summary['objectives_summary']}; "
            f"{summary['alternatives_summary']} | {run['elapsed_seconds']:.6f} | "
            f"{run['status']} |"
        )

    summary_lines = []
    for code in ("IT2-EVAL-SOL", "IT2-EVAL-INC", "IT2-EVAL-EQ", "IT2-EVAL-TEAM"):
        matching = [run for run in results if run["code"] == code]
        completed = [run for run in matching if run["status"] == "OK"]
        if code == "IT2-EVAL-SOL":
            values = [run["result"]["fitness"] for run in completed]
            label = "fitness final"
        elif code == "IT2-EVAL-INC":
            values = [
                run["result"]["alternatives"][0]["weighted_wait_hours"]
                for run in completed if run["result"]["alternatives"]
            ]
            label = "horas ponderadas de la primera alternativa devuelta"
        elif code == "IT2-EVAL-EQ":
            values = [
                100 - run["result"]["alternatives"][0]["fitness"]
                for run in completed if run["result"]["alternatives"]
            ]
            label = "100 - fitness de la primera alternativa devuelta"
        else:
            values = [
                run["result"]["proposals"][0]["fitness"]
                for run in completed if run["result"]["proposals"]
            ]
            label = "fitness de la primera propuesta devuelta"
        if values:
            variation = (
                f"mín. {min(values):.2f}; máx. {max(values):.2f}; "
                f"rango {max(values) - min(values):.2f}; "
                f"{len(set(values))} valor(es) distinto(s) en {len(values)} corrida(s)"
            )
        else:
            variation = "sin valores suficientes (corridas fallidas o sin alternativas)"
        summary_lines.append(f"- **{code}:** {label}: {variation}.")

    failures = [run for run in results if run["status"] != "OK"]
    failure_text = (
        "\n".join(f"- {run['code']}-{run['seed']}: {run['error']}" for run in failures)
        if failures else "- No hubo corridas fallidas."
    )
    text = f"""# Evaluación controlada de recomendaciones de DATALAN

## Alcance y reproducibilidad

- Ejecución real: `{datetime.now().astimezone().isoformat(timespec='seconds')}`.
- Conjunto único: `{DATASET_ID}`; los datos son completamente ficticios y están guardados completos en [datos_ficticios.json](./datos_ficticios.json).
- Reproducir las 12 llamadas medidas: `python docs/evaluacion_recomendaciones/reproducir_evaluacion.py` desde la raíz del repositorio. El script usa exclusivamente las funciones de algoritmo del proyecto; no llama a las vistas, PostgreSQL, ni modifica código o registros.
- Semillas: `{", ".join(map(str, SEEDS))}`. Para cada modalidad se mantuvieron datos y configuración iguales; solo cambió `random_seed`.
- Configuraciones fijas: algoritmo general `{DEFAULT_OPTIMIZATION_CONFIG}`; algoritmos NSGA-II `{DEFAULT_INCIDENT_NSGA2_CONFIG}`. Cruce y mutación en la tabla se expresan como porcentajes configurados.
- El horario simulado de la asignación de incidencias es `{INCIDENT_CLOCK}`; el horario fijo del caso de equipo es `{FIXED_TEAM_SCHEDULE}`. No se cambió el reloj del sistema.
- El tiempo es `perf_counter` alrededor de la llamada Python al algoritmo y se expresa en segundos. No representa duración de atención ni tiempo del servicio.
- Resultados completos de cada llamada, semillas, configuración, tiempos, historial y alternativas: [ejecuciones.json](./ejecuciones.json).

## Definición verificada de las métricas y objetivos

1. **GA de solicitudes:** fitness de `0` a `100`, mayor es mejor. En el modo operativo del conjunto sintético, el fitness combina prioridad `25%`, tiempo ponderado `20%`, distancia `15%`, carga `15%` y fitness medio de equipos `25%`, multiplicados por la cobertura. La cobertura es porcentaje de solicitudes con técnico/equipo asignado. El gráfico registra el mejor fitness de la población por generación.
2. **NSGA-II de incidencias:** objetivo 1 = suma de minutos de espera hasta el siguiente inicio de jornada, multiplicada por el peso de urgencia, dividida entre 60 (`h ponderadas`, minimizar). Objetivo 2 = suma de `(carga proyectada - carga media)^2` entre técnicos (`asignaciones^2`, minimizar); carga proyectada incluye trabajos activos y asignaciones propuestas. Pesos de urgencia son factores adimensionales de la regla de severidad/antigüedad.
3. **NSGA-II de equipo para horario fijo:** el código minimiza `(100 - fitness, carga_media_proyectada)`. El fitness (puntos, 0-100) se calcula con capacidades 50%, liderazgo 20%, experiencia 15%, carga 10% y distancia 5%. La carga media es el promedio de carga activa más una asignación propuesta entre integrantes del equipo (`asignaciones/técnico`). Ambos objetivos se minimizan. El gráfico muestra alternativas devueltas por el algoritmo, no las rotula como un frente global: la salida puede tomar puntos de frentes posteriores si el primero contiene menos de tres.
4. **GA de equipo operativo:** el fitness es el puntaje ponderado de capacidades 50%, liderazgo 20%, experiencia 15%, carga 10% y distancia 5%; mayor es mejor. En esta modalidad la recomendación es un conjunto de hasta tres equipos archivados, no un frente de Pareto. Se informa cobertura de personal/déficit del equipo.

## Tabla de ejecuciones

Los campos “solicitudes/incidencias/técnicos” indican el tamaño del conjunto común completo, aunque una modalidad use solo una de esas colecciones. “Alternativas” es el número devuelto por la implementación en esa ejecución. “Fitness u objetivos” conserva el sentido de optimización; para NSGA se listan objetivos de cada alternativa devuelta, no se afirma que todas pertenezcan al frente global.

| Código | Modalidad | Conjunto y cantidades | Población | Generaciones | Cruce | Mutación | Semilla | Alternativas | Cobertura o déficit | Fitness u objetivos y alternativas | Tiempo real (s) | Estado |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|
{chr(10).join(rows)}

## Variación observada por modalidad

Los rangos siguientes comparan únicamente las tres semillas de la misma modalidad. No se comparan escalas de fitness entre modalidades ni se infiere una mejora del servicio real:

{chr(10).join(summary_lines)}

## Gráficos y alcance de interpretación

- [Fitness por generación — GA solicitudes](./fitness_generacional_solicitudes.png): líneas de las tres semillas; cada punto proviene del historial devuelto por esa ejecución.
- [Objetivos — NSGA-II incidencias](./objetivos_nsga2_incidencias.png): alternativas coincidentes se muestran con anillos concéntricos y su cantidad; ejes en unidades verificadas arriba.
- [Objetivos — NSGA-II equipos con horario fijo](./objetivos_nsga2_equipo_horario_fijo.png): alternativas coincidentes se muestran con anillos concéntricos y su cantidad; no se afirma que todas pertenezcan al frente global.
- Los tres PNG se generan con valores del JSON. El renderizador usa biblioteca estándar; no dibuja datos ilustrativos ni introduce puntos sintéticos.

## Errores e impedimentos

{failure_text}

No se ejecutaron solicitudes a la aplicación ni accesos a la base operativa. Estos experimentos miden recomendaciones algorítmicas sobre fixtures ficticios, no calidad de atención, efectividad del servicio ni resultados en producción.
"""
    (HERE / "resultados.md").write_text(text, encoding="utf-8")


def hex_color(value):
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


class Canvas:
    def __init__(self, width=1200, height=760, background="#ffffff"):
        self.width = width
        self.height = height
        self.pixels = bytearray(hex_color(background) * (width * height))

    def pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 3
            self.pixels[offset:offset + 3] = bytes(color)

    def line(self, x0, y0, x1, y1, color, width=1):
        color = hex_color(color) if isinstance(color, str) else color
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        error = dx + dy
        while True:
            radius = max(0, width // 2)
            for offset_y in range(-radius, radius + 1):
                for offset_x in range(-radius, radius + 1):
                    self.pixel(x0 + offset_x, y0 + offset_y, color)
            if x0 == x1 and y0 == y1:
                break
            twice = 2 * error
            if twice >= dy:
                error += dy
                x0 += sx
            if twice <= dx:
                error += dx
                y0 += sy

    def circle(self, cx, cy, radius, color):
        color = hex_color(color) if isinstance(color, str) else color
        for y in range(-radius, radius + 1):
            for x in range(-radius, radius + 1):
                if x * x + y * y <= radius * radius:
                    self.pixel(cx + x, cy + y, color)

    def text(self, x, y, value, color=INK, scale=2):
        normalized = unicodedata.normalize("NFKD", str(value))
        normalized = "".join(
            char for char in normalized if not unicodedata.combining(char)
        ).upper()
        color = hex_color(color) if isinstance(color, str) else color
        cursor = x
        for char in normalized:
            glyph = FONT.get(char, FONT["?"])
            for row, pattern in enumerate(glyph):
                for column, bit in enumerate(pattern):
                    if bit == "1":
                        for offset_y in range(scale):
                            for offset_x in range(scale):
                                self.pixel(
                                    cursor + column * scale + offset_x,
                                    y + row * scale + offset_y,
                                    color,
                                )
            cursor += 6 * scale

    def png(self, path):
        import struct
        import zlib

        def chunk(name, data):
            return (
                struct.pack(">I", len(data)) + name + data
                + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
            )

        scanlines = b"".join(
            b"\x00" + self.pixels[row * self.width * 3:(row + 1) * self.width * 3]
            for row in range(self.height)
        )
        data = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(
                b"IHDR",
                struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0),
            )
            + chunk(b"IDAT", zlib.compress(scanlines, 9))
            + chunk(b"IEND", b"")
        )
        Path(path).write_bytes(data)


def plot_axes(canvas, title, subtitle, x_label, y_label, x_values, y_values):
    left, top, right, bottom = 115, 145, canvas.width - 55, canvas.height - 110
    xmin, xmax = min(x_values), max(x_values)
    ymin, ymax = min(y_values), max(y_values)
    x_pad = max((xmax - xmin) * 0.12, 1.0)
    y_pad = max((ymax - ymin) * 0.16, 1.0)
    xmin -= x_pad
    xmax += x_pad
    ymin -= y_pad
    ymax += y_pad
    canvas.text(60, 32, title, color=INK, scale=3)
    canvas.text(60, 83, subtitle, color=MUTED, scale=2)
    canvas.text(left, top - 27, y_label, color=MUTED, scale=2)
    canvas.text(left + 180, bottom + 45, x_label, color=MUTED, scale=2)
    for index in range(6):
        fraction = index / 5
        y = round(bottom - fraction * (bottom - top))
        x = round(left + fraction * (right - left))
        canvas.line(left, y, right, y, GRID)
        canvas.line(x, top, x, bottom, GRID)
        canvas.text(35, y - 7, f"{ymin + fraction * (ymax - ymin):.1f}", MUTED)
        canvas.text(x - 12, bottom + 16, f"{xmin + fraction * (xmax - xmin):.1f}", MUTED)

    def project(x, y):
        px = round(left + (x - xmin) / (xmax - xmin) * (right - left))
        py = round(bottom - (y - ymin) / (ymax - ymin) * (bottom - top))
        return px, py

    canvas.line(left, top, left, bottom, INK, 2)
    canvas.line(left, bottom, right, bottom, INK, 2)
    return project


def draw_objective_points(canvas, project, points):
    groups = {}
    for run, alternative, x_value, y_value in points:
        groups.setdefault((x_value, y_value), []).append((run, alternative))

    for (x_value, y_value), entries in groups.items():
        point = project(x_value, y_value)
        if len(entries) == 1:
            run, alternative = entries[0]
            color = COLORS[SEEDS.index(run["seed"]) % len(COLORS)]
            canvas.circle(*point, 7, color)
            canvas.text(
                point[0] + 8,
                point[1] - 8,
                f"S{run['seed']}-A{alternative['number']}",
                color,
                1,
            )
            continue

        seeds = sorted(
            {run["seed"] for run, _ in entries},
            key=SEEDS.index,
            reverse=True,
        )
        for index, seed in enumerate(seeds):
            canvas.circle(
                *point,
                8 - index * 2,
                COLORS[SEEDS.index(seed) % len(COLORS)],
            )
        canvas.text(
            point[0] + 10,
            point[1] - 8,
            f"{len(entries)} ALT",
            INK,
            1,
        )


def make_plots(results):
    successful = [run for run in results if run["status"] == "OK"]
    genetic_runs = [run for run in successful if run["code"] == "IT2-EVAL-SOL"]
    if genetic_runs:
        canvas = Canvas()
        history = [
            (run, run["result"].get("history", [])) for run in genetic_runs
        ]
        x = [entry["generation"] for _, entries in history for entry in entries]
        y = [entry["fitness"] for _, entries in history for entry in entries]
        project = plot_axes(
            canvas,
            "GA SOLICITUDES: FITNESS POR GENERACION",
            "Mejor fitness de poblacion por llamada; mayor es mejor (0-100)",
            "Generacion",
            "Fitness",
            x,
            y,
        )
        for color_index, (run, entries) in enumerate(history):
            color = COLORS[color_index % len(COLORS)]
            points = [
                project(entry["generation"], entry["fitness"])
                for entry in entries
            ]
            for first, second in zip(points, points[1:]):
                canvas.line(*first, *second, color, 3)
            for point in points[::max(1, len(points) // 10)]:
                canvas.circle(*point, 4, color)
            label_x = 790
            label_y = 88 + color_index * 22
            canvas.line(label_x, label_y + 5, label_x + 28, label_y + 5, color, 3)
            canvas.text(label_x + 36, label_y, f"SEMILLA {run['seed']}", color, 2)
        canvas.png(HERE / "fitness_generacional_solicitudes.png")

    incident_runs = [run for run in successful if run["code"] == "IT2-EVAL-INC"]
    incident_points = [
        (run, alternative)
        for run in incident_runs
        for alternative in run["result"].get("alternatives", [])
    ]
    if incident_points:
        xs = [alternative["weighted_wait_hours"] for _, alternative in incident_points]
        ys = [alternative["load_imbalance"] for _, alternative in incident_points]
        canvas = Canvas()
        project = plot_axes(
            canvas,
            "NSGA-II INCIDENCIAS: OBJETIVOS DEVUELTOS",
            "Alternativas coincidentes: anillos concentricos y cantidad; no se afirma frente global",
            "Espera ponderada (h ponderadas), minimizar",
            "Desequilibrio de carga (asignaciones^2), minimizar",
            xs,
            ys,
        )
        draw_objective_points(
            canvas,
            project,
            [
                (
                    run,
                    alternative,
                    alternative["weighted_wait_hours"],
                    alternative["load_imbalance"],
                )
                for run, alternative in incident_points
            ],
        )
        for index, seed in enumerate(SEEDS):
            y = 95 + index * 22
            canvas.circle(820, y + 6, 6, COLORS[index])
            canvas.text(834, y, f"SEMILLA {seed}", COLORS[index], 2)
        canvas.png(HERE / "objetivos_nsga2_incidencias.png")

    team_runs = [run for run in successful if run["code"] == "IT2-EVAL-EQ"]
    team_points = [
        (run, alternative)
        for run in team_runs
        for alternative in run["result"].get("alternatives", [])
    ]
    if team_points:
        xs = [100 - alternative["fitness"] for _, alternative in team_points]
        ys = [alternative["projected_mean_workload"] for _, alternative in team_points]
        canvas = Canvas()
        project = plot_axes(
            canvas,
            "NSGA-II EQUIPO: OBJETIVOS PARA HORARIO FIJO",
            "Alternativas coincidentes: anillos concentricos y cantidad; menor es mejor",
            "100 - fitness (puntos), minimizar",
            "Carga media proyectada (asignaciones/tecnico), minimizar",
            xs,
            ys,
        )
        draw_objective_points(
            canvas,
            project,
            [
                (
                    run,
                    alternative,
                    100 - alternative["fitness"],
                    alternative["projected_mean_workload"],
                )
                for run, alternative in team_points
            ],
        )
        for index, seed in enumerate(SEEDS):
            y = 95 + index * 22
            canvas.circle(820, y + 6, 6, COLORS[index])
            canvas.text(834, y, f"SEMILLA {seed}", COLORS[index], 2)
        canvas.png(HERE / "objetivos_nsga2_equipo_horario_fijo.png")


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now().astimezone().isoformat(timespec="seconds")
    dataset = fake_dataset()
    (HERE / "datos_ficticios.json").write_text(
        json.dumps(dataset, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    results = execute(dataset)
    payload = {
        "evaluation": {
            "dataset_id": DATASET_ID,
            "seeds": list(SEEDS),
            "started_at": started_at,
            "completed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "timing": "time.perf_counter around the direct algorithm call",
            "database_accessed": False,
            "algorithms_modified": False,
        },
        "runs": results,
    }
    (HERE / "ejecuciones.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown(dataset, results)
    make_plots(results)
    failed = [run for run in results if run["status"] != "OK"]
    print(f"Dataset: {DATASET_ID}; ejecuciones: {len(results)}; fallidas: {len(failed)}")
    for run in results:
        print(
            f"{run['code']} seed={run['seed']} status={run['status']} "
            f"elapsed={run['elapsed_seconds']:.6f}s"
        )
        if run["status"] != "OK":
            print(f"  {run['error']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
