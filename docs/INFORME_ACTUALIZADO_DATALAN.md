# Informe actualizado de DATALAN

## 1. Identificación y alcance de la revisión

- Fecha de revisión: 23 de octubre de 2026.
- Versión / commit: el repositorio raíz está en `6c1252b`; el proyecto Django contenido en `DATALAN/` tiene HEAD `4b3dbbf` y el directorio está desalineado respecto a la rama `origin/master` con cambios locales sin confirmar. La comprobación se hizo con `git status --short` y `git rev-parse --short HEAD`.
- Cambios locales sin confirmar: sí existen. En la raíz del repositorio se detectan cambios en los archivos de documentación y un submódulo o proyecto anidado bajo `DATALAN/` con archivos no versionados; dentro de la app Django también hay varias modificaciones en `views.py`, `auth_service.py`, `workflow_service.py`, templates y estáticos. Se conservó la documentación histórica en `docs/INFORME_ITERACION_4_DATALAN.md` sin editarla.
- Carpetas y componentes revisados: `DATALAN/DATALAN/` (proyecto Django), `DATALAN/docs/` (documentación y esquemas), `DATALAN/requirements.txt`, `DATALAN/manage.py`, y las pruebas bajo `DATALAN/DATALAN/test_*.py`.
- Qué se comprobó leyendo código: rutas, roles, autorización, algoritmos genéticos, validaciones de cronogramas, persistencia en PostgreSQL y parser de perfiles técnicos; esto se verificó en `auth_service.py`, `optimization_service.py`, `views.py`, `urls.py`, y en los tests de Django.
- Qué se comprobó ejecutando pruebas: se ejecutó `cd c:\Users\Dxtr\Desktop\DATALAN\DATALAN; python manage.py test` (123 pruebas). Resultado actual: 123 ejecutadas, 1 fallo y 2 errores.
- Qué se comprobó mediante interfaz: no se ejecutó navegador real ni comprobación visual manual de la UI; la evidencia disponible es la renderización de templates y las pruebas de Django que validan respuesta HTTP y contenido HTML.
- Qué no se pudo verificar: despliegue real, autenticación con PostgreSQL en entorno productivo, concurrencia real, flujo de navegador end-to-end completo, y cualquier dato no presente en la base o en los archivos del repositorio.
- Distinción de estados: 
  - Implementado y conectado a una pantalla: mayoría de flujos de solicitudes, incidencias, perfiles y optimización para solicitudes/incidencias están conectados por rutas y vistas, por ejemplo en `urls.py` y `views.py`.
  - Implementado pero sin recorrido identificado desde la interfaz: algunas funciones internas del algoritmo y adaptadores de persistencia existen, pero no siempre tienen un botón visiblemente conectado al flujo principal.
  - Parcial o pendiente: validaciones de propuesta para jornada, conflicto de ocupación y algunos detalles de incidencias siguen siendo sospechosos o no están cubiertos por pruebas, como se refleja en los fallos actuales.
  - Comprobado mediante una prueba ejecutada: 123 pruebas en Django; 120 pasadas, 1 fallo y 2 errores.
  - Deducido del código, pero no probado: varios detalles de negocio en la lógica de optimización y de permisos no tienen evidencia en flujo de navegador ni en pruebas de integración reales.

## 2. Cambios respecto al informe anterior

El informe anterior (`docs/INFORME_ITERACION_4_DATALAN.md`) establece el estado de la iteración 4 y describe la optimización genérica y N-SGA-II. El código actual mantiene el enfoque general, pero presenta diferencias relevantes respecto a esa documentación histórica:

