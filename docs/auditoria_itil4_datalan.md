# Auditoría técnica de DATALAN y su relación con ITIL 4

**Fecha de revisión:** 12 de noviembre de 2026  
**Alcance:** código y documentación actualmente presentes en el repositorio de trabajo.  
**Propósito:** aportar evidencia técnica para delimitar qué prácticas de ITIL 4 se pueden atribuir al sistema, cómo se relacionan con sus funciones y qué afirmaciones conviene evitar en la tesis.

> **Criterio de interpretación:** una función parecida a una actividad de ITIL no demuestra por sí sola la adopción de toda una práctica. Este informe distingue entre implementación del software, pruebas documentadas y adopción organizacional. La auditoría no certifica conformidad con ITIL 4.

## A. Resumen ejecutivo

DATALAN es una aplicación Django para registrar y tramitar solicitudes de servicios de fibra óptica, coordinar actividades técnicas y atender incidencias vinculadas a servicios instalados. Su código define roles de Comercial, Encargado de Sistemas, Encargado de Planta Técnica, Soporte, Técnico y Administrador; ofrece pantallas y rutas específicas; y persiste solicitudes y flujos de trabajo mediante PostgreSQL. Las solicitudes incluyen información operativa, estado, fechas, evaluaciones e historial. Los reportes de incidencias se relacionan con la solicitud/enlace que los origina y se guardan dentro de los datos adicionales de esa solicitud.

La evidencia más sólida corresponde a dos prácticas seleccionadas y adaptadas al proceso de DATALAN:

1. **Service Request Management (Gestión de solicitudes de servicio):** se observan recepción, validación, evaluación por áreas, decisión comercial, coordinación, ejecución de etapas y conclusión.
2. **Incident Management (Gestión de incidentes):** se observan reporte ligado a un servicio activo, asignación, programación, atención, registro de resultado, solución, revisión por Soporte y cierre; los intentos sin solución pueden permanecer abiertos.

La correspondencia es **parcial y contextual**, no una implantación integral de esas prácticas en toda la organización. Las cinco fases propuestas para cada proceso son una adaptación académica del flujo DATALAN, no fases oficiales obligatorias de ITIL 4.

El sistema también contiene funciones de plazos internos, perfiles de soporte, registros, historial y optimización. Esas funciones pueden relacionarse con otras prácticas, pero la evidencia no basta para declarar implementadas de forma completa Service Level Management, Service Desk, Problem Management, Monitoring and Event Management, Measurement and Reporting, Continual Improvement o Service Configuration Management. En particular, el repositorio no acredita SLA formales vigentes para este estudio.

Los algoritmos genéticos (AG) y NSGA-II generan asignaciones o equipos recomendados. No son prácticas de ITIL 4 y no sustituyen la aprobación de una persona autorizada. En los flujos relevantes se valida después la propuesta y se persisten la decisión y el cambio de estado.

### Alcance y cautelas de esta revisión

- Se revisó el código Django en `DATALAN/DATALAN/`, las pruebas automatizadas disponibles, esquemas y documentación del repositorio.
- El árbol de trabajo contiene cambios locales y archivos sin seguimiento, incluidos archivos del proyecto Django. Por ello, las conclusiones describen el **estado de los archivos presentes en la revisión**, no necesariamente un commit publicado o desplegado.
- No se inspeccionó una instalación productiva ni se validó una instancia de navegador en ejecución.
- Se intentó ejecutar `python manage.py test --verbosity 1` desde `DATALAN/`. Django detectó **219 pruebas**, pero la ejecución se detuvo durante la preparación: la base PostgreSQL `test_datalan` ya existía y el proceso solicitó confirmación para eliminarla; al no haber entrada interactiva, terminó con `EOFError`. **No se completó esa suite en esta auditoría.**
- El repositorio conserva resultados previos de pruebas focalizadas fechados el 31 de octubre de 2026: Iteración 2 reporta 16 pruebas `OK` e Iteración 3 reporta 9 pruebas `OK`. Son resultados documentados de ejecuciones anteriores, no una repetición realizada para este informe.
- No se borró ninguna base de datos ni se modificó código de la aplicación.

### Estados de evidencia utilizados

| Estado | Significado en este informe |
|---|---|
| **IMPLEMENTADO Y VERIFICADO** | La función está en el código y hay una prueba o resultado de ejecución documentado que la ejercita. Si el resultado es histórico y no se repitió en esta auditoría, se indica como tal. |
| **IMPLEMENTADO SIN PRUEBA LOCALIZADA** | Hay código funcional identificable, pero no se ubicó una prueba que demuestre directamente ese caso. |
| **IMPLEMENTACIÓN PARCIAL** | Hay un subconjunto de capacidades relacionadas, pero faltan elementos necesarios para afirmar la práctica o el proceso en su totalidad. |
| **SOLO DOCUMENTADO** | La afirmación aparece en documentación, pero no se ubicó evidencia de implementación en el código inspeccionado. |
| **NO ENCONTRADO** | No se identificó evidencia suficiente en el alcance revisado. No equivale a afirmar que no exista fuera del repositorio. |

### Roles y funciones observadas

Los roles se definen en `ROLES` y los módulos se limitan según sesión/configuración. Las rutas se mapean en `urls.py`; la autorización de las operaciones concretas se vuelve a revisar en las vistas.

| Rol | Funciones observadas | Operaciones/datos que puede modificar en los flujos revisados | Rutas representativas |
|---|---|---|---|
| **Comercial** | Registrar/derivar solicitudes, consultar casos, emitir decisión comercial y consultar enlaces/estado. | Datos de solicitud en etapa comercial, decisión y razón/historial. | `/comercial/`, `/comercial/solicitudes/nueva/`, `/comercial/solicitudes/decidir/<cite>/`. |
| **Encargado de Sistemas** | Revisar solicitudes, mantener registros/configuraciones, gestionar propuestas/optimización y atender incidencias reportadas por Sistemas o Soporte en casos autorizados. | Resultado de revisión, asignaciones/configuración y revisión de incidencias permitida por el flujo. | `/sistemas/`, `/sistemas/solicitudes/`, `/sistemas/optimizacion/`, `/sistemas/incidencias/`. |
| **Encargado de Planta Técnica** | Evaluar solicitudes, administrar técnicos/perfiles y asignar técnico inicial a incidencias. | Evaluación, capacidades/perfiles y asignación técnica inicial. | `/planta-tecnica/encargado/`, `/planta-tecnica/encargado/solicitudes/`, `/planta-tecnica/encargado/incidencias/`, `/planta-tecnica/encargado/tecnicos/`. |
| **Soporte de Sistemas** | Reportar y gestionar solicitudes/incidencias asignadas; coordinar/confirmar cronogramas y revisar conclusiones cuando está autorizado. | Asignación operativa habilitada, aprobación/revisión de etapas e historial asociado. | `/sistemas/soporte/`, `/sistemas/soporte/solicitudes/`, `/sistemas/soporte/incidencias/`. |
| **Técnico** | Consultar trabajos asignados, proponer horarios, iniciar trabajo y registrar resultados de etapas e incidencias. | Su cronograma tentativo y resultados técnicos; no puede aprobar su propia conclusión en los casos descritos. | `/planta-tecnica/tecnico/`, `/planta-tecnica/tecnico/trabajos/`, `/planta-tecnica/tecnico/reportar/`. |
| **Administrador** | Administrar usuarios, roles/módulos y registros administrativos. | Cuentas, estado de usuario y accesos, sujeto a las restricciones implementadas. | `/usuarios/`, `/roles-accesos/`, `/actividad/`. |

