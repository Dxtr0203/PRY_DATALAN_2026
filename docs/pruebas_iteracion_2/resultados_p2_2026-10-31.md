# Resultados ejecutados — Iteracion 2 de DATALAN

**Fecha:** 2026-10-31  
**Ejecucion completa:** [registro_ejecucion_completa_2026-10-31.txt](./registro_ejecucion_completa_2026-10-31.txt)  
**Resultado del runner:** 16 pruebas ejecutadas, `OK`, codigo de retorno 0. Se cubrieron los cuatro grupos solicitados; 16 es el numero de pruebas/metodos reportado por Django, no el numero de requisitos P2.
**Ejecuciones por separado:** [detalle de pruebas individuales y tipos](./detalle_pruebas_individuales_2026-10-31.md), con la salida completa de cada invocación en [ejecuciones_individuales_2026-10-31.txt](./ejecuciones_individuales_2026-10-31.txt).

Este es el registro vigente para esta ejecucion. Los documentos fechados 2026-10-26 dentro de la carpeta se conservan como antecedentes y no describen esta corrida PostgreSQL.

## Alcance y entorno

- Siete pruebas nuevas de integracion ejecutan las rutas de registro/decision y los manejadores de etapas con funciones reales de persistencia.
- PostgreSQL se conecto a la base administrativa `postgres` solo para que Django creara la base de prueba exclusiva `datalan_it2_test`. Las pruebas verifican `current_database()` antes de preparar datos. Django destruyo la base de prueba al terminar.
- Dentro de esa base desechable las pruebas crean un esquema minimo `datalan` compatible con el adaptador de persistencia utilizado. No se conectaron a la base operativa `datalan` ni se uso el script de inicializacion con datos demo.
- Las comprobaciones de persistencia ejecutan consultas SQL directas a `datalan.solicitudes`, sus relaciones de prioridad/estado y el JSONB `extra_data`; despues vuelven a cargar por `get_requests()`.
- Los otros nueve metodos son pruebas existentes `SimpleTestCase` seleccionadas por su relacion con el alcance; usan datos de prueba y no comprueban persistencia PostgreSQL.
- El repositorio no contiene el catalogo original de requisitos P2 con sus descripciones. La tabla conserva los identificadores facilitados en la solicitud y relaciona cada uno con las comprobaciones solicitadas; no afirma cobertura de otros casos no enumerados.

## Tabla de resultados por codigo P2

| Codigo original P2 | Comprobacion | Fecha | Resultado obtenido | Estado | Evidencia |
|---|---|---|---|---|---|
| P2-01 | El registro incompleto se rechaza al faltar, individualmente, solicitante, correo o tipo; no se inserta una solicitud. | 2026-10-31 | Los tres subcasos fueron rechazados; consulta SQL de solicitudes: cero filas. | Aprobado | `test_registration_rejects_missing_fields_and_checks_priority_boundaries` |
| P2-02 | Registro permanente y eventual, guardado de datos y consulta posterior desde PostgreSQL. | 2026-10-31 | Se persistieron ambos tipos y se recargaron CITE, datos de puntos, correo, fechas y prioridad. | Aprobado | `test_permanent_and_eventual_registration_persist_and_reload`; SQL directo y `get_requests()` |
| P2-03 | Prioridad en 0, 3, 4, 7 y 8 dias; eventual prioriza la fecha DE y no HASTA. | 2026-10-31 | Limites: Alta, Alta, Media, Media y Baja. Registro eventual con DE +3/HASTA +8 quedo Alta en PostgreSQL. | Aprobado | `test_registration_rejects_missing_fields_and_checks_priority_boundaries`; `test_permanent_and_eventual_registration_persist_and_reload`; `test_installation_schedule_derives_priority_from_installation_date`; `test_eventual_schedule_uses_start_date_and_requires_valid_range` |
| P2-06 | Conservacion de evaluaciones y decision final comercial; el rechazo bloquea la asignacion tecnica. | 2026-10-31 | Aprobacion y rechazo se guardaron. La solicitud rechazada mantuvo su estado y no recibio tecnico al intentar asignarlo. | Aprobado | `test_commercial_approval_preserves_evaluations_and_resolution_note`; `test_commercial_rejection_is_persisted_and_blocks_execution`; `test_commercial_decision_supports_ajax_without_redirect` |
| P2-07 | Observaciones originales conservadas y explicacion comercial guardada al aprobar tras resolver una observacion. | 2026-10-31 | Las observaciones de ambas areas permanecieron en JSONB; la explicacion se guardo en la nota del historial comercial. | Aprobado | `test_commercial_approval_preserves_evaluations_and_resolution_note`; consulta SQL directa |
| P2-10 | Cronograma tentativo asociado a la CITE y actividad de instalacion. | 2026-10-31 | El tecnico envio la etapa `installation` con sus puntos, fechas, horas y descripciones; fue recargada de PostgreSQL. | Aprobado | `test_installation_schedule_submission_approval_and_reload` |
| P2-11 | Diferencia entre propuesta tentativa y aprobada; conservar y volver a consultar el horario aprobado. | 2026-10-31 | Soporte aprobo fechas/horas distintas; JSONB conserva `date` tentativa y `scheduled_date`/`scheduled_time` aprobadas, junto al equipo asignado. | Aprobado | `test_installation_schedule_submission_approval_and_reload`; SQL directo y `get_requests()` |
| P2-13 | Enviar conclusion no la aprueba; Soporte revisa y la aprobacion cierra instalacion permanente. | 2026-10-31 | Tras el envio quedo `ENVIADA`; tras aprobar, estado `FINALIZADA`, `concluded_at` registrado y el listado comercial mostro `ACTIVO` al recargar la solicitud. | Aprobado | `test_permanent_conclusion_requires_support_approval_for_active_link`; `test_delivery_stages_go_from_inspection_to_installation_and_conclusion` |
| P2-15 | Servicio eventual conserva su periodo y permanece abierto con retiro pendiente tras instalar. | 2026-10-31 | Fechas DE/HASTA se recargaron intactas; se mostro retiro en espera y el envio temprano de conclusion fue rechazado. | Aprobado | `test_eventual_service_stays_open_until_removal_and_final_review`; `test_operational_stage_display_tracks_regular_and_eventual_progress` |
| P2-16 | Gestion y aprobacion del retiro eventual con una propuesta de equipo valida. | 2026-10-31 | La propuesta de prueba fue aceptada; Soporte guardo el cronograma aprobado y el tecnico registro el retiro. | Aprobado | `test_eventual_service_stays_open_until_removal_and_final_review`; propuesta fixture en `genetic_team_proposals.removal` |
| P2-17 | Tras el retiro y sin otras actividades pendientes en el caso, enviar y aprobar conclusion eventual. | 2026-10-31 | El retiro completado habilito el envio; la aprobacion final guardo `FINALIZADA` y `concluded_at`, manteniendo el periodo. | Aprobado | `test_eventual_service_stays_open_until_removal_and_final_review`; SQL directo y `get_requests()` |