| Aspecto | Situación anterior | Funcionamiento actual | Evidencia | Efecto sobre el documento académico |
|---|---|---|---|---|
| Roles y acceso | Se describía un conjunto de roles y módulos para acceso. | El sistema sigue usando un mapeo de roles en `ROLES` y `login_view`, con verificación por sesión y módulos configurables. | [auth_service.py](../DATALAN/DATALAN/auth_service.py#L1-L95), [views.py](../DATALAN/DATALAN/views.py#L1717-L1758) | Se conserva la estructura académica del modelo de roles, pero debe mencionarse que la protección es por sesión y no por un backend de permisos independiente. |
| Optimización de solicitudes | Había una optimización global y propuestas por etapa. | Sigue existiendo, con funciones `run_genetic_optimization` y `run_genetic_team_optimization`, pero la validación de cronograma y los criterios de disponibilidad son más estrictos. | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L256-L718) | La descripción debe decir que es una optimización de asignación y no una aprobación automática del negocio. |
| Incidencias | Se describían NSGA-II globales y equipo para atención. | Sigue vigente; el algoritmo divide la población, evalúa dominancia y crowding distance, y produce hasta 3 alternativas. | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1323-L1587) | Debe conservarse la diferencia entre optimización general y generación de alternativas para un caso concreto. |
| Perfil técnico | Se mencionan capacidades y horarios. | Los perfiles se normalizan con validaciones de días laborables, horas, ausencias y capacidades, además de considerar apoyo. | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L728-L918) | Es importante expresar que el perfil técnico es un dato de operación y que no es una simple lista de competencias, sino un conjunto estructurado. |
| Validación de fechas | Se documentó la necesidad de fechas válidas en cronogramas. | La lógica conserva la validación de fecha/hora, el tope comercial y el control de plazo del técnico. | [views.py](../DATALAN/DATALAN/views.py#L2119-L2200), [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L256-L370) | Debe señalarse como restricción técnica y operativa, no como un dato académico opcional. |
| Estado actual de pruebas | El informe anterior indicaba avances en pruebas. | La suite actual ejecuta 123 pruebas, pero hay 1 fallo y 2 errores concretos. | Comando ejecutado: `python manage.py test` | Se debe reportar que la implementación no está plenamente estable en el estado actual. |

### Diferencias confirmadas

- Hay cuatro flujos de optimización conectados: solicitudes globales, propuestas por etapa, incidencias globales y equipo para incidencia con horario concreto.
- La generación de equipos usa un algoritmo basado en combinación, permutación y puntuación de habilidades, pero está acoplada a validaciones de horario y disponibilidad.
- Los perfiles de incidencia y los perfiles operativos son distintos y se normalizan por separado.
- Existen pruebas que cubren la lógica de horarios, capacidades, y propuestas, pero la suite actual no está completamente verde.
- Al revisar el código actual, la documentación debe distinguir entre “algoritmo ejecutado”, “resultado visualizado” y “decisión confirmada” porque no todo lo mostrado en UI corresponde a una acción persistente.

## 3. Usuarios, permisos y perfiles técnicos

### Inicio de sesión común

La autenticación se realiza en `authenticate()` de [auth_service.py](../DATALAN/DATALAN/auth_service.py#L23-L117). Acepta usuario/contraseña y, si el usuario existe en la base de datos, valida `password_hash` y actualiza `last_login_at`. La sesión guarda `identity` y `role` en `login_view()` de [views.py](../DATALAN/DATALAN/views.py#L1717-L1758). En modo demo, también existen usuarios predefinidos `DEMO_USERS` en [auth_service.py](../DATALAN/DATALAN/auth_service.py#L31-L55), pero la verificación real se hace contra la tabla `datalan.usuarios` cuando existe la base persistente.

### Roles y páginas

Los roles se definen en `ROLES` en [auth_service.py](../DATALAN/DATALAN/auth_service.py#L1-L30) y las rutas se exponen en [urls.py](../DATALAN/DATALAN/urls.py#L1-L120). Los permisos se revisan en `workflow()` y `screen_modules` en [views.py](../DATALAN/DATALAN/views.py#L2371-L2450), así como en `enabled_modules_for_role`/`get_role_module_access` de [views.py](../DATALAN/DATALAN/views.py#L181-L240). En términos prácticos:

- Comercial: registro, solicitudes, decisiones comerciales, enlaces y aprobación/rechazo; juega el papel de origen de la solicitud y del cierre comercial.
- Sistemas: revisión de solicitudes, registro técnico, optimización de solicitudes, pantalla de incidencias, soporte y coordinación de propuestas.
- Planta Técnica: gestión de técnicos, evaluación técnica, adopción de decisiones y seguimiento de trabajos.
- Soporte: gestión de incidencias reportadas, asignación a incidencias y confirmación/seguimiento de cronogramas.
- Técnico: ve sus trabajos, permisos y asistencia, y entrega inspección o resultados según el estado del trabajo.

### Permisos en servidor

Sí, los permisos se comprueban también en el servidor. El caso más claro es `generate_operational_team_proposals()` en [views.py](../DATALAN/DATALAN/views.py#L2119-L2200): valida rol (`soporte_sistemas` o `sistemas_encargado`), asignación del usuario a la solicitud, etapa y estado del equipo; además rechaza fechas fuera del rango o defectos en la firma de tiempo. También `login_view()` y `workflow()` validan acceso por sesión. Lo que no aparece es una capa de autorización centralizada tipo RBAC con políticas externas; se realiza a nivel de vistas y consultas.

### ¿Sistemas puede actuar como Soporte?

Sí, en ciertos casos. La lógica de `generate_service_incident_team_proposals()` permite que `sistemas_encargado` actúe si la incidencia fue reportada por Soporte y el rol del usuario que la reconfigura lo permite; la validación está en [views.py](../DATALAN/DATALAN/views.py#L2200-L2340). Además, la función de asignación y aprobación de cronogramas distingue el papel del usuario. No obstante, el flujo visible en la interfaz todavía depende del rol y de los módulos activos; la lógica de acceso no es perfectamente simétrica en todos los templates.

### Datos de Planta Técnica en TÉCNICOS y TÉCNICOS INCIDENCIAS

Se trata de dos perfiles relacionados pero distintos:

- Perfil operativo general: validado por `normalize_operational_profile()` en [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L728-L918). Contiene experiencia, dirección de equipos, días laborables, horario, ausencias y capacidades por etapa (`inspection`, `installation`, `removal`).
- Perfil específico de incidencias: norma y valida capacidades de diagnóstico, OTDR, empalmes, fusión, reparación y registro, a través de `normalize_incident_profile()` y funciones asociadas en [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L900-L1211).

La separación es clara: capacidades generales para solicitudes y capacidades de incidencias para servicio. Se comparten algunas capacidades concretas, como `use_otdr` y `perform_fusions`, pero cada perfil conserva su propio JSON y validación.

### Datos compartidos e independientes

- Compartidos: nombre del técnico, estado operativo, experiencia, liderazgo, horario básico y ausencias de trabajo general.
- Independientes: capacidades de incidencia y capacidades técnicas para solicitud; se gestionan desde pantallas distintas en Planta Técnica: la pantalla general y la de incidencias (`plant_technicians` frente a `plant_incident_technicians`).
- Experiencia, liderazgo, capacidades, horarios y ausencias: se editan por perfil y luego se consumen por `normalize_operational_profile()` antes de evaluar equipos. La comprobación de que la información mostrada en fichas coincide con la usada por algoritmos es positiva en la parte de lectura y normalización; no existe un log de auditoría separado de aquello que se visualiza actualmente.
- Origen de la carga mostrada: la carga activa se calcula con ` _active_workload_counts()` en [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L491-L518); para incidencias, la carga se determina por `base_workloads` y por asignaciones activas existentes en `run_incident_nsga2()`.
- Perfiles incompletos: si no hay datos evaluados, la lógica usa `default_operational_profile()` y el perfil se interpreta como `SIN_EVALUAR`; esto evita que el algoritmo asuma competencias no comprobadas. La función `_profile_has_no_evaluated_data()` existe para detectar este caso en [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L196-L240).

## 4. Flujo completo de solicitudes operativas

El flujo real que aparece en el código es: registro → evaluación → decisión comercial → asignaciones → inspección → instalación → conclusión → retiro eventual. El recorrido no es un único formulario; está fragmentado en vistas y estados del registro.

### Recorrido real

1. Registro y entrada de datos: `workflow()` y los formularios de comercial, con vistas de `new_request`, `forward_request`, etc.; la data se guarda por `save_requests()` en [workflow_service.py](../DATALAN/DATALAN/workflow_service.py#L119-L170).
2. Evaluación técnica: una solicitud revisada por Planta / Sistemas pasa por `plant_evaluate` y validaciones de factibilidad; la lógica es compleja y depende de la decisión de cada área; la evidencia va en [views.py](../DATALAN/DATALAN/views.py#L2371-L2753).
3. Decisión comercial: se usa `commercial_status` y el estado `APROBADO`/`RECHAZADO`. La candidata del algoritmo global exige `status == 'APROBADA'` y `commercial_status == 'APROBADO'`, además de ausencia de `assignment` en [views.py](../DATALAN/DATALAN/views.py#L2062-L2072).
4. Asignaciones: la generación de propuestas por etapa se hace desde `generate_operational_team_proposals()`; guarda la propuesta, pero no confirma a nadie ni modifica estado. [views.py](../DATALAN/DATALAN/views.py#L2119-L2200)
5. Inspección, instalación y retiro: cada etapa recibe un `status` y un `points` con cronograma tentativo. La aprobación final exige coincidir con la propuesta seleccionada y la misma fecha/hora. La validación se implementa en `_approved_team_for_schedule()` y en las gestiones de `handle_operational_stage_post()` en [views.py](../DATALAN/DATALAN/views.py#L1433-L1690).
6. Conclusión: la etapa se marca `APROBADA` y se conserva el cronograma definitivo y el equipo asignado.
7. Retiro eventual: la lógica exige que la solicitud sea `eventual` y que la etapa corresponda a `removal`; si no, se rechaza la propuesta. [views.py](../DATALAN/DATALAN/views.py#L2127-L2145).

### Aclaraciones operativas importantes

- Quién designa al responsable técnico: la lógica usa los campos `plant_technician_assignee` y `assignment` según el contexto operativo; no hay evidencia de un único punto central de decisión fuera del sistema. Se debe diferenciar entre “responsable técnico asignado al trabajo” y “coordinador de soporte”.
- Quién asigna al coordinador de Soporte: la evidencia actual apunta a que la rotación se hace al asignar a `support_assignee`/`support_secondary_assignee` en la solicitud. La asignación se usa para autorizar la generación de propuestas de equipo [views.py](../DATALAN/DATALAN/views.py#L2119-L2175).
- Comercial resuelve rechazo: el flujo persiste la solicitud rechazada y conserva el antecedente, pero el rechazo no elimina la información histórica; se guarda en `history` y el estado comercial que se lee desde la pantalla.
- Puntos de multipunto: el sistema representa los puntos como `points` y los valida por fecha/hora por punto en `_proposal_schedule_points()` y `generate_operational_team_proposals()`. Los puntos se guardan dentro de cada etapa y se convierten en puntos de inspección/instalación/retiro.
- Cálculo de prioridad: la prioridad se deriva de la fecha de instalación o de la fecha de inicio eventual; todo ello se calcula en `installation_priority()`, y se actualiza en `workflow()` con `priority_date`. [views.py](../DATALAN/DATALAN/views.py#L2371-L2425).
- Corrección de conclusiones observadas: el código permite reabrir o corregir un cronograma en la etapa de soporte bajo validaciones de fechas y se comparte la edición del cronograma tentativo. No hay una “revisión por otros actores” completamente independiente; se gestiona en la vista y en `save_requests()`.
- Cuándo queda activo el enlace: el sistema exige que la instalación y la conclusión de servicio estén aprobadas antes de reportar incidencias de servicio y, además, el cliente afectado debe estar disponible según el estado del servicio. Se valida en `is_completed_active_point_link()` y `submit_service_incident` de [views.py](../DATALAN/DATALAN/views.py#L2450-L2548).
- Conclusión de servicio permanente y eventual: la lógica distingue escenarios por `eventual` y por `installation_date`/`eventual_end_date`; la decisión final no se automatiza en un único punto, por lo que el informe académico debe hablar de “flujos con estados y cronogramas aprobables”, no de una finalización uniforme sin contexto.

## 5. Flujo completo de incidencias

El flujo de incidencias sigue la secuencia: reporte → comprobaciones iniciales → responsable → cronograma → propuesta de equipo → confirmación → diagnóstico y solución → verificación con el cliente → cierre.

- Reporte: se crea un `service_incidents` en la solicitud o bien se reporta directamente desde el flujo de incidencias con `submit_service_incident` y `handle_service_incident_workflow_post()` en [views.py](../DATALAN/DATALAN/views.py#L728-L1289).
- Comprobaciones iniciales: existe una validación explícita de que la instalación está concluida y el enlace es activo; si no, el sistema rechaza el reporte. Se ve en `submit_service_incident`, con mensajes como “Solo puedes reportar incidencias…”. [views.py](../DATALAN/DATALAN/views.py#L2450-L2548)
- Responsable: la lógica usa `incident_technician` o `plant_technician_assignee`, según el flujo. En las incidencias de servicio reportadas por Soporte, el equipo se asocia con N-SGA-II o con propuestas de equipo. [views.py](../DATALAN/DATALAN/views.py#L2200-L2340)
- Cronograma: la etapa `attention` puede tener `status='ENVIADA'` con `proposed_date` y `proposed_time` o un `schedule_signature` para un equipo. Existen validaciones de fecha/hora antes de generar la propuesta.
- Propuesta de equipo: la propuesta de equipo para una incidencia se genera con `generate_service_incident_team_proposals()` y se evalúa con `run_incident_team_nsga2()`. [views.py](../DATALAN/DATALAN/views.py#L2200-L2340), [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1645-L1805)
- Diagnóstico y solución: el cierre de servicio se hace con `incident_solution` / `solution` y `result`, según el flujo; el formulario permite ver resultados y cerrar la incidencia.
- Verificación con cliente y cierre: la vista y la lógica permiten confirmar solución y, si el cliente informa continuidad, el estado puede reabrirse o volver a evaluación. No se encontró un tratamiento automático de “cliente afirma que la falla continúa” distinto de volver al flujo de evaluación. La evidencia real está en la lógica de `workflow` y en los estados de un `service_incident` / `incident`.

### Aclaraciones puntuales

- Registro real de comprobaciones iniciales: sí existe, pero no como una tabla separada; está integrado en el campo `workflow` o en el texto del reporte y en las validaciones de `submit_service_incident`.
- Recorrido de solución remota sin visita: sí existe la posibilidad de que la incidencia se resuelva sin una visita física en el algoritmo y la UI, pero no está separado de la atención presencial con un registro de “solución remota” completamente independiente. La evidencia se ve en la lógica de `incident_attention` y `incident_solution`, no en una tabla única de solución remota.
- Prioridad y severidad: los valores se extraen de `severity`, `urgency` y `priority` y se convierten con `_incident_urgency_weight()` en [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1294-L1321). Si falta esa información, la lógica usa la antigüedad del reporte como valor fallback.
- Etapas separadas de atención y solución: sí existen. `attention` y `solution` están separados dentro del `workflow` de cada incidencia.
- Botones de optimización: el botón de optimización general de incidencias está en la pantalla de Sistemas, y el botón de propuesta de equipo para una incidencia con horario se usa desde la vista de soporte y del encargado de sistemas. En el código, ambos se diferencian claramente.
- Confirmación de cierre: la confirmación la hace quien tiene autoridad según el rol y el estado. El flujo de soporte/encargado lo gestiona en `handle_service_incident_workflow_post` y la vista de aprobación. [views.py](../DATALAN/DATALAN/views.py#L728-L1289)

## 6. Responsable del caso y líder del equipo

Se revisó por separado solicitudes e incidencias.

- Responsable inicial: se toma principalmente del `plant_technician_assignee` o del responsable asignado a la solicitud. En las incidencias se usa el `incident_technician` y el `responsible` o líder según el estado de la propuesta. La lógica no siempre tiene un único campo central; depende del flujo.
- Si se conserva tras generar y confirmar propuestas: en la generación y aprobación del equipo para etapas, el responsable del caso puede conservarse en el estado o ser reemplazado por el líder de la propuesta, según la pantalla y la etapa. El código actual evidencia que, al confirmar un equipo para una incidencia, el responsable técnico puede cambiar. Esta lógica está en `run_incident_team_nsga2()` y en la lógica de `handle_service_incident_workflow_post()`.
- Si el responsable debe integrar físicamente el equipo: el código no impone que el responsable tenga que formar parte del equipo, pero sí pueden aparecer como `leader` o `members` según la composición del equipo. La evaluación del peor/completo equipo toma cuenta del “leader” y la capacidad de liderazgo.
- Cuenta dentro de la cantidad de integrantes: sí, la cantidad de técnicos del equipo y el líder cuentan dentro del equipo. Se ve en `recommended_team_size` y `team_size` de `run_genetic_team_optimization()`: el algoritmo elige un tamaño determinado y después ordena a los miembros. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L519-L718)
- Cómo se elige al líder: se define por el perfil de liderazgo y experiencia del equipo, usando `_team_profile_components()` y la función de evaluación. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L405-L518)
- Si líder y responsable pueden ser distintos: sí, pueden ser distintos. El líder puede ser el técnico mejor evaluado del equipo y el responsable puede ser otra persona o seguir asignado al caso; el sistema guarda ambos datos, pero no siempre obliga a que coincidan.
- Qué campo cambia al aprobar: el campo más visible es `assigned_team`, `team_proposal_id` o la estructura de `genetic_team_proposals`, según la etapa. La confirmación del cronograma no siempre reemplaza el `plant_technician_assignee` salvo en incidencias específicas.
- Permisos del responsable anterior: cuando cambian las asignaciones, se conserva la trazabilidad del estado previo en `history`, pero no hay una “historial de permisos” estrictamente separada; la evidencia es por `history` y por la lógica de actualización del estado.
- Qué ocurre cuando no está disponible: la disponibilidad se valida revisando horario, días laborables, ausencias y ocupación en `_technician_is_available_for_points()`, `_scheduled_intervals()` y el criterio de `available`. Si no está disponible, no se incluye como candidato. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L310-L404)

## 7. Inventario de modalidades de optimización

Se comprobaron las cuatro modalidades que el proyecto menciona:

| Modalidad | Actor | Pantalla / botón | Ruta o vista | Función del algoritmo | Entradas | Resultados | Datos guardados | Efecto al confirmar |
|---|---|---|---|---|---|---|---|---|
| 1. Optimización general de solicitudes | Encargado de Sistemas | `sistemas/optimizacion/` > Ejecutar optimización | [views.py](../DATALAN/DATALAN/views.py#L2371-L2450), [urls.py](../DATALAN/DATALAN/urls.py#L84-L99) | `run_genetic_optimization()` | solicitudes aprobadas, comerciales y no asignadas | fitness, historial y hasta 3 órdenes | configuración en tabla `optimizacion_configuracion` | No confirma; sólo presenta alternativas |
| 2. Equipos para inspección/instalación/retiro | Soporte / Sistemas | Botón `GENERAR PROPUESTA` del trabajo | [views.py](../DATALAN/DATALAN/views.py#L2119-L2200) | `run_genetic_team_optimization()` | una solicitud, una etapa, puntos programados, perfiles y disponibilidad | hasta 3 equipos | `genetic_team_proposals` y `save_requests()` | requiere confirmación de cronograma y selecciona equipo |
| 3. Optimización general de incidencias | Encargado de Sistemas | `sistemas/incidencias/` > Optimización NSGA-II | [views.py](../DATALAN/DATALAN/views.py#L2371-L2450) | `run_incident_nsga2()` | incidencias abiertas, técnicos, carga y configuración NSGA-II | alternativas de asignación y carga proyectada | sólo presentación y configuración, no asignación real | no confirma ni guarda equipo |
| 4. Equipo para atención de incidencia con horario concreto | Soporte / Sistemas | botón de propuesta para una incidencia | [views.py](../DATALAN/DATALAN/views.py#L2200-L2340) | `run_incident_team_nsga2()` | incidencia, horario tentativo, otros incidentes y técnicos elegibles | hasta 3 equipos | `team_proposals` y validación de horario | confirma y guarda equipo y fecha/hora |

La diferencia clave es la de “recomendación general”, “propuesta guardada” y “asignación confirmada”. No todas las modalidades se materializan como una asignación ejecutada; algunas sólo muestran recomendaciones en pantalla y otras guardan una propuesta que luego el usuario debe confirmar.

## 8. Algoritmos genéticos de solicitudes

### 1. Optimización general de solicitudes

- Qué representa un gen: la posición de una solicitud dentro del plano de orden de trabajo y la asignación asociada. En la implementación, el cromosoma representa una permutación de solicitudes y luego se decodifica en un orden de ejecución. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L2056-L2341)
- Qué representa el cromosoma: una permutación total de una lista de solicitudes que cumplen los criterios de entrada.
- Se permutan: solicitudes, no técnicos; el algoritmo usa una estructura permutacional y luego toma el mejor conjunto de asignaciones.
- Población inicial: se basa en una solución de orden inicial y se completan con permutaciones aleatorias hasta llegar a `population_size`. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L2341-L2440)
- Formación del equipo: se forma a partir de la alternativa y las capacidades del equipo, mediante `_prepare_operational_team_candidates()` y la posterior evaluación de `run_genetic_optimization()`.
- Condiciones obligatorias y puntuación: la lógica combina penalizaciones por capacidad y por condiciones del equipo; no todas las restricciones son solo puntaje: el algoritmo exige que el equipo haga sentido para la etapa y que cumpla el perfil mínimo.
- Función de evaluación: `evaluate_candidate()` y la lógica de fitness combinan costo de orden y capacidades; la parte concreta está en `optimization_service.py` y se califica por orden y restricciones. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L2056-L2341)
- Fórmulas, pesos, unidades y normalización: hay pesos definidos en la semántica de `fitness` y en los componentes de equipo, pero no existe un documento normativo que explique por qué esos valores fueron elegidos. Se debe reportar como regla del código y no como una regla de negocio además de lo que aparece en la implementación.
- Selección, cruce y mutación: se usan orden crossover, mutación por intercambio y elitismo por ranking. El código tiene una comparación por fitness y por clave de equipo.
- Criterio de parada: cuando se alcanzan `generations` o cuando no hay más soluciones. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L2341-L2440)
- Evitar alternativas repetidas: se reutiliza una estructura de `archive` y se deduplican por clave de equipo/orden.
- “Hasta tres alternativas”: el sistema devuelve `[:3]` en la parte de ranking final. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L2390-L2440)

### 2. Equipos para inspección, instalación y retiro

- Gen: índice de técnico seleccionado en la población candidate.
- Cromosoma: una permutación de índices de técnicos elegibles para el equipo determinado.
- Diferencias por etapa: `inspection`, `installation` y `removal` usan grupos distintos de capacidades y tamaños recomendados por `activity_team_size()`.
- Cantidad de integrantes: la regla se fija por prioridad, distancia del enlace y etapa; la parte del algoritmo está en `run_genetic_team_optimization()` y usa `recommended_team_size`. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L519-L718)
- Si hay personal insuficiente: el algoritmo puede producir un “equipo pequeño” o una excepción con un mensaje de error. La lógica se implementa en `team_shortage` y en la rama combinatorial.
- Si existen ramas sin generaciones: sí, hay una rama `combinatorial_reference` cuando no se alcanza la cantidad recomendada de candidatos. Es decir, no siempre el algoritmo genera una población evolutiva; en algunos casos sólo evalúa combinaciones factibles.
- La fórmula visible coincide con la ejecutada: sí, en gran medida, porque las restricciones se reúnen en `score['fitness']` y `team_profile_score`. No se encontró un cálculo distinto oculto en otra capa.
- Rutas antiguas: se menciona la existencia de una API y de una ruta `generate_operational_team_proposals()`, pero no se encontró evidencia de rutas obsoletas que sigan activas; la implementación actual tiene rutas principales y no una segunda vía clara de “legacy”.

## 9. NSGA-II de incidencias

### Modo general de incidencias

- Representación de la alternativa: un vector de índices de técnicos para cada incidencia abierta.
- Objetivos: `weighted_wait_hours` (espera) y `load_imbalance` (carga de trabajo). La lógica se ve en `_incident_nondominated_fronts()` y en el cálculo de objetivos de la parte del algoritmo. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1323-L1547)
- Unidades: horas de espera y carga proyectada; “load_imbalance” es una medida de distribución de carga (no necesariamente horas de trabajo directas en sentido absoluto, sino un criterio de equilibrio).
- Restricciones: no se debe asignar a un técnico no elegible, la condición de trabajo debe ser compatible con cargas, días y horarios, y existen capacidades mínimas según el tipo de incidencia. La evidencia se centra en `incident_required_capabilities()` y `_incident_skill_value()`. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1212-L1294)
- Generación inicial: se construye una población de soluciones candidatas; se calcula la carga base y la elegibilidad del personal. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1405-L1530)
- Selección de padres: se hace por rank de nondominance y crowding distance. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1323-L1399)
- Cruce y mutación: se generan hijos combinando dos padres y mutando una posición escogida al azar.
- Clasificación por dominancia: se implementa en `_incident_nondominated_fronts()`. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1323-L1365)
- Medida de diversidad: `_incident_crowding_distance()` define la distancia de crowding. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1366-L1405)
- Reemplazo y finalización: se combina población con descendencia y se toma la mejor por front y diversidad. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1468-L1547)
- Selección de alternativas mostradas: el sistema toma hasta tres alternativas no repetidas de los front finales, ordenadas según objetivo de espera y distancia de crowding. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1547-L1587)

### Respuestas a preguntas clave

- Desde qué momento se calcula la espera: `current_time` se usa para calcular la demora y la prioridad del incidente. Si no se especifica, toma `datetime.now()` en `run_incident_nsga2()`. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1394-L1450)
- ¿Se considera duración de trabajos y secuencia de atención?: se considera la carga y el siguiente inicio disponible, pero no hay una secuencia de atención explícita como un cronograma completo; se prioriza la espera y el equilibrio de carga.
- ¿La carga representa cantidad de trabajos, horas u otra medida?: la carga se interpreta como “trabajo activo actualmente + incidencias propuestas”. Se refleja en el texto del algoritmo: `load_basis`: “Asignaciones de trabajo activas actuales más las incidencias propuestas.” [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1580-L1605)
- ¿Las incidencias ya asignadas se vuelven a evaluar?: sí, el algoritmo toma incidencias abiertas y, cuando corresponda, la carga actual del técnico se considera; no se documenta una duplicación por alta de un mismo trabajo, pero sí se incluyen las asignaciones activas en la carga.
- ¿Cómo se evita contar dos veces una misma actividad?: se usa una deduplicación por clave y se excluyen los casos con `incident_status` en `CERRADA` o `PENDIENTE DE VALIDACIÓN`. En la lógica de propuestas por equipo, también se tiene exclusión por `incident_id`.
- ¿Qué se optimiza cuando el horario está fijado?: en el caso de una incidencia concreta con horario, el algoritmo deja fijo el horario y optimiza el equipo compatible con ese horario y con la base de carga.
- ¿Todas las tarjetas corresponden al primer frente o incluyen otros?: se muestran alternativas de los frentes finales, no solo del primer frente. Se seleccionan hasta 3, priorizando el frente de menor espera y menor carga.
- ¿La carga interviene en más de un objetivo?: sí; la carga se usa para el segundo objetivo y en la construcción del diagnóstico del equipo. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1323-L1547)
- ¿Lo mostrado en pantalla coincide con cálculos?: en la parte visible del código, sí, porque la respuesta JSON y la pantalla consultan los mismos resultados de la función; no hay evidencia de una capa adicional que reinterpreta los valores.

## 10. Disponibilidad, capacidades y confirmación

Se verificó lo siguiente:

- Si se revisa solo el inicio o todo el intervalo del trabajo: la validación se realiza sobre cada punto del intervalo, no solo por el inicio; ` _technician_is_available_for_points()` usa `start` y `end` para comprobar disponibilidad. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L372-L404)
- Si se impide que el trabajo termine fuera de la jornada: sí, la lógica compara `start` y `end` con los horarios de trabajo y con las ausencias; si el intervalo excede la jornada o cae dentro de una ausencia, el técnico queda descartado. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L312-L404)
- Si solicitudes e incidencias comparten la revisión de ocupaciones: sí, comparten la idea de `occupied_intervals`, pero la implementación se realiza por cada caso y por cada algoritmo; no existe un único “scheduler central” del sistema. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L310-L404), [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1645-L1805)
- Si una propuesta pendiente ocupa un horario: sí, el sistema revisa ocupación de otros trabajos y bloquea horarios conflictivos. Esto se hace con `_scheduled_intervals()`.
- Si un cronograma tentativo se trata como una reserva: en la práctica sí, porque la propuesta se guarda y luego la confirmación exige una firma de horarios; no es un bloqueo absoluto de recurso, pero sí se usa como restricción temporal.
- Si se vuelve a comprobar disponibilidad y capacidades al confirmar: sí; el flujo de confirmación exige una propuesta existente con el mismo `date/time` y la misma composición; la validación se vuelve a ejecutar antes de aceptar la propuesta. [views.py](../DATALAN/DATALAN/views.py#L1537-L1690)
- Si dos usuarios pueden aprobar trabajos incompatibles para el mismo técnico: no hay evidencia de un bloqueo de concurrencia explícito al nivel de base de datos; la lógica de negocio no parece presentar una transacción de dos fases para confirmaciones simultáneas. Esto debe señalarse como una limitación y no como una garantía.
- Si existe protección de datos frente a confirmaciones simultáneas: no se encontró evidencia de locks transaccionales ni de bloqueo a nivel de rows para evitar doble confirmación. La lógica actual se apoya en validaciones de estado y en la sesión del usuario; no se documenta un mecanismo de concurrencia robusto.
- Qué ocurre si cambian perfiles, horarios o asignaciones después de generar una propuesta: la propuesta se compara con la firma del cronograma y la regla de disponibilidad; si cambia algo, no se acepta sin una nueva validación. No se encontró una regeneración automática.
- Cómo se interpretan “Sin evaluar”, “No realiza”, “Con apoyo” y “Sin apoyo”: estos valores se convierten con `_capability_value()` y se normalizan en `CAPABILITY_OPTIONS`; la semántica es clara, pero estos valores no están respaldados por una referencia documental externa. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L243-L249)
- Si “Con apoyo” exige un compañero capaz de realizar la actividad sin apoyo: la lógica puede aceptar “con apoyo” si la capacidad del técnico es compatible con apoyo, pero el sistema exige que al menos exista una composición de equipo que cumpla la etapa. No se encontró una regla de negocio adicional que obligue a un compañero “sin apoyo” en todos los casos.
- Qué sucede si faltan horarios o duración: la lógica lanza errores y bloquea la planificación. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L256-L294)
- Si se excluyen actividades de la misma solicitud al comprobar conflictos: sí, la función `_scheduled_intervals()` excluye la solicitud actual por `excluded_cite` y también sólo mira trabajos con estado `APROBADA`, `ASIGNADA`, `EN EJECUCIÓN`. Esto reduce la posibilidad de doble conteo dentro de la misma solicitud. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L310-L370)

