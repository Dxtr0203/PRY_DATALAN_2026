# Pruebas individuales — Iteración 2 de DATALAN

**Fecha de ejecución:** 2026-10-31  
**Ejecuciones independientes:** 16 métodos, una invocación por método.  
**Resultado:** 16 invocaciones terminaron con `OK` y `RETURN_CODE=0`.  
**Grupos funcionales cubiertos:** 4.  
**Evidencia de consola:** [salidas completas de cada ejecución](./ejecuciones_individuales_2026-10-31.txt).
**Comando preparado para capturas por punto:** [ejecutar_prueba_por_punto.ps1](./ejecutar_prueba_por_punto.ps1).

## Tipo de prueba y entorno

- **Integración PostgreSQL (7 métodos):** usan `django.test.TestCase`; cada ejecución creó y destruyó la base exclusiva `datalan_it2_test`. Incluyen consultas SQL directas, comprobación de estados y recarga de datos cuando se indica en el resultado.
- **Unitaria/de flujo (9 métodos):** usan `SimpleTestCase`; validan reglas o respuestas del flujo sin persistencia PostgreSQL. La consola indica `Skipping setup of unused database(s): default.`
- Cada método se ejecutó por separado con `manage.py test <etiqueta completa> --verbosity 2`. Por eso, el resumen de cada bloque dice `Ran 1 test`, no 16.
- La preparación de la base aislada fue realizada por Django. Ninguna ejecución usó la base operativa.

## Registro y prioridad de solicitudes

| Punto comprobado | Tipo y prueba ejecutada | Resultado de consola y resultado observado |
|---|---|---|
| Rechazo de registros con solicitante, correo o tipo incompletos (P2-01). | Integración PostgreSQL: `test_registration_rejects_missing_fields_and_checks_priority_boundaries`. El método prueba cada campo obligatorio faltante y consulta que no se insertó la solicitud. | `test_registration_rejects_missing_fields_and_checks_priority_boundaries ... ok`; `Ran 1 test`; `OK`; `RETURN_CODE=0`. Los casos incompletos fueron rechazados. |
| Guardado y consulta de solicitudes permanentes y eventuales conservando sus datos (P2-02). | Integración PostgreSQL: `test_permanent_and_eventual_registration_persist_and_reload`. Consulta SQL directa y recarga mediante `get_requests()`. | `test_permanent_and_eventual_registration_persist_and_reload ... ok`; `Ran 1 test`; `OK`; `RETURN_CODE=0`. Ambos tipos y sus datos fueron recuperados. |
| Prioridad en 0, 3, 4, 7 y 8 días (P2-03). | Integración PostgreSQL: `test_registration_rejects_missing_fields_and_checks_priority_boundaries`. Pruebas unitarias complementarias: `test_installation_schedule_derives_priority_from_installation_date` y `test_eventual_schedule_uses_start_date_and_requires_valid_range`. | Las tres salidas muestran `... ... ok`, `Ran 1 test`, `OK` y `RETURN_CODE=0`. La integración confirmó Alta, Alta, Media, Media y Baja, respectivamente; las unitarias verificaron las reglas de fecha de instalación y fecha DE eventual. |

## Decisión comercial