## Precisiones sobre el comportamiento verificado

1. Las propuestas de equipo de los cronogramas fueron registros ficticios incluidos en JSONB para satisfacer el requisito de aprobacion: identificador `0`, tecnico lider/miembro, ID de miembro, fitness y firma de fechas/horas coincidente con la aprobacion. No se ejecuto ni evaluo el algoritmo de propuestas.
2. No hay una tabla/campo persistido independiente que marque un enlace como activo en esta ruta. El listado comercial ahora deriva y muestra `ACTIVO` cuando la solicitud recargada cumple `is_completed_active_point_link()`: instalacion realizada, conclusion aprobada y solicitud `FINALIZADA`. El estado se deriva de la solicitud guardada; no se reporta una escritura en un registro separado de enlaces.
3. La conclusion eventual se habilita mediante la condicion `removal_completed`. En la prueba no habia otras actividades pendientes; el flujo no comprobo una lista general de tareas pendientes.
4. No se ejecutaron navegador, pruebas manuales ni la suite completa. Tampoco se verificaron los codigos P2 que no aparecen en la solicitud.

## Repeticion

Desde PowerShell, en la raiz del repositorio:

```powershell
$env:DJANGO_SETTINGS_MODULE='DATALAN.settings_iteration2_test'
Push-Location DATALAN
..\venv\Scripts\python.exe manage.py test DATALAN.test_iteration2_postgresql DATALAN.test_optimization_service.GeneticOptimizationTests.test_installation_schedule_derives_priority_from_installation_date DATALAN.test_optimization_service.GeneticOptimizationTests.test_eventual_schedule_uses_start_date_and_requires_valid_range DATALAN.test_optimization_service.GeneticOptimizationTests.test_commercial_decision_supports_ajax_without_redirect DATALAN.test_optimization_service.GeneticOptimizationTests.test_commercial_final_approval_overrides_an_area_rejection DATALAN.test_optimization_service.GeneticOptimizationTests.test_delivery_stages_go_from_inspection_to_installation_and_conclusion DATALAN.test_optimization_service.GeneticOptimizationTests.test_eventual_installation_can_only_finish_after_approved_removal DATALAN.test_optimization_service.GeneticOptimizationTests.test_incident_candidates_require_completed_non_eventual_pp_or_mp DATALAN.test_optimization_service.GeneticOptimizationTests.test_operational_stage_display_tracks_regular_and_eventual_progress DATALAN.test_optimization_service.GeneticOptimizationTests.test_commercial_request_saves_derived_priority_port_and_dates --verbosity 2
Pop-Location
```

Para una captura de terminal, incluye el comando y su entorno, la linea `Found 16 test(s).`, los nombres de las pruebas, `Ran 16 tests`, `OK`, `System check identified no issues` y el codigo de salida `0`. No es necesario capturar la ejecucion de algoritmos ni una base operativa.