## 11. Datos, parámetros y reglas fijas

| Dato o regla | Procedencia | Dónde se modifica | Modalidades que lo utilizan | Valor de respaldo | Justificación encontrada |
|---|---|---|---|---|---|
| Población | `DEFAULT_OPTIMIZATION_CONFIG` / `DEFAULT_INCIDENT_NSGA2_CONFIG` | `save_optimization_config()` y `save_incident_nsga2_config()` | solicitudes e incidencias | 40 para genético; 48 para NSGA-II | Se declara explícitamente en el código, pero no se documenta una justificación empresarial ajena al repositorio |
| Generaciones | mismo archivo | configuración persistida | solicitudes e incidencias | 100 / 80 | se observa en la implementación y en tests de validación |
| Cruce y mutación | setup de `DEFAULT_*_CONFIG` | configuración persistida | solicitudes e incidencias | 80% cruce / 10% mutación y 85% / 15% | regla del algoritmo, no un dato de negocio institucional |
| Pesos de puntuación | fórmula de fitness y evaluación por equipo | código del algoritmo | solicitudes y equipos | 1.0 / 0.3 / 0.0 según liderazgo | se deduce del cálculo; no hay documentación de negocio | 
| Experiencia | perfil técnico | `normalize_operational_profile()` | solicitudes, equipos e incidencias | 0 años/meses por defecto | la lógica usa la experiencia para desempatar y para evaluar equipos |
| Cantidad de integrantes | `activity_team_size()` / `recommended_team_size` | cálculo del equipo | inspección, instalación, retiro, incidencias | depende de prioridad y distancia | no existe una normativa documental que justifique un número fijo salvo el código |
| Prioridad y urgencia | `installation_priority()` y `_incident_urgency_weight()` | vista y lógica de incidencias | solicitudes e incidencias | media por defecto, fallback por antigüedad | se observa en la lógica, no en un documento normativo de la empresa |
| Duración estimada | `_stage_total_duration_hours()` | perfil o solicitud | equipos y cronogramas | 0.5h, 2h, 2h por etapa | valor por defecto en el código |
| Distancia del enlace | `distance_km` dentro de la evaluación del equipo | evaluación de solicitud | propuestas | 0 km por defecto | se valida como float y se usa para calcular equipo recomendado |
| Distancia de traslado | `travel_distance_km` en perfil técnico | perfil del usuario | propuestas | 0 km por defecto | se usa como componente del score |
| Capacidades requeridas | `CAPABILITY_GROUPS` y `incident_required_capabilities()` | perfiles y flujo de incidencias | propuestas y equipos | `SIN_EVALUAR` por defecto | es un dato evaluado y validado, no un dato de “negocio” externo |
| Carga de trabajo | `_active_workload_counts()` y base workloads | algoritmo de equipo e incidencias | propuestas y NSGA-II | 0 si no hay trabajos activos | se basa en trabajos activos y priorización |

