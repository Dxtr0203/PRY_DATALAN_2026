# Resultados de pruebas — Iteración 3

**Fecha:** 2026-10-31  
**Ejecución final:** [salida completa de consola](./registro_ejecucion_completa_2026-10-31.txt)  
**Alcance:** cuatro grupos funcionales; el total de métodos ejecutados se informa por separado.  
**Base exclusiva:** PostgreSQL `datalan_it3_test`, creada y eliminada por Django. Las pruebas nuevas verifican `current_database()` antes de las consultas SQL directas.

## Salidas separadas para capturas de pantalla

Cada archivo conserva el comando, fecha/hora, nombres de pruebas, salida de Django y resumen de su ejecución. Abre el TXT correspondiente para capturar el grupo que necesitas:

| Grupo importante | Pruebas ejecutadas | Resultado | Salida estilo terminal |
|---|---:|---|---|
| 1. Registro del reporte (P3-01, P3-02) | 2 | `Ran 2 tests` — `OK` | [terminal_grupo_1_registro_reporte.txt](./terminal_grupo_1_registro_reporte.txt) |
| 2. Designación del responsable técnico (P3-04, P3-05) | 1 | `Ran 1 test` — `OK` | [terminal_grupo_2_designacion_responsable.txt](./terminal_grupo_2_designacion_responsable.txt) |
| 3. Diagnóstico y registro de atención (P3-08, P3-09) | 3 | `Ran 3 tests` — `OK` | [terminal_grupo_3_diagnostico_atencion.txt](./terminal_grupo_3_diagnostico_atencion.txt) |
| 4. Verificación y cierre (P3-10, P3-11, P3-13) | 2 | `Ran 2 tests` — `OK` | [terminal_grupo_4_verificacion_cierre.txt](./terminal_grupo_4_verificacion_cierre.txt) |

Son **8 ejecuciones de prueba agrupadas**, con una prueba repetida entre los grupos 3 y 4 (7 métodos únicos en estas salidas). No confundir con la ejecución completa previa: **9 métodos** en total, registrada por separado en el TXT de ejecución completa.

## Resultados por requisito original P3

| Código P3 | Comprobación | Fecha | Resultado obtenido | Estado | Evidencia |
|---|---|---|---|---|---|
| P3-01 | El reporte se asocia al CITE del cliente/enlace PP activo seleccionado. | 2026-10-31 | Se registró el reporte con el CITE de un servicio cuya instalación y conclusión están aprobadas; SQL verificó el cliente, tipo de enlace y objeto de incidencia bajo ese CITE. | Aprobado | `test_report_is_linked_to_active_service_and_reloads_without_diagnosis`; `test_incident_report_rejects_uncompleted_service_without_saving` |
| P3-02 | La descripción se registra sin diagnóstico definitivo y se conserva al volver a consultar. | 2026-10-31 | El reporte se guardó sin campo `diagnosis`; SQL JSONB y `get_requests()` confirmaron la descripción y el estado inicial. | Aprobado | `test_report_is_linked_to_active_service_and_reloads_without_diagnosis` |
| P3-04 | Planta Técnica designa al responsable inicial. | 2026-10-31 | El encargado asignó un técnico disponible; SQL confirmó el nombre asignado y el estado `ASIGNADA`. | Aprobado | `test_assignment_permissions_preserve_data_and_expose_assignee`; `test_service_incident_runs_through_assignment_approval_and_resolution` |
| P3-05 | El técnico y Soporte pueden identificar al responsable; roles no autorizados no cambian la asignación y el rechazo conserva los datos. | 2026-10-31 | Las vistas de técnico y Soporte mostraron el responsable. Un intento de Encargado de Sistemas fue rechazado y una nueva consulta SQL mostró el JSONB sin cambios; luego el Encargado de Planta realizó la asignación válida. | Aprobado | `test_assignment_permissions_preserve_data_and_expose_assignee` |
| P3-08 | Diagnóstico, actividades, resultados y observaciones quedan vinculados a la incidencia correcta y persisten. | 2026-10-31 | Se registraron por el flujo y se consultaron en PostgreSQL el trabajo programado, el resultado de atención y el intento de solución. La aplicación no tiene campos independientes de diagnóstico ni de observaciones técnicas. | Parcial: diagnóstico y observaciones técnicas no comprobables con el modelo actual | `test_attention_activity_and_result_are_persisted_for_incident`; `test_persistent_solution_attempt_is_saved_and_does_not_close_incident` |
| P3-09 | Un resultado técnico confirmado queda disponible para Soporte y no cierra automáticamente el caso. | 2026-10-31 | Tras registrar solución `SOLUCIONADA`, el estado fue `SOLUCIÓN: COMPLETADA`; al enviar la conclusión quedó `PENDIENTE DE VALIDACIÓN`. La consulta de la vista de Soporte mostró el resultado antes de la aprobación. | Aprobado | `test_confirmed_solution_waits_for_support_review_before_closure`; `test_service_incident_runs_through_assignment_approval_and_resolution` |
| P3-10 | Soporte registra verificación del restablecimiento y cierra la incidencia confirmada. | 2026-10-31 | Soporte aprobó la conclusión incluyendo una nota de verificación; SQL confirmó el estado `CERRADA` y la nota preservada. | Aprobado | `test_support_verification_closes_and_preserves_incident_history`; `test_systems_manager_can_approve_and_close_support_reported_incident` |
| P3-11 | Si la falla persiste, la incidencia sigue abierta y conserva los antecedentes/observaciones. | 2026-10-31 | El intento con resultado `PERSISTE` se guardó en `attempts`, quedó en `SOLUCIÓN: PENDIENTE` y mantuvo la nota previa; Soporte pudo consultar el intento. | Aprobado | `test_persistent_solution_attempt_is_saved_and_does_not_close_incident` |
| P3-13 | Tras el cierre se consultan reporte, diagnóstico/atención, actividades, solución y verificación. | 2026-10-31 | Una nueva lectura del JSONB SQL y `get_requests()` recuperó reporte, descripción y resultado de atención, intento técnico, nota de verificación y estado `CERRADA`. No hay un diagnóstico independiente que pueda consultarse. | Parcial: el diagnóstico independiente no existe | `test_support_verification_closes_and_preserves_incident_history` |