Evidencia transversal: [`auth_service.py`, roles](../DATALAN/DATALAN/auth_service.py#L8), [`urls.py`, rutas](../DATALAN/DATALAN/urls.py#L20), y [`views.py`, autorización en `workflow()`](../DATALAN/DATALAN/views.py#L3845). La tabla resume capacidades observadas; no implica que todos los usuarios de una organización real tengan esas responsabilidades ni reemplaza la matriz formal de permisos del proyecto.

### Rangos de línea de las funciones principales

Los enlaces del informe saltan al inicio de cada función; los rangos que delimitan las funciones verificadas son:

| Archivo | Función | Líneas |
|---|---|---:|
| [`views.py`](../DATALAN/DATALAN/views.py) | `is_completed_active_point_link()` | 942–959 |
| [`views.py`](../DATALAN/DATALAN/views.py) | `handle_service_incident_workflow_post()` | 1200–1660 |
| [`views.py`](../DATALAN/DATALAN/views.py) | `handle_sla_post()` | 1663–1686 |
| [`views.py`](../DATALAN/DATALAN/views.py) | `installation_priority()` / `installation_schedule()` | 1689–1730 |
| [`views.py`](../DATALAN/DATALAN/views.py) | `workflow_updates()` | 1941–2086 |
| [`views.py`](../DATALAN/DATALAN/views.py) | `handle_operational_stage_post()` | 2099–2381 |
| [`views.py`](../DATALAN/DATALAN/views.py) | `generate_operational_team_proposals()` | 3165–3312 |
| [`views.py`](../DATALAN/DATALAN/views.py) | `generate_service_incident_team_proposals()` | 3317–3451 |
| [`views.py`](../DATALAN/DATALAN/views.py) | `workflow()` | 3845–5585 |
| [`workflow_service.py`](../DATALAN/DATALAN/workflow_service.py) | `save_requests()` / `add_history()` | 119–152 / 291–293 |
| [`optimization_service.py`](../DATALAN/DATALAN/optimization_service.py) | `run_genetic_team_optimization()` / `run_genetic_optimization()` | 582–793 / 2426–2527 |
| [`optimization_service.py`](../DATALAN/DATALAN/optimization_service.py) | `run_incident_nsga2()` / `run_incident_team_nsga2()` | 1456–1681 / 1684–2072 |

## B. Prácticas ITIL 4 identificadas

| Práctica ITIL 4 | Propósito en términos generales | Elementos observados en DATALAN | Evaluación |
|---|---|---|---|
| **Service Request Management** — Gestión de solicitudes de servicio | Gestionar solicitudes de servicio acordadas y su atención. | Registro de solicitudes permanentes y eventuales, evaluaciones, decisiones, coordinación técnica, ejecución y conclusión. | **Seleccionada e incorporada parcialmente/adaptada.** Hay flujo de aplicación y evidencia de pruebas focalizadas. No demuestra una práctica organizacional integral ni catálogo formal de solicitudes. |
| **Incident Management** — Gestión de incidentes | Minimizar el impacto de incidentes mediante la restauración oportuna del servicio normal. | Reportes de fallas de enlaces activos, asignación, coordinación, atención, intentos de solución, revisión y cierre. | **Seleccionada e incorporada parcialmente/adaptada.** El flujo está en código y hay pruebas focalizadas documentadas. No se demuestra operación productiva ni todos los elementos de una práctica completa. |
| **Service Level Management** — Gestión de niveles de servicio | Establecer objetivos de servicio y asegurar que la entrega se evalúe frente a ellos. | Configuración de metas de tiempo internas por fase y cálculos asociados en `sla_service.py`. | **Elemento relacionado; no declarar práctica completa.** DATALAN no cuenta con SLA formales definidos para este estudio; valores sugeridos o configurables no son compromisos contractuales. |
| **Service Desk** — Mesa de servicio | Proporcionar un punto de contacto eficaz entre usuarios y proveedor del servicio. | Pantallas de Soporte y Sistemas para reportar, consultar y tramitar solicitudes e incidencias. | **Elemento relacionado.** Hay funciones de atención, pero no evidencia suficiente de una mesa de servicio completa con operación, catálogo, niveles, medición y gobierno formal. |
| **Problem Management** — Gestión de problemas | Reducir la probabilidad e impacto de incidentes mediante identificación de causas y gestión de problemas/conocidos. | Se guardan descripciones, actividades, intentos de solución y resultados de incidentes individuales. | **No encontrada como práctica.** No se identificó un registro de problemas separado ni flujo estructurado de causa raíz, errores conocidos o análisis de recurrencia. |
| **Monitoring and Event Management** — Monitorización y gestión de eventos | Observar servicios y componentes, identificar eventos y responder a ellos. | Se consultan estados e historiales de casos. | **No encontrada como práctica.** Consultar el estado de solicitudes/incidencias no demuestra telemetría ni detección automatizada de eventos de red. |
| **Measurement and Reporting** — Medición y generación de informes | Apoyar decisiones mediante mediciones y reportes confiables. | Hay vistas de registro y resultados/configuraciones de optimización. | **Elementos parciales.** No se halló evidencia suficiente de un marco integral de indicadores, gobierno, revisión periódica y reporting de toda la práctica. |
| **Continual Improvement** — Mejora continua | Mantener una práctica sistemática para identificar y ejecutar mejoras. | Hay ajustes de parámetros y pruebas del software. | **No demostrada como práctica.** Cambiar parámetros o corregir software no prueba por sí mismo un proceso institucional de mejora continua. |
| **Service Configuration Management** — Gestión de configuración del servicio | Mantener información confiable sobre los elementos de configuración y sus relaciones. | Se almacenan configuraciones de algoritmos, perfiles técnicos y datos operativos. | **Elemento relacionado, práctica no demostrada.** No se encontró una CMDB ni un modelo que gestione de forma integral elementos de configuración y relaciones del servicio. |

**Conclusión de selección:** con la evidencia actual se recomienda declarar **dos prácticas seleccionadas e incorporadas parcialmente o de forma adaptada**: Service Request Management e Incident Management. No se recomienda presentar otras prácticas como incorporadas sin evidencia adicional, delimitación de alcance y criterios de aceptación explícitos.

## C. Correspondencia de Service Request Management

### Flujo respaldado por el código

El flujo general reconocible es:

**registro → evaluación de Planta Técnica/Sistemas → decisión comercial → asignación y programación → ejecución de las etapas pertinentes → revisión/conclusión.**

La aplicación distingue solicitudes eventuales de las permanentes. Para una solicitud eventual se validan fecha de inicio y fecha de fin; el retiro eventual se gestiona como etapa propia y el proceso no se considera concluido simplemente por la instalación. Estos son comportamientos del proceso implementado por DATALAN, no una secuencia impuesta por ITIL 4.

| Actividad | Responsable(s) | Comportamiento que se observa | Datos y estados relevantes | Evidencia y pruebas |
|---|---|---|---|---|
| Registro y derivación | Comercial | La vista `workflow()` procesa registro, edición permitida, derivación y acciones comerciales. `save_requests()` valida que exista el esquema y persiste los cambios. | CITE, solicitante/cliente, tipo, requisitos, prioridad, fechas, estado, fechas de recepción/derivación e historial. | [`views.py`, `workflow()` y acciones POST](../DATALAN/DATALAN/views.py#L3845); [`workflow_service.py`, `save_requests()`](../DATALAN/DATALAN/workflow_service.py#L119); [`test_iteration2_postgresql.py`](../DATALAN/DATALAN/test_iteration2_postgresql.py). |
| Tipos y fechas | Comercial | La lógica distingue el tipo eventual y valida fecha o rango. | `eventual`, `installation_date`, `eventual_start_date`, `eventual_end_date`. | [`views.py`, `installation_schedule()`](../DATALAN/DATALAN/views.py#L1696); [`test_iteration2_postgresql.py`](../DATALAN/DATALAN/test_iteration2_postgresql.py). |
| Cálculo de prioridad | Comercial / flujo de solicitud | Se deriva de la fecha de instalación o del inicio eventual: alta hasta 3 días, media hasta 7 y baja después. Es una regla implementada en la aplicación, no una política ITIL prescrita. | Etiqueta de prioridad y fechas usadas en el cálculo. | [`views.py`, `installation_priority()`](../DATALAN/DATALAN/views.py#L1689); prueba `test_installation_schedule_derives_priority_from_installation_date` en [`test_optimization_service.py`](../DATALAN/DATALAN/test_optimization_service.py). |
| Evaluación de factibilidad | Encargado de Planta Técnica | El flujo contiene pantallas/acciones de evaluación y decisión de Planta Técnica. | Evaluación, factibilidad, observaciones y estado de la solicitud. | [`views.py`, `workflow()` y ramas de evaluación/decisión](../DATALAN/DATALAN/views.py#L3845); rutas [`urls.py`](../DATALAN/DATALAN/urls.py#L36). |
| Revisión de Sistemas | Encargado de Sistemas | Hay acciones/pantallas para revisión, registro y decisión de Sistemas antes del flujo de aprobación o asignación según el caso. | Revisión/evaluación, resultado, observaciones y estado. | [`views.py`](../DATALAN/DATALAN/views.py#L3845); rutas [`urls.py`](../DATALAN/DATALAN/urls.py#L54). |
| Decisión comercial | Comercial | El flujo admite decisión de aprobación o rechazo y conserva razón/historial. Una solicitud rechazada no debe avanzar a ejecución. | `commercial_status`, estado, explicación y eventos de historial. | [`views.py`](../DATALAN/DATALAN/views.py#L3845); [`test_iteration2_postgresql.py`](../DATALAN/DATALAN/test_iteration2_postgresql.py), pruebas de decisión comercial documentadas en [`resultados_p2_2026-10-31.md`](./pruebas_iteracion_2/resultados_p2_2026-10-31.md). |
| Asignación y coordinación | Soporte / Encargado de Sistemas / Planta Técnica | El flujo contempla asignación de personal de Soporte y responsables técnicos; las vistas verifican rol, etapa y estado antes de aceptar acciones. | `support_assignee`, responsable técnico, asignación y equipo propuesto. | [`views.py`, `handle_operational_stage_post()`](../DATALAN/DATALAN/views.py#L2099); [`views.py`, `generate_operational_team_proposals()`](../DATALAN/DATALAN/views.py#L3165). |
| Propuesta de equipo | Soporte / Encargado de Sistemas | La ruta de propuesta exige sesión/rol, relación del usuario con la solicitud, etapa válida y cronograma tentativo; guarda la propuesta. No equivale por sí sola a confirmar la asignación. | Etapa, miembros recomendados, puntuaciones, firma del cronograma y resultado del algoritmo. | [`views.py`, `generate_operational_team_proposals()`](../DATALAN/DATALAN/views.py#L3165); [`optimization_service.py`, `run_genetic_team_optimization()`](../DATALAN/DATALAN/optimization_service.py#L582); integración de propuesta/confirmación en [`test_technician_capabilities.py`](../DATALAN/DATALAN/test_technician_capabilities.py). |
| Cronograma | Técnico / Soporte / Sistemas según la etapa | Se envían propuestas de fechas/horas y se validan fechas, límites y estado; el cronograma aprobado se conserva separado del tentativo. | Puntos/fechas tentativas y aprobadas, descripción, responsable, estado de etapa. | [`views.py`, `handle_operational_stage_post()`](../DATALAN/DATALAN/views.py#L2099); prueba `test_installation_schedule_submission_approval_and_reload` en [`test_iteration2_postgresql.py`](../DATALAN/DATALAN/test_iteration2_postgresql.py). |
| Inspección, instalación y retiro eventual | Técnico / Planta / Soporte | Las etapas registran programación, aprobación, ejecución y resultados. El retiro sólo corresponde a solicitudes eventuales. | Estado por etapa, puntos, equipo, resultado y fechas. | [`views.py`, `handle_operational_stage_post()`](../DATALAN/DATALAN/views.py#L2099); prueba `test_eventual_service_stays_open_until_removal_and_final_review` en [`test_iteration2_postgresql.py`](../DATALAN/DATALAN/test_iteration2_postgresql.py). |
| Revisión y conclusión | Técnico / Soporte / Comercial según el caso | Enviar una conclusión no equivale a aprobarla. La revisión de Soporte puede aprobarla o devolverla; la aprobación cambia el estado de finalización. | Resultado, nota, usuario y fecha de revisión, `concluded_at` y estado final. | [`views.py`, `handle_operational_stage_post()`](../DATALAN/DATALAN/views.py#L2099); resultados P2-13 y P2-17 en [`resultados_p2_2026-10-31.md`](./pruebas_iteracion_2/resultados_p2_2026-10-31.md). |
| Consulta e historial | Roles con acceso al caso | Hay pantallas por rol, actualización de partes del flujo e historial de eventos. | Estado visible, eventos, área, usuario, fecha, acción y nota. | [`views.py`, `workflow_updates()`](../DATALAN/DATALAN/views.py#L1941); [`workflow_service.py`, `add_history()`](../DATALAN/DATALAN/workflow_service.py#L291); rutas en [`urls.py`](../DATALAN/DATALAN/urls.py#L20). |

### Evaluación frente a las cinco fases definidas para DATALAN

| Fase propuesta para DATALAN | Correspondencia encontrada | Matiz necesario |
|---|---|---|
| 1. Recepción y registro | Registro comercial, datos de solicitud, CITE e historial. | No confundir un formulario con el alcance completo de Service Request Management. |
| 2. Evaluación y decisión | Evaluaciones de Planta Técnica y Sistemas y decisión comercial. | Las áreas y secuencias son propias de DATALAN; no son fases oficiales obligatorias de ITIL 4. |
| 3. Asignación y coordinación | Asignación de Soporte/técnicos, propuestas de equipos y aprobación de horarios. | La recomendación algorítmica y la aprobación humana son acciones distintas. |
| 4. Ejecución y seguimiento | Inspección, instalación, retiro eventual, resultados e historial. | Las etapas dependen del tipo de solicitud; no toda solicitud recorre exactamente las mismas. |
| 5. Revisión y conclusión | Envío/revisión de conclusión y persistencia del resultado final. | La aprobación y cierre dependen de reglas de DATALAN y de quién tiene autorización. |

Las cinco fases son una **descomposición del proceso de negocio de DATALAN** para el análisis y la tesis. No deben presentarse como cinco fases oficiales de ITIL 4.

## D. Correspondencia de Incident Management

### Flujo respaldado por el código

El flujo observado es:

**reporte → validación del enlace → asignación → propuesta/aprobación de horario → atención técnica → registro de intento de solución → conclusión enviada → revisión de Soporte/Sistemas → cierre o devolución.**

La incidencia se crea asociada a una solicitud de servicio y el código exige que el servicio PP/MP esté instalado y su conclusión aprobada para permitir el reporte. El sistema registra descripción inicial y estados. Las pruebas de Iteración 3 puntualizan que no hay un campo estructurado de “diagnóstico” independiente; por ello, no se debe afirmar que existe tal entidad o dato si la tesis lo describe de esa manera.

| Actividad | Responsable(s) | Comportamiento que se observa | Datos y estados relevantes | Evidencia y pruebas |
|---|---|---|---|---|
| Registro del reporte | Soporte / Encargado de Sistemas | `submit_service_incident` valida pantalla/rol, enlace completado, descripción no vacía y límite de longitud; crea incidencia con identificador y estado inicial. | CITE padre, `incident_id`, descripción, reportante/rol, fecha, estado e historial. | [`views.py`, `workflow()`/`submit_service_incident`](../DATALAN/DATALAN/views.py#L3968); prueba `test_report_is_linked_to_active_service_and_reloads_without_diagnosis` en [`test_iteration3_postgresql.py`](../DATALAN/DATALAN/test_iteration3_postgresql.py). |
| Comprobación inicial | Soporte / Sistemas | `is_completed_active_point_link()` determina si el enlace puede recibir el reporte. No es diagnóstico automático de red. | Tipo de enlace, instalación completada, conclusión aprobada y estado final. | [`views.py`, `is_completed_active_point_link()`](../DATALAN/DATALAN/views.py#L942); rama de reporte en [`views.py`](../DATALAN/DATALAN/views.py#L3968). |
| Asignación inicial | Encargado de Planta Técnica | Comprueba rol, estado de la incidencia y disponibilidad del técnico antes de asignarlo. | `plant_technician_assignee`, estado `ASIGNADA`, evento de historial. | [`views.py`, `handle_service_incident_workflow_post()`](../DATALAN/DATALAN/views.py#L1200); pruebas P3-04/P3-05 descritas en [`resultados_p3_2026-10-31.md`](./pruebas_iteracion_3/resultados_p3_2026-10-31.md). |
| Coordinación de horario | Técnico asignado y persona reportante autorizada | El técnico propone fecha/hora y descripción; el reportante Soporte o Sistemas autorizado aprueba. | `attention`, horario propuesto/aprobado, estado de incidencia e historial. | [`views.py`, `handle_service_incident_workflow_post()`](../DATALAN/DATALAN/views.py#L1200); prueba de integración `test_p4_11_and_p4_12_incident_proposal_and_attention_confirmation_persist` en [`test_iteration4_functional_integration.py`](../DATALAN/DATALAN/test_iteration4_functional_integration.py). |
| Atención | Técnico asignado | Sólo el técnico asignado puede iniciar y registrar el resultado de atención; se exige aprobación previa del horario. | Inicio real, actor, resultado y estado `ATENCIÓN: COMPLETADA`. | [`views.py`, acciones `start_incident_attention` y `complete_incident_stage`](../DATALAN/DATALAN/views.py#L1200); prueba `test_attention_activity_and_result_are_persisted_for_incident` en [`test_iteration3_postgresql.py`](../DATALAN/DATALAN/test_iteration3_postgresql.py). |
| Diagnóstico/solución | Técnico asignado | Registra resultado, clasifica intento como `SOLUCIONADA` o `PERSISTE`; si persiste, guarda el intento y la incidencia queda pendiente de solución. | Lista `attempts`, resultado, clasificación y fechas/usuario de intento. | [`views.py`, rama `complete_incident_stage`](../DATALAN/DATALAN/views.py#L1200); prueba `test_persistent_solution_attempt_is_saved_and_does_not_close_incident` en [`test_iteration3_postgresql.py`](../DATALAN/DATALAN/test_iteration3_postgresql.py). |
| Envío de conclusión | Técnico asignado | Sólo permite enviar conclusión si la solución está marcada como resuelta; enviar no cierra por sí mismo. | `conclusion.status = ENVIADA`, resultado, usuario y hora. | [`views.py`, acción `submit_incident_conclusion`](../DATALAN/DATALAN/views.py#L1200); `test_confirmed_solution_waits_for_support_review_before_closure` en [`test_iteration3_postgresql.py`](../DATALAN/DATALAN/test_iteration3_postgresql.py). |
| Verificación y cierre | Reportante Soporte o Sistemas autorizado | Puede aprobar o devolver la conclusión. Para cerrar exige solución confirmada; se guarda `CERRADA` y la fecha de conclusión. | Decisión, nota, revisador, fecha y estado final. | [`views.py`, acción `review_incident_conclusion`](../DATALAN/DATALAN/views.py#L1200); prueba `test_support_verification_closes_and_preserves_incident_history` en [`test_iteration3_postgresql.py`](../DATALAN/DATALAN/test_iteration3_postgresql.py). |
| Historial | Soporte / Sistemas / Planta / Técnico según permisos | Las incidencias se presentan asociadas al caso padre y los eventos se agregan al historial del caso. | Reporte, etapas, intentos, notas, actores y estados. | [`views.py`, `flatten_service_incidents()` y `workflow_updates()`](../DATALAN/DATALAN/views.py#L1045); [`workflow_service.py`, `add_history()`](../DATALAN/DATALAN/workflow_service.py#L291). |

### Evaluación frente a las cinco fases definidas para DATALAN

| Fase propuesta para DATALAN | Correspondencia encontrada | Diferencia o límite |
|---|---|---|
| 1. Recepción y registro | Reporte con descripción, identificador y vínculo a un servicio que cumple las condiciones definidas. | La validación confirma elegibilidad del enlace; no detecta automáticamente fallas de fibra. |
| 2. Comprobaciones iniciales | Se verifica instalación/conclusión y se valida la descripción. | No se encontró una batería automática de pruebas remotas del enlace. |
| 3. Asignación y coordinación | Se designa técnico, propone horario y se aprueba antes de iniciar la atención. | La asignación inicial y la propuesta de equipo optimizada son mecanismos distintos. |
| 4. Diagnóstico y atención | El técnico registra actividad/resultado, y uno o varios intentos de solución. | No existe un campo independiente de causa raíz/diagnóstico; el resultado técnico se registra en etapas/intent. |
| 5. Verificación y cierre | El técnico envía conclusión y un actor autorizado la revisa; si se aprueba se cierra, si se observa retorna a corrección. | La “verificación” se representa por la revisión de conclusión de DATALAN; no es una entidad separada. |

Estas etapas son el modelo de análisis del proyecto, no una secuencia oficial o universal de ITIL 4. La principal diferencia entre la fase descrita y la transición implementada es que **registrar una solución técnica no cierra la incidencia**: hace falta enviar la conclusión y que Soporte/Sistemas la revise. Si la falla persiste, el intento queda conservado y el caso no se cierra.

## E. Otras prácticas y conceptos relacionados

### Service Level Management

El repositorio contiene [sla_service.py](../DATALAN/DATALAN/sla_service.py#L1), que define fases y metas internas por defecto, puede guardar objetivos configurables e historial de cambios, y calcula resultados relacionados con los tiempos. La ruta de configuración es `/sistemas/registro/sla/` y se restringe al Encargado de Sistemas ([urls.py](../DATALAN/DATALAN/urls.py), [views.py, `handle_sla_post()`](../DATALAN/DATALAN/views.py#L1663)).

Esto permite describir una **función de seguimiento de metas internas de tiempo**. No permite afirmar que existen SLA acordados con clientes, que haya cumplimiento contractual, o que la práctica de Service Level Management esté implantada de extremo a extremo. Para este estudio se declara expresamente que **no existen SLA formales definidos**. Los valores predeterminados en código son parámetros internos, no compromisos vigentes.

### Service Desk

Soporte y Sistemas cuentan con vistas y acciones para recibir y tramitar reportes. Esto es compatible con algunas funciones de punto de contacto. No basta para declarar una práctica completa de Service Desk: no se halló evidencia que permita demostrar organización, catálogo, operación integral y medición formal de una mesa de servicio.

### Problem Management

Los intentos, resultados y notas de una incidencia ayudan a conservar antecedentes. No se identificó una entidad de problema independiente, registro de error conocido, análisis causal sistemático ni proceso de eliminación de causa raíz. Por tanto, conviene decir que DATALAN **registra resultados de incidentes**, no que implementa Problem Management.

### Monitoring and Event Management

Las páginas consultan casos y estados; la aplicación también puede actualizar partes de la pantalla. No se encontró evidencia de telemetría de enlaces, sondas, ingestión de eventos de red o alertamiento automático. La visibilidad de un estado creado por usuarios no equivale a monitorización y gestión de eventos.

### Measurement and Reporting

Existen registros y vistas de datos operativos, así como datos de ejecución de algoritmos. Sin una definición y gobierno completo de indicadores, generación sistemática, revisión y decisiones demostradas, debe tratarse como funcionalidad parcial de reporte, no como prueba de adopción completa de la práctica.

### Continual Improvement

Las pruebas, ajustes y mejoras técnicas del software apoyan el desarrollo. No se halló un ciclo institucional documentado que registre oportunidades, priorice, implemente y evalúe mejoras de servicios de forma continua. No confundir iteraciones de desarrollo o ajuste de algoritmos con la práctica completa.

### Service Configuration Management

Se persisten datos de solicitudes, configuración, perfiles y capacidades. No se halló un inventario de elementos de configuración del servicio con relaciones, ciclo de vida y control equivalentes a una CMDB. No declarar esta práctica a partir de la sola presencia de configuraciones en PostgreSQL.

## F. Algoritmos genéticos y NSGA-II

Los cuatro modos indicados en el alcance son componentes de optimización. Son herramientas para apoyar decisiones de asignación, no prácticas de ITIL 4.

| Modalidad | Función y entrada principal | Propósito operativo | Qué no implica |
|---|---|---|---|
| AG general de solicitudes | `run_genetic_optimization()` evalúa solicitudes elegibles y técnicos. | Proponer una distribución de asignaciones según las reglas implementadas y la información disponible. | No aprueba solicitudes ni confirma por sí solo asignaciones operativas. |
| AG/propuestas de equipos por etapa | `run_genetic_team_optimization()` considera una etapa y un horario tentativo; usa perfiles, capacidades, disponibilidad, ausencias, carga y distancia. Se integra por `generate_operational_team_proposals()`. | Recomendar equipos para inspección, instalación o retiro eventual. | La propuesta guardada sigue siendo propuesta; Soporte/Sistemas debe confirmar el horario/equipo en el flujo de aplicación. |
| NSGA-II general de incidencias | `run_incident_nsga2()` procesa incidencias abiertas y técnicos elegibles. | Generar alternativas que equilibran espera ponderada por urgencia y desequilibrio de carga. | No detecta fallas de red ni resuelve la incidencia automáticamente. |
| NSGA-II de equipo para una incidencia con horario definido | `run_incident_team_nsga2()` evalúa equipos compatibles en el horario y calcula alternativas con más de un objetivo. | Recomendar equipo de atención factible para el horario planteado. | No sustituye la aprobación de Soporte/Sistemas ni el registro posterior del trabajo. |

### Recomendación frente a asignación confirmada

1. **Generar recomendación:** el servicio algorítmico devuelve una o más alternativas; las vistas pueden guardar el resultado/propuesta y mostrarlo.
2. **Seleccionar y aprobar:** la persona autorizada selecciona una alternativa y el flujo verifica rol, estado, vigencia de la propuesta y coherencia del horario.
3. **Persistir la asignación:** la aplicación registra equipo/responsable, aprobación, cambios de estado e historial.

Por tanto, el texto académico debe usar verbos como “recomienda”, “propone” o “apoya la selección” al describir el algoritmo; reservar “asigna” o “confirma” para la acción de la vista que aplica la decisión autorizada.

Evidencia principal: [`optimization_service.py`](../DATALAN/DATALAN/optimization_service.py#L582) (equipo genético), [`optimization_service.py`](../DATALAN/DATALAN/optimization_service.py#L1456) (NSGA-II general), [`optimization_service.py`](../DATALAN/DATALAN/optimization_service.py#L1684) (NSGA-II por equipo/horario), y [`views.py`](../DATALAN/DATALAN/views.py#L3165) / [`views.py`](../DATALAN/DATALAN/views.py#L3317) (integración de propuestas).

## G. Matriz de evidencias para la defensa

Las historias HU y códigos P2/P3/P4 son los identificadores tal como aparecen en la documentación de iteraciones del repositorio. Deben contrastarse con el documento oficial de requisitos de tesis: no se halló en el repositorio un catálogo completo y autorizado de todas las historias originales.

| Práctica/tema | HU o iteración documentada | Archivo y función | Evidencia de datos/estado | Prueba localizada | Pantalla/ruta que conviene mostrar |
|---|---|---|---|---|---|
| Roles y acceso | HU-01 / Iteración 1 | [`auth_service.py`, `ROLES`/`authenticate()`](../DATALAN/DATALAN/auth_service.py#L1); [`views.py`, `workflow()`](../DATALAN/DATALAN/views.py#L3845); [`urls.py`](../DATALAN/DATALAN/urls.py#L1) | Rol de sesión, módulos habilitados y acceso a rutas. | [`test_admin_accounts.py`](../DATALAN/DATALAN/test_admin_accounts.py), pruebas de permisos en [`test_optimization_service.py`](../DATALAN/DATALAN/test_optimization_service.py). | Inicio de sesión y navegación autorizada de cada rol. |
| Registro de solicitud | HU-02 / Iteración 2, P2-01/P2-02 | [`views.py`, `workflow()`](../DATALAN/DATALAN/views.py#L3845); [`workflow_service.py`, `save_requests()`](../DATALAN/DATALAN/workflow_service.py#L119) | CITE, datos de cliente, tipo, prioridad, fechas e historial persistidos. | `test_permanent_and_eventual_registration_persist_and_reload`; informe de pruebas [`resultados_p2_2026-10-31.md`](./pruebas_iteracion_2/resultados_p2_2026-10-31.md). | Comercial → nueva solicitud permanente y eventual. |
| Factibilidad y decisiones por área | HU-03/HU-04 / Iteración 2 | [`views.py`, `workflow()` y etapas de evaluación](../DATALAN/DATALAN/views.py#L2371) | Evaluaciones/observaciones, resultado y transición de estado. | Pruebas P2-06/P2-07 descritas en [`resultados_p2_2026-10-31.md`](./pruebas_iteracion_2/resultados_p2_2026-10-31.md). | Solicitudes de Planta Técnica, Sistemas y Comercial. |
| Propuesta de equipo y confirmación de etapa | HU-05 a HU-10 / Iteración 4 | [`views.py`, `generate_operational_team_proposals()`](../DATALAN/DATALAN/views.py#L3165); [`optimization_service.py`, `run_genetic_team_optimization()`](../DATALAN/DATALAN/optimization_service.py#L582) | Propuesta, miembros/fitness y firma de horario; luego equipo y cronograma aprobados. | [`test_technician_capabilities.py`](../DATALAN/DATALAN/test_technician_capabilities.py), [`test_iteration4_functional_integration.py`](../DATALAN/DATALAN/test_iteration4_functional_integration.py). | Solicitud asignada → generar propuesta → seleccionar y aprobar horario. |
| Retiro eventual y conclusión | HU-08 / Iteración 2, P2-15 a P2-17 | [`views.py`, `handle_operational_stage_post()`](../DATALAN/DATALAN/views.py#L2099) | Rango eventual, retiro, resultado y conclusión final. | `test_eventual_service_stays_open_until_removal_and_final_review`; salida registrada en [`resultados_p2_2026-10-31.md`](./pruebas_iteracion_2/resultados_p2_2026-10-31.md). | Mostrar un eventual instalado, retiro pendiente y conclusión después del retiro. |
| Reporte de incidencia vinculado a enlace | HU-11 / Iteración 3, P3-01/P3-02 | [`views.py`, reporte en `workflow()`](../DATALAN/DATALAN/views.py#L3968); `is_completed_active_point_link()` | CITE del servicio, descripción, reportante, fecha y estado inicial. | `test_report_is_linked_to_active_service_and_reloads_without_diagnosis`; [`resultados_p3_2026-10-31.md`](./pruebas_iteracion_3/resultados_p3_2026-10-31.md). | `/sistemas/incidencias/` o `/sistemas/soporte/incidencias/`. |
| Asignación y atención de incidencia | HU-12 / Iteración 3, P3-04/P3-08/P3-09 | [`views.py`, `handle_service_incident_workflow_post()`](../DATALAN/DATALAN/views.py#L1200) | Técnico, horario aprobado, inicio real, actividad, resultado e intentos. | [`test_iteration3_postgresql.py`](../DATALAN/DATALAN/test_iteration3_postgresql.py). | Soporte reporta; Planta asigna; Técnico registra atención y resultado. |
| Persistencia de incidencia abierta | HU-12 / Iteración 3, P3-11 | [`views.py`, rama `resolution_status == 'PERSISTE'`](../DATALAN/DATALAN/views.py#L1300) | Intento guardado; estado pendiente; no se cierra. | `test_persistent_solution_attempt_is_saved_and_does_not_close_incident`. | Mostrar intento persistente y estado abierto. |
| Verificación/cierre por Soporte | HU-12 / Iteración 3, P3-10/P3-13 | [`views.py`, `review_incident_conclusion`](../DATALAN/DATALAN/views.py#L1300) | Revisor, nota, decisión, fecha de cierre y estado `CERRADA`. | `test_support_verification_closes_and_preserves_incident_history`. | Enviar conclusión por Técnico y revisar/aprobar desde Soporte. |
| Algoritmos de incidencias | HU-13/HU-14 / Iteración 4 | [`optimization_service.py`, `run_incident_nsga2()`](../DATALAN/DATALAN/optimization_service.py#L1456); `run_incident_team_nsga2()` | Alternativas, objetivos, cargas y miembros propuestos. | Pruebas de NSGA-II y las evidencias de Iteración 4 en [`REPORTE_PRUEBAS_ITERACION_4.md`](../DATALAN/documentacion/iteracion_4/evaluacion/REPORTE_PRUEBAS_ITERACION_4.md). | Optimización de incidencias y registro de propuestas. |
| Metas internas de tiempo | Función relacionada, no práctica formal | [`sla_service.py`](../DATALAN/DATALAN/sla_service.py#L1); [`views.py`, `handle_sla_post()`](../DATALAN/DATALAN/views.py#L1663) | Metas parametrizadas e historial de modificaciones. | [`test_sla_service.py`](../DATALAN/DATALAN/test_sla_service.py). | `/sistemas/registro/sla/`, aclarando que son parámetros internos, no SLA contractuales. |

### Evidencias visuales que se recomienda preparar

La interfaz debe mostrarse con datos de prueba o datos que se autorice exponer. Las siguientes son **capturas recomendadas para la defensa**, no se afirma que todas existan ya:

1. Comercial: registro de solicitud con los datos obligatorios y una eventual con fechas DE/HASTA.
2. Planta Técnica y Sistemas: evaluación y observación; Comercial: decisión final.
3. Técnico: cronograma tentativo; Soporte: aprobación; resultado de etapa y conclusión revisada.
4. Incidencia: reporte ligado al CITE de un enlace activo, estado inicial e identidad/rol del reportante.
5. Incidencia: técnico asignado, horario tentativo/aprobado, resultado técnico `PERSISTE` y estado aún abierto.
6. Incidencia: solución confirmada, conclusión enviada y revisión/cierre autorizado.
7. Optimización: parámetros y alternativas recomendadas, seguidos de la pantalla que muestra la selección/aprobación humana.
8. Registro de pruebas: salida de las ejecuciones focalizadas reproducibles, junto con fecha, settings de pruebas, nombre de la base temporal y código de salida.

El repositorio sí contiene algunas capturas de escenarios de prueba bajo [`resultados_tesis_3_4/capturas/`](../resultados_tesis_3_4/capturas/), por ejemplo `formulario_solicitud_prueba.png` y `selector_incidencia_pp_mp.png`. Antes de presentarlas, comprobar que correspondan a la versión vigente y rotularlas como evidencia de prueba, no como una captura de producción.

## H. Redacción académica sugerida

Los siguientes textos son propuestas. Deben adecuarse a la estructura, objetivos y resultados medidos de la tesis.

### Capítulo I: delimitación temática y alcance de ITIL 4

> El presente proyecto toma como referencia selectiva prácticas de ITIL 4 relacionadas con el objetivo del sistema: la gestión de solicitudes operativas de servicios de fibra óptica y la atención de incidencias asociadas a enlaces activos. El alcance se limita a la incorporación parcial y adaptada de Service Request Management e Incident Management en los flujos implementados por DATALAN. El proyecto no implementa ni declara conformidad integral con ITIL 4, sus 34 prácticas, ni una certificación. Las etapas descritas responden al proceso definido para el caso de estudio.

### Capítulo II: definición de las prácticas seleccionadas

> Service Request Management se utiliza como referencia para analizar el registro, evaluación, decisión, coordinación, ejecución y conclusión de solicitudes operativas. Incident Management se utiliza para analizar el reporte de fallas de un servicio instalado, la asignación y atención técnica, el registro de intentos de solución y la revisión del cierre. La relación con DATALAN se establece por correspondencia funcional verificable; no se afirma que el sistema replique la totalidad de las recomendaciones, roles o mecanismos organizacionales de las prácticas oficiales.

### Capítulo III: relación con Iteraciones 2 y 3

> La Iteración 2 materializa el flujo de solicitudes operativas mediante formularios, estados, evaluación de áreas, decisiones, programación y conclusión, con diferencias de recorrido para solicitudes permanentes y eventuales. La Iteración 3 materializa el registro y seguimiento de incidencias de servicios habilitados, incluida la asignación técnica, coordinación de la atención, persistencia de intentos no resueltos y revisión antes del cierre. Estas iteraciones representan el diseño de procesos de DATALAN y se relacionan de manera parcial con Service Request Management e Incident Management, respectivamente; no son fases oficiales de ITIL 4.

### Apartado 3.4: resultados de la incorporación de prácticas ITIL 4

> La revisión del código y de las pruebas focalizadas permite identificar dos prácticas seleccionadas: Service Request Management e Incident Management. En solicitudes se observaron estados, validaciones, evaluaciones por área, asignaciones, cronogramas e historial. En incidencias se observaron el vínculo con servicios elegibles, la asignación, el registro de actividades e intentos de solución, la conservación de casos no resueltos y la revisión previa al cierre. La incorporación es parcial y adaptada al contexto de DATALAN. Los algoritmos genéticos y NSGA-II se consideran herramientas de apoyo a la asignación, no prácticas ITIL 4. No se atribuyen SLA contractuales ni adopción integral de otras prácticas.

### Capítulo IV: resultados e interpretación

> Los resultados muestran que DATALAN proporciona soporte funcional para tramitar solicitudes de fibra óptica y atender incidencias vinculadas a enlaces instalados. La aplicación conserva estados e historial y valida acciones según rol y etapa. Para las incidencias, un intento marcado como persistente permanece abierto y la conclusión técnica requiere revisión autorizada antes del cierre. Los algoritmos generan propuestas que requieren selección y confirmación en el flujo operativo. La interpretación se limita a la funcionalidad observada y a las pruebas registradas: no equivale a demostrar operación productiva, cumplimiento contractual de niveles de servicio ni adopción integral de ITIL 4.

## I. Respuesta para el tribunal

### Versión oral aproximada de un minuto

> “El proyecto selecciona dos prácticas de ITIL 4: Service Request Management e Incident Management, en forma parcial y adaptada al caso DATALAN. Las seleccioné porque el sistema se centra en tramitar solicitudes operativas de fibra óptica y atender incidencias de enlaces activos. La aplicación permite registrar y evaluar solicitudes, tomar decisiones por rol, coordinar cronogramas, registrar la ejecución y revisar la conclusión. Para incidencias, permite reportar el problema asociado a un servicio, asignar un técnico, coordinar la atención, registrar intentos de solución y mantener abierto el caso si la falla persiste; el cierre requiere revisión autorizada. Estas funciones se sustentan en las vistas, servicios de persistencia y pruebas focalizadas del repositorio. Los algoritmos genéticos y NSGA-II solo recomiendan alternativas y no son prácticas ITIL. No afirmamos implementar las 34 prácticas ni tener SLA contractuales o certificación.”

### Versión de aproximadamente 20 segundos

> “DATALAN incorpora parcialmente y de forma adaptada Service Request Management e Incident Management: gestiona solicitudes de fibra y atiende incidencias vinculadas a enlaces activos. Lo demostramos con flujos por rol, estados, historial y pruebas focalizadas. Los algoritmos apoyan decisiones; no son prácticas ITIL ni confirman asignaciones por sí solos.”

## J. Conclusión y correcciones recomendadas para la tesis

### Conclusión de auditoría

La evidencia revisada permite declarar **dos prácticas seleccionadas e incorporadas parcialmente/adaptadas**:

1. Service Request Management.
2. Incident Management.

“Parcial/adaptada” es la formulación prudente: existe funcionalidad concreta de aplicación y resultados previos de pruebas focalizadas, pero no se evaluó la operación organizacional integral, la instalación de producción, la totalidad de criterios de ITIL, ni una certificación. No se recomienda afirmar que alguna práctica está implantada integralmente.

### Contradicciones o exageraciones que conviene corregir

1. **Alcance del marco:** reemplazar afirmaciones que impliquen adopción de las 34 prácticas por la selección explícita de dos prácticas.
2. **Fases:** rotular las cinco fases de solicitudes e incidencias como fases adaptadas de DATALAN, no como fases oficiales obligatorias de ITIL 4.
3. **SLA:** describir las metas de `sla_service.py` como configuración/medición interna. No afirmar SLA vigentes, cumplimiento contractual o compromisos con clientes.
4. **Algoritmos:** distinguir generación de alternativas, selección autorizada y persistencia de la asignación. No atribuir a AG/NSGA-II aprobación automática ni condición de práctica ITIL.
5. **Diagnóstico y Problem Management:** distinguir los resultados e intentos técnicos almacenados del diagnóstico estructurado o de una gestión de problemas/cause-root que no se encontró implementada.
6. **Service Desk y monitorización:** no equiparar pantallas de Soporte ni consulta de estados con una práctica completa de Service Desk o Monitoring and Event Management.
7. **Datos de incidencias:** aclarar que los reportes y etapas se guardan asociados a la solicitud, en sus datos JSONB/historial, según el flujo revisado; las pruebas de Iteración 3 indican que no hay campos independientes de diagnóstico.
8. **Pruebas:** separar resultados históricos de pruebas y ejecución actual. Los reportes fechados 31-10-2026 registran 16 pruebas P2 y 9 pruebas P3 satisfactorias; en la auditoría del 12-11-2026 la suite completa no llegó a correr debido a una base de pruebas PostgreSQL preexistente. No atribuir a esta auditoría un resultado completo de suite.
9. **Evidencia visual:** indicar si cada captura es de prueba o de producción y verificar que corresponda a la versión actual. No presentar capturas recomendadas como si ya hubieran sido tomadas.
10. **Trazabilidad:** los códigos HU/P2/P3/P4 citados provienen de documentación del repositorio; cotejarlos con el catálogo oficial de requisitos de la tesis antes de usarlos como identificadores definitivos.

### Referencias técnicas principales

- [Rutas y pantallas Django](../DATALAN/DATALAN/urls.py)
- [Flujos, permisos y acciones](../DATALAN/DATALAN/views.py)
- [Persistencia de solicitudes e historial](../DATALAN/DATALAN/workflow_service.py)
- [Roles y autenticación](../DATALAN/DATALAN/auth_service.py)
- [Algoritmos y perfiles técnicos](../DATALAN/DATALAN/optimization_service.py)
- [Metas internas de tiempo](../DATALAN/DATALAN/sla_service.py)
- [Pruebas de solicitudes — Iteración 2](../DATALAN/DATALAN/test_iteration2_postgresql.py)
- [Pruebas de incidencias — Iteración 3](../DATALAN/DATALAN/test_iteration3_postgresql.py)
- [Integración de optimización — Iteración 4](../DATALAN/DATALAN/test_iteration4_functional_integration.py)
- [Resultados documentados P2](./pruebas_iteracion_2/resultados_p2_2026-10-31.md)
- [Resultados documentados P3](./pruebas_iteracion_3/resultados_p3_2026-10-31.md)

## K. Las 34 prácticas ITIL 4 y oportunidades para ampliar DATALAN

Esta matriz distingue **lo encontrado actualmente** de **lo que podría desarrollarse**. “Potencial” no significa que la práctica ya esté implementada ni que baste con agregar una pantalla. Para declararla incorporada habría que implementar el flujo necesario, definir responsables y reglas, conservar los datos, probarlo y limitar la afirmación al alcance realmente demostrado.

Los nombres se agrupan en las tres familias de ITIL 4: prácticas de gestión general, prácticas de gestión de servicios y prácticas de gestión técnica.

| # | Familia | Práctica ITIL 4 | Situación observada en DATALAN | Potencial y mejora necesaria |
|---:|---|---|---|---|
| 1 | Gestión general | **Architecture Management** — Gestión de arquitectura | **No encontrada.** La arquitectura Django/PostgreSQL del sistema no equivale a una práctica de gestión de arquitectura. | **Bajo/condicionado.** Sería pertinente si el alcance creciera a gobernar arquitectura de servicios, aplicaciones e infraestructura, con principios, decisiones, responsables y revisiones. No parece prioritaria para la tesis actual. |
| 2 | Gestión general | **Continual Improvement** — Mejora continua | **Relacionada, no establecida.** Hay iteraciones de desarrollo, ajustes y pruebas, pero no se identificó un registro formal de oportunidades y beneficios. | **Alto.** Añadir registro de oportunidades, indicador base, responsable, acción, plazo, resultado y revisión periódica; aplicar un ciclo de mejora documentado. Esto permitiría fundamentar una práctica adicional si se ejecuta y evalúa, no solo si se crea el formulario. |
| 3 | Gestión general | **Information Security Management** — Gestión de seguridad de la información | **No demostrada como práctica.** Hay autenticación y controles de acceso por rol; eso es evidencia de funciones de seguridad, no de un sistema integral de gestión de seguridad. | **Medio, condicionado al alcance.** Se necesitarían políticas, clasificación/protección de datos, gestión de riesgos, registro y revisión de accesos, respuesta a incidentes de seguridad y pruebas. Evitar declararla solo por tener login y roles. |
| 4 | Gestión general | **Knowledge Management** — Gestión del conocimiento | **No encontrada como base de conocimiento.** El sistema conserva historial, reportes y resultados técnicos, pero no se encontró un repositorio editorial de soluciones reutilizables. | **Alto.** Incorporar artículos de conocimiento vinculados a fallas y servicios, búsqueda, autor/revisor, estado de vigencia y relación con incidentes. La información histórica actual podría ser fuente, pero no es por sí sola conocimiento gestionado. |
| 5 | Gestión general | **Measurement and Reporting** — Medición y generación de informes | **Parcial/relacionada.** Existen reportes, historial, estados y métricas de los algoritmos; no se demostró gobierno integral de indicadores de servicio. | **Alto.** Definir KPI con fórmula, fuente, periodo, responsable, umbral y revisión; por ejemplo tiempo de atención, incidentes reabiertos, solicitudes por etapa y antigüedad de casos. No reportar cifras sin validar su cálculo y calidad. |
| 6 | Gestión general | **Organizational Change Management** — Gestión del cambio organizacional | **No encontrada.** Los cambios de estados en solicitudes no son la gestión organizacional de cambios culturales, estructurales o de adopción. | **Bajo/condicionado.** Podría apoyar un programa de adopción con comunicación, formación, impacto, participación y evaluación. Parte importante es organizacional y no se resuelve únicamente con software. |
| 7 | Gestión general | **Portfolio Management** — Gestión de portafolio | **No encontrada.** Los listados de solicitudes no constituyen un portafolio de productos/servicios o inversiones. | **Bajo.** Solo sería pertinente si DATALAN incorporara priorización de iniciativas/servicios, valor, costos, riesgos, dependencias y decisiones de inversión. |
| 8 | Gestión general | **Project Management** — Gestión de proyectos | **No encontrada como función del sistema.** Las iteraciones del propio desarrollo no muestran que DATALAN gestione proyectos de la organización. | **Bajo.** Se podría ampliar a proyectos de despliegue de fibra con alcance, hitos, recursos, riesgos, costos y avance, pero sería otro dominio funcional. |
| 9 | Gestión general | **Relationship Management** — Gestión de relaciones | **Parcialmente relacionada.** Solicitudes conservan cliente/solicitante y existen vistas de clientes; no se encontró una gestión completa de relaciones y expectativas. | **Medio.** Añadir interesados y contactos, compromisos, comunicaciones, retroalimentación/satisfacción y seguimiento de acuerdos. No presentarla como implementada por almacenar el nombre del cliente. |
| 10 | Gestión general | **Risk Management** — Gestión de riesgos | **No encontrada como proceso.** Validaciones de fechas o disponibilidad son reglas operativas, no un registro integral de riesgos. | **Medio.** Podría agregarse registro de riesgo asociado a servicio/solicitud, probabilidad, impacto, mitigación, responsable, vencimiento y seguimiento. |
| 11 | Gestión general | **Service Financial Management** — Gestión financiera de servicios | **No encontrada.** No se identificó manejo de presupuesto, costo del servicio, facturación o análisis financiero. | **Bajo.** Posible si el alcance incluye costos de instalación/mantenimiento, presupuesto, consumo de recursos y costos por servicio. Requiere datos y reglas financieras confiables. |
| 12 | Gestión general | **Strategy Management** — Gestión de estrategia | **No encontrada.** El sistema operativo no documenta una estrategia de servicios o de TI. | **Bajo.** Normalmente requiere gobierno, objetivos estratégicos, análisis y decisiones institucionales; no es una ampliación inmediata del flujo de tickets. |
| 13 | Gestión general | **Supplier Management** — Gestión de proveedores | **No encontrada.** No se halló gestión de contratos, proveedores, desempeño o dependencias de terceros. | **Bajo/condicionado.** Puede ser útil si instalación o soporte dependen de proveedores; requeriría registro de proveedores, servicios/contratos, contactos, renovaciones, riesgos y evaluación de desempeño. |
| 14 | Gestión general | **Workforce and Talent Management** — Gestión de fuerza laboral y talento | **Parcialmente relacionada.** DATALAN mantiene técnicos, perfiles, capacidades, horarios, ausencias y carga; no se identificó ciclo de talento, formación y desarrollo. | **Medio/alto.** Extender perfiles con competencias evaluadas y vigentes, formación, certificaciones, necesidades de capacitación y planificación de capacidad. La asignación actual por sí sola no acredita la práctica completa. |
| 15 | Gestión de servicios | **Availability Management** — Gestión de disponibilidad | **No encontrada como medición de disponibilidad.** Se registran incidencias, pero no se observaron cálculo de disponibilidad, ventanas de servicio ni tiempos de indisponibilidad verificados. | **Alto si se dispone de datos confiables.** Registrar inicio/fin de interrupción, servicio/enlace afectado, ventana acordada y fórmula; mostrar disponibilidad por periodo. Mantener claro que no hay SLA formales vigentes salvo que se acuerden posteriormente. |
| 16 | Gestión de servicios | **Business Analysis** — Análisis de negocio | **Parcialmente relacionada.** Las solicitudes guardan requisitos y datos del solicitante; no se identificó trazabilidad estructurada de necesidades, reglas de aceptación y cambios de requisito. | **Medio.** Añadir levantamiento/versionado de requisitos, criterios de aceptación, interesados, reglas de negocio y vínculo entre necesidad y entrega. Adecuado si la tesis quiere evaluar el ciclo de solicitud como requerimiento de servicio. |
| 17 | Gestión de servicios | **Capacity and Performance Management** — Gestión de capacidad y rendimiento | **Parcialmente relacionada solo con carga de trabajo de técnicos.** El algoritmo distribuye trabajo; no se halló medición del rendimiento/capacidad de la red de fibra. | **Alto para una ampliación técnica.** Incorporar capacidad del enlace/puerto, uso, umbrales, crecimiento y rendimiento medido, vinculados a servicio y eventos. No confundir balance de técnicos con capacidad de red. |
| 18 | Gestión de servicios | **Change Enablement** — Habilitación del cambio | **No encontrada como control de cambios del servicio.** Aprobar un cronograma de solicitud no equivale necesariamente a evaluar cambios sobre servicios/infraestructura en operación. | **Alto si la operación incluye cambios de red.** Crear solicitud de cambio con motivo, elementos afectados, riesgo/impacto, autorización, ventana, plan de reversión, ejecución y revisión posterior. Delimitarla a cambios de configuración/red. |
| 19 | Gestión de servicios | **Incident Management** — Gestión de incidentes | **Implementada parcialmente/adaptada.** Hay reporte relacionado con enlace elegible, asignación, atención, intentos de solución, conclusión y cierre revisado. | **Ya es candidata principal.** Fortalecer categorización, impacto/urgencia consistentes, comunicación, reapertura, prioridades, métricas y revisión del proceso si se desea una mayor correspondencia. |
| 20 | Gestión de servicios | **IT Asset Management** — Gestión de activos de TI | **No encontrada como ciclo de vida de activos.** Los datos de equipamiento de una solicitud no demuestran inventario, custodia, estado y ciclo de vida de activos. | **Alto para fibra/equipos.** Añadir inventario de ONT, routers, puertos, equipos y materiales con identificador, ubicación, propietario/custodio, estado, instalación/retiro, garantía y vínculo a servicio/orden. |
| 21 | Gestión de servicios | **Monitoring and Event Management** — Monitorización y gestión de eventos | **No encontrada como monitorización de infraestructura.** Hay consulta/actualización de estados de casos, no evidencia de eventos automáticos de red. | **Alto, requiere integración técnica.** Integrar una fuente autorizada de telemetría/alertas; normalizar evento, recurso, fecha, severidad y correlación; separar evento informativo de incidente y registrar respuesta. |
| 22 | Gestión de servicios | **Problem Management** — Gestión de problemas | **No encontrada.** Diagnósticos/resultados puntuales de incidentes no conforman un proceso de causa raíz, problemas y errores conocidos. | **Alto.** Crear problemas vinculables a varios incidentes, causa conocida/hipótesis, análisis, workaround, error conocido, responsable y acciones preventivas; medir recurrencia. |
| 23 | Gestión de servicios | **Release Management** — Gestión de liberaciones | **No encontrada.** El historial de solicitudes no gestiona liberaciones de servicios o cambios agrupados. | **Bajo/condicionado.** Sería útil para agrupar cambios planificados de servicios/red, ventanas de liberación, aprobaciones, comunicación, verificación y revisión posterior. |
| 24 | Gestión de servicios | **Service Catalogue Management** — Gestión del catálogo de servicios | **Parcialmente relacionado.** Hay tipos de solicitud y formularios, pero no se demostró un catálogo gobernado de ofertas con descripción, elegibilidad, responsable y condiciones. | **Alto y cercano al alcance.** Formalizar tipos de servicio, descripción, opciones, requisitos previos, elegibilidad, aprobadores, entrega y condiciones; usar el catálogo como fuente de formularios. |
| 25 | Gestión de servicios | **Service Configuration Management** — Gestión de configuración del servicio | **No encontrada como CMDB.** PostgreSQL almacena solicitudes y datos JSONB; no se observó un registro gobernado de elementos de configuración y sus relaciones. | **Alto para trazabilidad de fibra.** Crear inventario de elementos de configuración (enlace, nodo, puerto, equipo, ubicación) y relaciones entre ellos; versionar cambios y enlazar solicitudes/incidentes a los elementos afectados. |
| 26 | Gestión de servicios | **Service Continuity Management** — Gestión de continuidad del servicio | **No encontrada.** La permanencia de registros de incidentes no equivale a continuidad/recuperación del servicio. | **Medio/condicionado.** Documentar escenarios, servicios críticos, objetivos de recuperación acordados, responsables, procedimientos de contingencia y pruebas periódicas. No inventar objetivos RTO/RPO sin decisión institucional. |
| 27 | Gestión de servicios | **Service Design** — Diseño del servicio | **No encontrada como ciclo de diseño.** Los formularios de instalación capturan solicitudes, no un proceso completo de diseño del servicio. | **Medio.** Puede incorporar ficha de diseño de servicio, requisitos técnicos, capacidad, seguridad, disponibilidad, soporte y criterios de aceptación antes de habilitar una oferta. |
| 28 | Gestión de servicios | **Service Desk** — Mesa de servicio | **Parcialmente relacionada.** Soporte y Sistemas tienen pantallas de atención y tramitación, pero no se demostró una práctica completa de mesa de servicio. | **Muy alto y cercano al flujo actual.** Consolidar un punto de contacto, clasificación, prioridad, asignación/cola, comunicación al solicitante, escalamiento, conocimiento y medición de atención. |
| 29 | Gestión de servicios | **Service Level Management** — Gestión de niveles de servicio | **Parcialmente relacionada; sin SLA formal para este estudio.** Hay metas internas configurables, pero no se deben presentar como compromisos contractuales. | **Alto, condicionado a acuerdo formal.** Definir catálogo/servicio y partes, objetivos medibles, periodos/horarios, exclusiones, fuente de medición, reportes y revisión. Solo después de que la organización los apruebe sería válido hablar de gestión de niveles de servicio acordados. |
| 30 | Gestión de servicios | **Service Request Management** — Gestión de solicitudes de servicio | **Implementada parcialmente/adaptada.** El flujo de solicitud contiene registro, evaluación, decisión, coordinación, ejecución y conclusión. | **Ya es candidata principal.** Mejorar catálogo, estados/criterios trazables, comunicación al solicitante, excepciones, métricas y pruebas por cada recorrido permanente/eventual. |
| 31 | Gestión de servicios | **Service Validation and Testing** — Validación y pruebas del servicio | **Parcialmente relacionada.** Hay validaciones de formulario y pruebas automatizadas de código/flujo; no se encontró una práctica de aceptación del servicio entregado con criterios sistemáticos. | **Medio/alto.** Definir listas de pruebas de aceptación de enlaces (resultado, evidencia, responsable, fecha, resultado esperado/obtenido) y relacionarlas con instalación, cambio y cierre. No confundir pruebas de software con pruebas de validación del servicio de fibra. |
| 32 | Gestión técnica | **Deployment Management** — Gestión del despliegue | **No encontrada como proceso de despliegue de software/infraestructura.** La existencia de Django/PostgreSQL no demuestra operación de despliegues. | **Bajo para el objetivo actual.** Relevante si DATALAN también gestionará despliegues de aplicaciones o de componentes de infraestructura; requeriría versiones, ambientes, plan, autorización, verificación y reversión. |
| 33 | Gestión técnica | **Infrastructure and Platform Management** — Gestión de infraestructura y plataformas | **No encontrada como capacidad de administración de infraestructura.** La aplicación corre sobre plataforma, pero no gestiona esa plataforma. | **Bajo/condicionado.** Podría ampliarse a inventario y monitoreo de plataformas, dependencias, capacidad y mantenimiento; probablemente corresponde a herramientas operativas de infraestructura, no al núcleo de solicitudes de fibra. |
| 34 | Gestión técnica | **Software Development and Management** — Desarrollo y gestión de software | **No encontrada como práctica gestionada por DATALAN.** El repositorio demuestra que DATALAN está construido como software y tiene pruebas; no que el producto gestione el ciclo de desarrollo de software. | **Bajo para el alcance de tesis.** Solo sería pertinente si se añadiera gestión de productos/versiones, backlog, defectos, releases y ciclo de vida de software. El propio desarrollo del proyecto no cuenta como función implementada por el sistema. |

### Oportunidades futuras más defendibles

Si el objetivo es ampliar las prácticas relacionadas sin desviar el tema central, recomiendo priorizar:

1. **Service Desk:** es la extensión más próxima a las pantallas actuales de Soporte. Consolidar recepción, clasificación, comunicación, escalamiento y seguimiento.
2. **Service Catalogue Management:** formalizar las ofertas/tipos ya usados en formularios y sus requisitos/condiciones de atención.
3. **Knowledge Management:** convertir soluciones validadas en conocimiento reutilizable y enlazarlas con casos.
4. **Problem Management:** identificar recurrencias entre incidentes y gestionar causa/acciones preventivas.
5. **Measurement and Reporting + Continual Improvement:** definir indicadores verificables y un ciclo de acciones basado en resultados; no solo gráficos o ajustes del algoritmo.
6. **IT Asset Management + Service Configuration Management:** inventariar equipos/elementos de red y sus relaciones con enlaces, solicitudes e incidencias. Son dos prácticas diferentes, aunque puedan compartir datos.
7. **Monitoring and Event Management:** candidata útil para el dominio de fibra, pero requiere una fuente real de monitoreo/telemetría e integración técnica. No se logra solo consultando los estados ingresados por usuarios.
8. **Service Level Management / Availability Management:** podrían ser posteriores, una vez acordados formalmente servicios, horarios y objetivos medibles. Hasta entonces, no llamar SLA a metas internas ni afirmar disponibilidad contractual.
9. **Change Enablement y Service Validation and Testing:** pertinentes si DATALAN comienza a gestionar cambios sobre enlaces activos y pruebas de aceptación verificables.

Estas son **opciones de evolución**, no prácticas adicionales incorporadas hoy. Para la tesis actual, una selección realista sería mantener las dos principales y describir una o dos oportunidades futuras como trabajo propuesto, en vez de inflar la cantidad de prácticas declaradas.

### Priorización sugerida para una evolución del producto

| Prioridad | Prácticas futuras | Primer incremento de software | Evidencia para poder declarar incorporación parcial |
|---|---|---|---|
| 1 — Próxima al flujo actual | Service Desk, Service Catalogue Management | Catálogo de solicitudes, clasificación y cola, trazabilidad de responsable y comunicación al solicitante. | Prueba del recorrido desde recepción hasta resolución/conclusión por rol, registro y métricas básicas. |
| 2 — Aprovecha los datos actuales | Knowledge Management, Problem Management | Artículos revisados y problemas vinculados a múltiples incidentes; clasificación y causa/acciones. | Prueba que demuestre búsqueda/reutilización de conocimiento y trazabilidad de incidentes recurrentes hacia un problema. |
| 3 — Gobierno y medición | Measurement and Reporting, Continual Improvement | Definiciones de KPI, periodos, responsables, registro de mejoras y revisión de resultados. | Cálculos reproducibles sobre datos válidos y evidencia de decisión/acción de mejora asociada a un resultado. |
| 4 — Dominio de red | IT Asset Management, Service Configuration Management, Monitoring and Event Management | Inventario de activos y relaciones; integración con eventos autorizados; correlación a enlace/servicio. | Casos de prueba de trazabilidad activo-servicio-incidente-evento y actualización controlada del inventario. |
| 5 — Formalización de servicio | Service Level Management, Availability Management | Definición acordada de horarios, objetivos, medición, exclusiones e informes de nivel/disponibilidad. | Aprobación documentada de objetivos y prueba de cálculo con datos observados; hasta entonces no afirmar SLA. |
| 6 — Cambios de red | Change Enablement, Service Validation and Testing | Flujo de solicitud de cambio, evaluación de riesgo, autorización, ejecución, reversión y checklist de aceptación. | Casos de prueba de aprobación, rechazo, ejecución, reversión y aceptación con responsables y evidencia. |

### Recomendación para la tesis

La respuesta más defendible hoy es: **dos prácticas ITIL 4 seleccionadas e incorporadas parcialmente/adaptadas**. En una sección de trabajo futuro se pueden mencionar las prácticas candidatas anteriores, especialmente Service Desk, Service Catalogue Management, Knowledge Management, Problem Management y Measurement and Reporting, condicionándolas a las funcionalidades que realmente se construyan y prueben.

No presentar “podría integrarse” como “ya está integrado”. Una práctica futura solo debe subir a la lista de incorporadas cuando existan, como mínimo, un proceso definido, responsables, datos persistidos, transiciones/controles, interfaz o mecanismo operativo, y pruebas/evidencia acordes con el alcance declarado.