Se distingue claramente entre datos introducidos por persona, datos calculados, valores predeterminados, estimaciones y reglas del código. Las “justificaciones” que aparecen en el documento final deben limitarse a lo que se ve en la implementación y no inventar un marco empresarial sin evidencia.

## 12. Pruebas y evidencia actualizada

### Pruebas ejecutadas

Comando ejecutado:

```bash
cd c:\Users\Dxtr\Desktop\DATALAN\DATALAN
python manage.py test
```

Entorno: Windows 11, Python 3.13.14, Django 6.1, PostgreSQL configurado por `settings.py` y datos persistentes (no se usó navegador real).

Resultado:

- Total ejecutadas: 123
- Aprobadas: 120
- Fallidas: 1
- Errores: 2
- Omitidas: 0

### Fallos actuales documentados

Los fallos descubiertos con `manage.py test` se corresponden con:

- `ERROR: test_eventual_inspection_deadline_uses_commercial_end_date`
- `ERROR: test_plant_technician_sends_tentative_inspection_details_to_assigned_support`
- `FAIL: test_systems_incidents_page_shows_interactive_support_reports`

Estos errores son relevantes porque cuestionan la estabilidad del flujo de fechas, la propuesta de apoyo técnico y la representación de incidencias reportadas por soporte en la pantalla de Sistemas. La comprobación confirma que el sistema no está 100% estable en esta revisión.