## Alcance y observaciones de implementación

- Se ejecutan **6 pruebas de integración PostgreSQL** y **3 pruebas unitarias reutilizadas**: **9 métodos en total**. Son cuatro grupos de comprobación, no cuatro pruebas.
- Las pruebas unitarias reutilizadas usan datos simulados/mocks; la persistencia PostgreSQL y el estado de la base se acreditan con las seis pruebas de integración.
- Los reportes no se almacenan en una tabla independiente: `service_incidents` y sus etapas se guardan dentro del JSONB `datalan.solicitudes.extra_data`, relacionado al cliente y enlace mediante la fila de solicitud/CITE. La ejecución confirmó `current_database() = datalan_it3_test` antes de las consultas SQL directas.
- La aplicación no tiene campos estructurados independientes de diagnóstico ni de observaciones técnicas. La prueba valida los campos disponibles: `attention.work_description` (trabajo programado), `attention.result`, `solution.attempts[].result` y `conclusion.review_note` (observación de revisión de Soporte). Por ello P3-08 y P3-13 quedan parciales; no se atribuye al sistema una persistencia de diagnóstico que no implementa. El reporte inicial no exige un campo de diagnóstico.
- No existe una entidad separada de “verificación del servicio”: la ruta implementada usa la revisión de la conclusión de Soporte y guarda la observación en `conclusion.review_note`. La nota es opcional en la interfaz para aprobar; el caso probado la envía y verifica que persiste.
- No se ejecutó ni se calificó el algoritmo NSGA-II. Se probaron permisos y asignación del responsable inicial, no la selección optimizada de equipos.

## Comando para repetir

Desde PowerShell en la raíz del repositorio:

```powershell
$env:DJANGO_SETTINGS_MODULE = 'DATALAN.settings_iteration3_test'
Push-Location DATALAN
..\venv\Scripts\python.exe manage.py test DATALAN.test_iteration3_postgresql DATALAN.test_optimization_service.GeneticOptimizationTests.test_incident_report_rejects_uncompleted_service_without_saving DATALAN.test_optimization_service.GeneticOptimizationTests.test_systems_manager_can_approve_and_close_support_reported_incident DATALAN.test_optimization_service.GeneticOptimizationTests.test_service_incident_runs_through_assignment_approval_and_resolution --verbosity 2
Pop-Location
```

Para el informe, capturar el comando y la fecha, desde `Creating test database ... datalan_it3_test` hasta los nombres individuales de pruebas, `Ran 9 tests`, `OK`, `System check identified no issues` y la destrucción de la base de prueba. La última ejecución capturada terminó con `PROCESS_EXIT=0`.