| Punto comprobado | Tipo y prueba ejecutada | Resultado de consola y resultado observado |
|---|---|---|
| Conservación de las evaluaciones de Planta Técnica y Sistemas (P2-06). | Integración PostgreSQL: `test_commercial_approval_preserves_evaluations_and_resolution_note`. Verifica datos guardados con SQL. | `test_commercial_approval_preserves_evaluations_and_resolution_note ... ok`; `Ran 1 test`; `OK`; `RETURN_CODE=0`. |
| Registro de aprobación o rechazo final de Comercial (P2-06). | Integración PostgreSQL: `test_commercial_approval_preserves_evaluations_and_resolution_note` y `test_commercial_rejection_is_persisted_and_blocks_execution`. Unitarias complementarias: `test_commercial_decision_supports_ajax_without_redirect` y `test_commercial_final_approval_overrides_an_area_rejection`. | Las cuatro ejecuciones terminaron con `... ... ok`, `Ran 1 test`, `OK` y `RETURN_CODE=0`. La aprobación y el rechazo quedaron registrados; también se comprobó la respuesta AJAX y el carácter final de la decisión comercial. |
| Conservación de la observación original y de la explicación al resolverla (P2-07). | Integración PostgreSQL: `test_commercial_approval_preserves_evaluations_and_resolution_note`. Consulta SQL directa de observaciones y nota comercial. | `test_commercial_approval_preserves_evaluations_and_resolution_note ... ok`; `Ran 1 test`; `OK`; `RETURN_CODE=0`. Las observaciones originales y la explicación se conservaron. |
| Una solicitud rechazada no continúa a ejecución (P2-06). | Integración PostgreSQL: `test_commercial_rejection_is_persisted_and_blocks_execution`. Comprueba estado y que no se asigne técnico al intentar avanzar. | `test_commercial_rejection_is_persisted_and_blocks_execution ... ok`; `Ran 1 test`; `OK`; `RETURN_CODE=0`. La solicitud permaneció rechazada y no avanzó a asignación técnica. |

## Coordinación de cronogramas

| Punto comprobado | Tipo y prueba ejecutada | Resultado de consola y resultado observado |
|---|---|---|
| Cronograma tentativo vinculado a la solicitud y actividad correctas (P2-10). | Integración PostgreSQL: `test_installation_schedule_submission_approval_and_reload`. | `test_installation_schedule_submission_approval_and_reload ... ok`; `Ran 1 test`; `OK`; `RETURN_CODE=0`. El cronograma enviado se asoció a la solicitud y a la etapa de instalación. |
| Diferencia entre el cronograma enviado y el aprobado (P2-11). | Integración PostgreSQL: `test_installation_schedule_submission_approval_and_reload`. Compara fechas/horas tentativas con los campos aprobados guardados. | `test_installation_schedule_submission_approval_and_reload ... ok`; `Ran 1 test`; `OK`; `RETURN_CODE=0`. La propuesta y el horario aprobado quedaron diferenciados. |
| Conservación y consulta posterior del horario aprobado (P2-11). | Integración PostgreSQL: `test_installation_schedule_submission_approval_and_reload`. Verificación SQL y recarga posterior. | `test_installation_schedule_submission_approval_and_reload ... ok`; `Ran 1 test`; `OK`; `RETURN_CODE=0`. El horario aprobado se conservó y pudo consultarse al recargar. |
| Preparación de equipo requerida para aprobar el cronograma. | Dato de preparación de la prueba de integración anterior; no es una evaluación del algoritmo. | Se utilizó una propuesta ficticia válida de equipo en los datos JSONB de prueba, con identificador, líder/miembro, fitness y firma de fechas/horas coincidente con la aprobación. No se ejecutó ni evaluó el algoritmo de propuestas. La prueba de aprobación terminó `OK`. |

## Conclusión de solicitudes permanentes y eventuales