### Tipología de pruebas

- Pruebas del algoritmo: sí existen, principalmente en `test_optimization_service.py` y `test_technician_capabilities.py`.
- Pruebas de vista con `RequestFactory`: sí, se usan para comprobar roles, respuestas HTML y mensajes.
- Pruebas contra persistencia real: la configuración de base de datos usa PostgreSQL y se ejecuta a través de la capa de Django; sin embargo, no se realizaron pruebas con una base de prueba independiente y disponible para la comprobación final.
- Pruebas completas mediante navegador: no se ejecutaron.
- Pruebas de concurrencia: no se encontraron.

### Error previo relacionado con fecha inválida

Se insistió en comprobar si se corrigió el problema de “mensajes en una prueba de fecha inválida”. La evidencia actual muestra que la validación de fechas sigue activa: `generate_operational_team_proposals()` rechaza fechas no válidas y `handle_operational_stage_post()` invalida cronogramas fuera de rango. Por tanto, el control existe, pero la suite sigue mostrando errores relacionados con la ejecución de fechas y la UI de incidencias; no se puede afirmar que el problema fue resuelto al 100%. La correcta formulación es: “la validación existe y está presente en el código, pero al menos dos casos de la suite siguen fallando”.

## 13. Relación con las quince historias de usuario

Las historias de usuario que aparecen en la tarea se pueden relacionar con la implementación actual así:

| Historia | Funciones encontradas | Evidencia | Estado |
|---|---|---|---|
| HU-01 | autenticación, login, roles, módulos activos | [auth_service.py](../DATALAN/DATALAN/auth_service.py#L1-L95), [views.py](../DATALAN/DATALAN/views.py#L1717-L1758) | Implementado y conectado |
| HU-02 | registro y derivación de solicitudes | [views.py](../DATALAN/DATALAN/views.py#L2371-L2450), [workflow_service.py](../DATALAN/DATALAN/workflow_service.py#L119-L170) | Implementado |
| HU-03 | evaluación técnica y factibilidad | [views.py](../DATALAN/DATALAN/views.py#L2371-L2753) | Implementado parcialmente |
| HU-04 | evaluación de equipamiento y asignación de Soporte | [views.py](../DATALAN/DATALAN/views.py#L2119-L2200) | Implementado y conectado |
| HU-05 | designación del responsable técnico | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L519-L718), [views.py](../DATALAN/DATALAN/views.py#L1433-L1690) | Implementado parcialmente |
| HU-06 | gestión de perfiles y capacidades | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L728-L918) | Implementado |
| HU-07 | coordinación y aprobación de cronogramas | [views.py](../DATALAN/DATALAN/views.py#L1537-L1690) | Implementado |
| HU-08 | resultados de inspección, instalación y retiro | [views.py](../DATALAN/DATALAN/views.py#L1433-L1690) | Implementado |
| HU-09 | optimización general de solicitudes | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L2342-L2440) | Implementado y probado parcialmente |
| HU-10 | generación de equipos por etapa | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L519-L718) | Implementado |
| HU-11 | registro y evaluación inicial de incidencias | [views.py](../DATALAN/DATALAN/views.py#L728-L1289) | Implementado |
| HU-12 | coordinación, atención y cierre de incidencias | [views.py](../DATALAN/DATALAN/views.py#L728-L1289) | Implementado parcialmente |
| HU-13 | optimización general de incidencias NSGA-II | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1323-L1605) | Implementado |
| HU-14 | generación y selección de equipos para incidencias | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1645-L1805), [views.py](../DATALAN/DATALAN/views.py#L2200-L2340) | Implementado |
| HU-15 | configuración de algoritmos | [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L97-L188) | Implementado |

Se debe recordar que la relación con las historias no es un criterio de aceptación “oficial” del negocio, sino una trazabilidad del código actual frente a la intención de diseño.

## 14. Correspondencia con las cinco iteraciones

### 1. Acceso y perfiles técnicos

Se corresponde con la parte de roles, `ROLES`, autenticación y perfiles normales de técnicos. [auth_service.py](../DATALAN/DATALAN/auth_service.py#L1-L95), [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L728-L918)

### 2. Solicitudes operativas

Se corresponde con `workflow`, `commercial_status`, decisiones comerciales, asignación y etapas. [views.py](../DATALAN/DATALAN/views.py#L2371-L2753), [workflow_service.py](../DATALAN/DATALAN/workflow_service.py#L119-L170)

### 3. Incidencias

Se corresponde con la lógica de reportes, atención y solución, así como la coordinación con Soporte y Sistemas. [views.py](../DATALAN/DATALAN/views.py#L728-L1289), [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1212-L1605)

### 4. Algoritmos genéticos y configuración mediante CRISP-DM

Se corresponde con `save_optimization_config()` y `save_incident_nsga2_config()`, y con la lógica del algoritmo para solicitudes y equipos. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L97-L188), [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L519-L718), [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1323-L1605)

### 5. Integración y evaluación

Se corresponde con la vista de flujo, la llamada a servicios y la renderización de resultado. La integración de pruebas y del entorno de Django se observa en los tests ejecutados y en la base de datos PostgreSQL. [settings.py](../DATALAN/DATALAN/settings.py#L32-L75), [test_optimization_service.py](../DATALAN/DATALAN/test_optimization_service.py)

### Iteración 4, organización CRISP-DM

- Comprensión del negocio: la estructura de roles, estados y pantallas explica las decisiones operativas del estudio. [auth_service.py](../DATALAN/DATALAN/auth_service.py#L1-L95), [urls.py](../DATALAN/DATALAN/urls.py#L1-L118)
- Comprensión de los datos: perfiles, horarios, ausencias, capacidades y carga. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L728-L918)
- Preparación de los datos: normalización, parsing de entradas y validación de estados. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L728-L918)
- Modelado: algoritmos genéticos y NSGA-II. [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L519-L718), [optimization_service.py](../DATALAN/DATALAN/optimization_service.py#L1323-L1605)
- Evaluación: tests y comprobación de resultados. [test_optimization_service.py](../DATALAN/DATALAN/test_optimization_service.py)
- Integración en el entorno de prueba: Django + PostgreSQL + tests de vista y servicio. [settings.py](../DATALAN/DATALAN/settings.py#L32-L75)

## 15. Indicadores que realmente pueden medirse

Se revisó qué cosas pueden medirse con los datos actuales y sin inventar resultados. A continuación se presentan indicadores y limitaciones:

| Indicador | Definición y fórmula | Datos necesarios | Datos guardados | Unidad | Limitaciones | Tipo |
|---|---|---|---|---|---|---|
| Trazabilidad | seguimiento del estado del trabajo y de los cambios históricos | `history`, fechas y roles | sí | texto/registro histórico | no siempre completo para cada transición | medible operativo |
| Cumplimiento de condiciones de asignación | si el técnico cumple disponibilidad, horario, capacidad y estado | perfiles, trabajo activo, fechas | sí | booleano / porcentaje | depende de la normalización del perfil y del estado | medible operacional |
| Distribución de carga | diferencia entre tarea asignada y carga existente | `base_workloads`, trabajos activos | parcialmente | horas o unidades | no siempre expresadas en horas, depende del cálculo | estimación |
| Tiempo de generación | duración real del algoritmo | `time.perf_counter()` o similares | no aparecía en la evidencia | segundos | no está integrado de forma consistente | medición de prueba |
| Espera estimada | diferencia entre `current_time` y siguiente inicio disponible | fechas/hora y urgencia | sí en el algoritmo | horas | depende de la definición de “siguiente inicio” | estimación |
| Tiempos reales registrados | fechas/hora de asignación, atención y cierre | campos de `history`, `reported_at`, `scheduled_at` | parcialmente | datetime | la información puede estar fragmentada | medible operativo |
| Otros indicadores | número de propuestas, fitness, pareto size | algoritmo y resultados | parcialmente | valores numéricos | no hay un panel histórico de resultados | prueba / deducción |

### Repetibilidad

La información actual permite repetir la evaluación solo si se conservan:

- datos de entrada (solicitudes, perfiles, incidencias, configuración del algoritmo),
- configuración (población, generaciones, cruce, mutación), y
- semilla aleatoria cuando el algoritmo usa `random_seed`.

El código actual muestra que se guarda la configuración de optimización en `optimizacion_configuracion`, pero no se encontró evidencia de un almacenamiento completo de resultados y semillas para auditoría histórica. Esto limita la reproducción completa del experimento.

## 16. Imágenes y diagramas para el capítulo

Se listan pantallas que pueden capturarse y lo que deben demostrar:

- Flujo de solicitudes: pantallas de Comercial, Planta Técnica y Sistemas; deben mostrar el paso de registro a aprobación y coordinación.
- Flujo de incidencias: pantallas de reportes, revisión de soporte, atención y cierre; deben mostrar la separación entre `attention` y `solution`.
- Procedencia de datos: pantallas de perfil técnico, gestión de usuarios, edición de capacidades y horarios; deben mostrar el origen del perfil que alimenta al algoritmo.
- Representación de alternativas de cada algoritmo: pantallas de optimización genérica y de propuestas por equipo; deben mostrar los resultados de fitness, orden y carga proyectada.
- Generación, selección y confirmación: pantallas de `GENERAR PROPUESTA` y confirmación de cronogramas; deben mostrar que la propuesta se guarda antes de la confirmación.
- Relación entre roles y funciones: pantallas `roles-accesos`, `usuarios`, `workflow` y dashboards; deben mostrar qué rol puede acceder y qué módulos tienen.

### Gráficos recomendados

- Diagrama de flujos por estado (solicitudes e incidencias): sí es viable y útil.
- Diagrama de procedencia de datos: útil para explicar que el algoritmo no trabaja sobre datos “nativos” aislados, sino sobre perfiles normalizados y solicitudes guardadas.
- Diagramas de alternativas: deben incluir una comparación de fitness / espera / carga y la selección final de ≤3 alternativas.
- Relación entre roles y funciones: se puede representar con un organigrama funcional, no necesariamente con datos calculados.

Los gráficos generados por el sistema deben distinguirse de los que hay que elaborar con resultados exportados: los primeros corresponden a pantallas y estados internos del sistema; los segundos necesitan exportar los resultados del algoritmo para comparar alternativas y periodos.

## 17. Resumen final de correcciones del documento

### Apartado académico

- Qué puede conservarse: la estructura general de roles, la separación entre solicitudes e incidencias, la lógica de perfil técnico, la idea de optimización genérica y el uso de NSGA-II para incidencias.
- Qué debe cambiarse: debe decirse con precisión que muchos elementos están “implementados” pero no todos están cubiertos por pruebas de navegador ni por pruebas de integración reales; debe también distinguir claramente entre “propuesta” y “confirmación ejecutada”.
- Redacción factual sugerida: “El sistema DATALAN implementa flujos de registro, evaluación, asignación y cierre para solicitudes e incidencias; en la parte operativa, se usan algoritmos genéticos para generar propuestas de equipo y NSGA-II para evaluar alternativas de atención. Sin embargo, la validación actual del código sigue presentando errores en tres pruebas relevantes y no se ha demostrado una verificación de navegador end-to-end.”
- Evidencia: `auth_service.py`, `views.py`, `optimization_service.py`, `urls.py`, `settings.py`, `test_optimization_service.py`, y la salida de `python manage.py test` con 123 pruebas y 1 fallo + 2 errores.

### Lista breve de conclusiones

1. Diferencias confirmadas respecto al informe anterior:
   - Sigue existiendo optimización para solicitudes e incidencias, pero con más validaciones de cronograma y disponibilidad.
   - Los perfiles técnicos y de incidencias se mantienen separados y normalizados.
   - El sistema no está totalmente estable: la suite actual tiene 3 pruebas con fallo/error.

2. Decisiones de negocio que todavía requieren definición:
   - gobernanza exacta de responsables y líderes en casos de reconfiguración,
   - política documental para valores por defecto y pesos del algoritmo,
   - política de confirmación concurrente, y
   - definición explícita de “reporte de continuidad del cliente” para incidencias.

3. Errores o limitaciones pendientes:
   - errores actuales en la suite (`test_eventual_inspection_deadline_uses_commercial_end_date`, `test_plant_technician_sends_tentative_inspection_details_to_assigned_support`, `test_systems_incidents_page_shows_interactive_support_reports`),
   - falta de verificación de navegador real,
   - falta de auditoría completa de resultados y semillas en la base de datos.

4. Evidencias disponibles:
   - código fuente de Django y templates,
   - tests automáticos,
   - configuración de base de datos y documentación histórica,
   - salida de ejecución de pruebas.

5. Afirmaciones que todavía no pueden sostenerse:
   - que el sistema está 100% validado operativamente,
   - que el flujo de incidencias es completamente consistente en todos los roles,
   - que los pesos del algoritmo son una decisión de negocio respaldada fuera del código.

El objetivo de este informe es entregar una descripción fiel del sistema actual, no ocultar diferencias ni presentar resultados que no se midieron ni se validaron de manera suficiente.