| Punto comprobado | Tipo y prueba ejecutada | Resultado de consola y resultado observado |
|---|---|---|
| Enviar una conclusión no la aprueba automáticamente (P2-13). | Integración PostgreSQL: `test_permanent_conclusion_requires_support_approval_for_active_link` y `test_eventual_service_stays_open_until_removal_and_final_review`. Unitaria de flujo complementaria: `test_delivery_stages_go_from_inspection_to_installation_and_conclusion`. | Las tres ejecuciones terminaron con `... ... ok`, `Ran 1 test`, `OK` y `RETURN_CODE=0`. Tras enviar, la etapa quedó pendiente de aprobación. |
| La aprobación de instalación permanente concluye la etapa y registra el enlace como activo (P2-13). | Integración PostgreSQL: `test_permanent_conclusion_requires_support_approval_for_active_link`. Comprueba estado persistido, `concluded_at` y estado derivado tras recargar. | `test_permanent_conclusion_requires_support_approval_for_active_link ... ok`; `Ran 1 test`; `OK`; `RETURN_CODE=0`. La solicitud quedó `FINALIZADA` y el listado recargado mostró `ACTIVO`. `ACTIVO` es un estado derivado de la solicitud guardada; la prueba no afirma una escritura en un registro independiente de enlaces. |
| La instalación eventual conserva el periodo y deja pendiente el retiro (P2-15). | Integración PostgreSQL: `test_eventual_service_stays_open_until_removal_and_final_review`. Unitaria complementaria: `test_operational_stage_display_tracks_regular_and_eventual_progress`. | Ambas ejecuciones terminaron con `... ... ok`, `Ran 1 test`, `OK` y `RETURN_CODE=0`. El periodo se recargó intacto y el retiro permaneció pendiente; no se permitió concluir antes del retiro. |
| La aprobación del retiro permite concluir la solicitud eventual si no hay actividades pendientes (P2-16, P2-17). | Integración PostgreSQL: `test_eventual_service_stays_open_until_removal_and_final_review`. Unitaria complementaria: `test_eventual_installation_can_only_finish_after_approved_removal`. | Ambas ejecuciones terminaron con `... ... ok`, `Ran 1 test`, `OK` y `RETURN_CODE=0`. Con el retiro completado, se habilitó el envío y aprobación final; se guardaron `FINALIZADA` y `concluded_at`. La prueba no evaluó un listado general de otras tareas pendientes. |

## Ejecuciones que no se cuentan como cobertura del alcance

También se ejecutó `test_incident_candidates_require_completed_non_eventual_pp_or_mp` porque formaba parte de la selección previa. Su invocación individual terminó `OK`, pero trata de candidatos a incidentes y no acredita ninguno de los puntos solicitados aquí. Por tanto, el total real fue **16 invocaciones**, de las cuales **15 se relacionan con el alcance** y una es suplementaria; no se usa para declarar cubierto un requisito de Iteración 2.

## Repetir una sola prueba

Para que la terminal muestre el identificador P2, la explicación, el comando y la salida real juntos, desde PowerShell en la raíz del repositorio ejecuta **una sola línea por captura**:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-01
```

Repite individualmente con cada identificador de esta tabla. Espera a que aparezca `RETURN_CODE=0` antes de tomar la captura. El registro previo de cada prueba confirmó `OK`; al repetir, la terminal mostrará el resultado actual.

| Punto para capturar | Comando |
|---|---|
| P2-01 — Registro incompleto | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-01` |
| P2-02 — Guardado y recarga | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-02` |
| P2-03 — Límites de prioridad | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-03` |
| P2-06 — Evaluaciones de áreas | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-06-EVAL` |
| P2-06 — Decisión final | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-06-DECISION` |
| P2-06 — Bloqueo del rechazo | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-06-BLOQUEO` |
| P2-07 — Observación y explicación | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-07` |
| P2-10 — Cronograma tentativo | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-10` |
| P2-11 — Horario aprobado | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-11` |
| P2-13 — Envío permanente sin aprobación automática | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-13-ENVIO-PERMANENTE` |
| P2-13 — Envío eventual sin aprobación automática | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-13-ENVIO-EVENTUAL` |
| P2-13 — Aprobación y enlace activo | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-13-ACTIVO` |
| P2-15 — Periodo y retiro pendiente | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-15` |
| P2-16/P2-17 — Retiro y conclusión eventual | `powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\pruebas_iteracion_2\ejecutar_prueba_por_punto.ps1 P2-16-17` |

La captura debe mostrar el encabezado `PUNTO` y `COMPROBACION`, el nombre de la prueba terminado en `... ok`, el resumen (`Ran 1 test` o, para la decisión final, `Ran 2 tests`), `OK` y `RETURN_CODE=0`. Para las pruebas PostgreSQL también aparecerá la creación y destrucción de la base exclusiva `datalan_it2_test`.
