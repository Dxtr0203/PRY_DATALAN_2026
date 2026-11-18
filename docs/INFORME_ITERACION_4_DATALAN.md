# Informe de la Iteración 4: algoritmos genéticos e integración en DATALAN

**Fecha de revisión:** 20 de octubre de 2026

**Alcance:** revisión del código actual, pantallas, flujos de confirmación y pruebas automatizadas. Este informe documenta lo que está implementado; no propone cambiar el sistema para ajustarlo a una especificación.

## Cómo leer la evidencia

- **[Conectado]**: hay un recorrido desde una pantalla/botón hasta la vista y el servicio del algoritmo.
- **[Solo código]**: existe una función o rama de código, pero no se encontró un botón o recorrido normal desde la interfaz que la utilice.
- **[Incompleto/pendiente]**: el comportamiento tiene una limitación explícita o no completa la regla del negocio.
- **[Probado]**: una prueba automatizada ejecutada comprueba el comportamiento indicado. Las pruebas de vista con `RequestFactory` y servicios simulados no equivalen a una prueba de navegador ni a una ejecución contra datos reales.
- **[Deducción del código]**: conclusión obtenida al seguir las funciones; no es una garantía documentada ni una prueba de concurrencia o despliegue.

Las referencias enlazan a los archivos fuente con sus líneas actuales. Los nombres y valores numéricos descritos abajo son reglas que aparecen en el código; salvo que se diga lo contrario, no se encontró un documento normativo de DATALAN que explique por qué se eligieron esos valores.

## 1. Resumen del funcionamiento actual

En el código hay cuatro recorridos conectados a la aplicación. El primero ordena solicitudes; el segundo recomienda equipos para etapas de solicitudes; el tercero propone asignaciones globales para incidencias; el cuarto propone un equipo para una incidencia en un horario tentativo.

| Uso | Quién, página y botón | Datos principales | Resultado y efecto |
|---|---|---|---|
| Optimización general de solicitudes | **Encargado de Sistemas → Optimización → Ejecutar optimización**. [Conectado] | Solicitudes con estado `APROBADA`, decisión comercial `APROBADO` y sin `assignment`; técnicos y perfiles; parámetros guardados. | Muestra fitness, historial y hasta tres órdenes de solicitudes con sus asignaciones sugeridas. No persiste la solución, no asigna técnicos ni cambia estados. Sí persiste la configuración enviada. |
| Propuestas para inspección, instalación y retiro eventual | **Soporte de Sistemas** —o Encargado de Sistemas actuando como usuario de soporte asignado— abre el trabajo y usa **GENERAR PROPUESTA** en la etapa correspondiente. El botón de retiro solo aplica a solicitudes eventuales. [Conectado] | Una solicitud y etapa `ENVIADA`, fecha/hora tentativa por punto, técnicos, perfiles, ausencias y agendas operativas conocidas. | Muestra hasta tres equipos. La propuesta se guarda en `genetic_team_proposals`, pero no confirma por sí misma equipo ni horario. El botón posterior de confirmación exige seleccionar una propuesta y conservar la misma fecha/hora. |
| Optimización general de incidencias | **Encargado de Sistemas → Incidencias → Optimización NSGA-II → Ejecutar NSGA-II**. [Conectado] | Incidencias abiertas recibidas por el servicio, perfiles de técnicos, carga base y configuración NSGA-II. | Presenta hasta tres planes de asignación y la carga proyectada. No guarda el plan como asignación, no cambia estados y no reserva horarios; la pantalla no proporciona un botón para aplicar directamente uno de esos planes. |
| Equipo para incidencia y horario concretos | **Soporte de Sistemas → Incidencias → reporte propio → aprobación de atención → GENERAR PROPUESTA**. [Conectado para Soporte]. La API también autoriza a Sistemas en ciertas incidencias reportadas por Soporte, pero la plantilla de reportes de Sistemas oculta este botón. | Una incidencia, etapa `attention`, fecha/hora que se desea aprobar, técnicos elegibles, cargas y ocupaciones conocidas. | Muestra hasta tres equipos de dos o tres técnicos y guarda las alternativas en `team_proposals`. Al seleccionar y confirmar, el flujo guarda horario, equipo y líder; también sustituye el responsable técnico de la incidencia por el líder seleccionado. |

No se encontró un botón de algoritmo para la etapa **solución** de incidencias: el endpoint de equipo rechaza cualquier etapa distinta de `attention`. La optimización global de incidencias y la propuesta para horario son dos funciones distintas, aunque ambas se etiquetan NSGA-II.

## 2. Recorrido desde la pantalla hasta el resultado

### 2.1 Solicitudes: orden genético global

1. **Pantalla:** ruta `sistemas/optimizacion/`, definida en [`urls.py:L87-L90`](../DATALAN/DATALAN/urls.py#L87), con el botón **Ejecutar optimización** y los parámetros en [`workflow.html:L60-L99`](../DATALAN/DATALAN/templates/workflow.html#L60).
2. **Vista:** `workflow()` valida el rol y, al recibir POST en la pantalla `systems_optimization`, guarda la configuración, filtra entradas y llama al algoritmo en [`views.py:L2072-L2090`](../DATALAN/DATALAN/views.py#L2072) y [`views.py:L2451-L2472`](../DATALAN/DATALAN/views.py#L2451).
3. **Filtro:** `optimization_candidates()` exige `status == APROBADA`, `commercial_status == APROBADO` y ausencia de asignación en [`views.py:L1765-L1771`](../DATALAN/DATALAN/views.py#L1765).
4. **Algoritmo:** `run_genetic_optimization()` evalúa los órdenes y retorna la solución mejor puntuada y las alternativas en [`optimization_service.py:L2341-L2440`](../DATALAN/DATALAN/optimization_service.py#L2341).
5. **Resultado:** `workflow.html` dibuja fitness, órdenes y asignaciones sugeridas. No presenta un botón para confirmar esas asignaciones.
6. **Confirmación posterior:** se debe realizar por las pantallas/flujos habituales de asignación; la ejecución no las envía allí ni las guarda como decisión.

**Persistencia:** la solicitud se lee y escribe mediante el adaptador PostgreSQL [`workflow_service.py:L101-L145`](../DATALAN/DATALAN/workflow_service.py#L101). En este recorrido, el POST guarda los parámetros con `save_optimization_config()` y calcula el resultado en la respuesta, pero no llama a `save_requests()` para registrar el cromosoma ganador.

### 2.2 Solicitudes: propuestas genéticas por etapa

1. **Pantalla y botón:** el modal de Soporte contiene botones para inspección, instalación y retiro en [`support-work-modal.html:L100-L160`](../DATALAN/DATALAN/templates/support-work-modal.html#L100). El controlador JS envía cada acción al endpoint en [`app.js:L2195-L2203`](../DATALAN/DATALAN/static/js/app.js#L2195).
2. **Ruta/API:** `api/propuesta-equipo-genetica/`, definida en [`urls.py:L32-L34`](../DATALAN/DATALAN/urls.py#L32).
3. **Autorización y datos:** `generate_operational_team_proposals()` verifica el rol de Sistemas/Soporte, que el usuario esté asignado a la solicitud, la etapa, su estado y el horario en [`views.py:L1820-L1890`](../DATALAN/DATALAN/views.py#L1820).
4. **Configuración:** carga `get_optimization_config()` —la misma clave `genetic` de la pantalla de Sistemas— y llama `run_genetic_team_optimization()`.
5. **Persistencia de la propuesta:** guarda el resultado en `item['genetic_team_proposals'][stage_name]` y llama `save_requests()` antes de devolver el JSON. Guardar esa propuesta no equivale a asignar el equipo.
6. **Selección y confirmación:** JS muestra las propuestas; Soporte selecciona una y luego confirma el cronograma en [`app.js:L1560-L1625`](../DATALAN/DATALAN/static/js/app.js#L1560) y [`app.js:L2195-L2210`](../DATALAN/DATALAN/static/js/app.js#L2195). El servidor usa `_approved_team_for_schedule()` para exigir una propuesta existente, sin déficit de personal y con la firma de fechas/horas sin cambios, en [`views.py:L2027-L2069`](../DATALAN/DATALAN/views.py#L2027).
7. **Aceptación:** inspección queda en `technician_inspection['assigned_team']`; instalación y retiro quedan en `delivery_workflow[stage]['assigned_team']`. Se guarda el cronograma como aprobado. La aprobación no vuelve a ejecutar el algoritmo.

**¿Soporte utiliza la configuración de Sistemas? Sí.** Los tres botones de Soporte llaman la API anterior, que lee `get_optimization_config()`. No hay un formulario separado para que Soporte guarde otra población, tasa o configuración genética. Cambiar la configuración en Sistemas afecta las siguientes propuestas por etapa generadas por Soporte.

### 2.3 Incidencias: asignación global NSGA-II

1. **Pantalla y botón:** ruta `sistemas/incidencias/optimizacion/` en [`urls.py:L87-L90`](../DATALAN/DATALAN/urls.py#L87); botón **Ejecutar NSGA-II** en [`workflow.html:L115-L119`](../DATALAN/DATALAN/templates/workflow.html#L115).
2. **Vista y configuración:** `workflow()` persiste la configuración `incident_nsga2`, obtiene técnicos y carga base, aplana incidencias y llama a `run_incident_nsga2()` en [`views.py:L2474-L2500`](../DATALAN/DATALAN/views.py#L2474).
3. **Algoritmo:** `run_incident_nsga2()` construye población, calcula espera/carga, evoluciona y retorna alternativas en [`optimization_service.py:L1388-L1610`](../DATALAN/DATALAN/optimization_service.py#L1388).
4. **Resultado:** la plantilla muestra técnico recomendado, comienzo estimado, espera y cargas en [`workflow.html:L115-L121`](../DATALAN/DATALAN/templates/workflow.html#L115).
5. **Confirmación:** no hay botón de aceptación de plan global. La pantalla dice que no asigna automáticamente. Para asignar una incidencia se usa el flujo de asignación y aprobación correspondiente.

### 2.4 Incidencias: propuesta NSGA-II para horario

1. **Pantalla y botón:** Soporte abre la aprobación de la etapa de atención y pulsa **GENERAR PROPUESTA**, definido en [`reporter-incident-approval.html:L1-L9`](../DATALAN/DATALAN/templates/reporter-incident-approval.html#L1). La modal para alternativas está en [`service-incident-report.html:L11-L20`](../DATALAN/DATALAN/templates/service-incident-report.html#L11).
2. **Cliente JS:** envía CITE, ID de incidencia, etapa y fecha/hora al endpoint, y permite seleccionar una alternativa en [`app.js:L2782-L2955`](../DATALAN/DATALAN/static/js/app.js#L2782).
3. **Ruta/API:** `api/propuesta-equipo-incidencia/`, en [`urls.py:L32-L34`](../DATALAN/DATALAN/urls.py#L32).
4. **Vista:** `generate_service_incident_team_proposals()` exige usuario autorizado, etapa `attention`, horario tentativo enviado y fecha no pasada; recopila cargas y llama a `run_incident_team_nsga2()` en [`views.py:L1910-L2024`](../DATALAN/DATALAN/views.py#L1910).
5. **Persistencia de propuesta:** asigna identificadores a las alternativas, guarda el objeto en `stored_incident['team_proposals']['attention']` y persiste las solicitudes. Todavía no cambia el responsable ni aprueba el horario.
6. **Aceptación:** al enviar el formulario de aprobación, `handle_service_incident_workflow_post()` valida la propuesta elegida y la fecha/hora; guarda `workflow.attention.assigned_team`, marca la etapa aprobada y cambia `plant_technician_assignee` al líder en [`views.py:L486-L698`](../DATALAN/DATALAN/views.py#L486).

La configuración que lee este endpoint es `incident_nsga2`, la misma que se edita desde la pantalla de Sistemas, no la configuración `genetic`.

## 3. Datos utilizados y su procedencia

Las solicitudes operativas se guardan mediante `workflow_service.py`; perfiles/configuración de optimización se guardan en PostgreSQL en `datalan.optimizacion_tecnicos` y `datalan.optimizacion_configuracion`. Las pruebas abajo descritas usan datos sintéticos, objetos en memoria o mocks; no representan mediciones productivas.

| Dato | Dónde se registra o calcula | Uso algorítmico | Si falta |
|---|---|---|---|
| Capacidades de inspección, instalación y retiro | Perfil operativo editado por Planta Técnica. Los grupos están en [`optimization_service.py:L15-L67`](../DATALAN/DATALAN/optimization_service.py#L15); lectura y normalización en [`optimization_service.py:L728-L815`](../DATALAN/DATALAN/optimization_service.py#L728). | GA global infiere requisitos de solicitudes y verifica capacidades del equipo. Propuesta de etapa puntúa el grupo completo de capacidades de esa etapa. | Perfil normalizado puede quedar en `SIN_EVALUAR`; no es lo mismo que capacidad probada. En la ruta general, `SIN_EVALUAR` puntúa 0,25 y puede satisfacer la prueba `> 0`; en la propuesta por etapa reduce el puntaje pero no hace automáticamente inválido al equipo. |
| Capacidades de incidencias | Perfil separado de incidencias, actualizado por Planta Técnica; nueve capacidades definidas en [`optimization_service.py:L7-L25`](../DATALAN/DATALAN/optimization_service.py#L7) y guardadas por separado en [`optimization_service.py:L953-L1010`](../DATALAN/DATALAN/optimization_service.py#L953). | El NSGA-II de incidencias exige que cada requisito inferido tenga por lo menos un miembro con `CON_APOYO` o `SIN_APOYO`. | `SIN_EVALUAR` y `NO_REALIZA` no califican. |
| Capacidades compartidas OTDR/fusiones | `INCIDENT_SHARED_CAPABILITIES`, [`optimization_service.py:L20-L25`](../DATALAN/DATALAN/optimization_service.py#L20), y `_incident_skill_value()`, [`optimization_service.py:L1243-L1252`](../DATALAN/DATALAN/optimization_service.py#L1243). | Para incidencias, OTDR y fusiones se leen del perfil operativo de instalación; el resto, del perfil de incidencias. | No se duplican en la ficha de incidencias; un valor operativo sin evaluar no habilita esas capacidades en el NSGA-II de incidencias. |
| Experiencia y liderazgo | Perfil operativo del técnico; perfil de incidencias tiene además `lead_incidents`. Funciones de validación/actualización en [`optimization_service.py:L817-L951`](../DATALAN/DATALAN/optimization_service.py#L817) y [`optimization_service.py:L979-L1210`](../DATALAN/DATALAN/optimization_service.py#L979). | Puntúan equipos para solicitudes; para la propuesta NSGA-II de equipo de incidencia puntúan experiencia y `lead_incidents`. El NSGA-II global de incidencias no usa experiencia ni liderazgo para decidir. | Experiencia normalizada/por defecto queda en cero y liderazgo sin evaluar se valora parcialmente; en las propuestas de etapas, los equipos de inspección/retiro con líder valorado `NO` son rechazados, pero `SIN_EVALUAR` no se rechaza. |
| Estado operativo y disponibilidad | `operational_profile.operational_status` y `available`, editados/guardados en ficha técnica. | Filtro estricto `ACTIVO` y disponible para GA operativo y NSGA-II; filtro `staff_type == 'TÉCNICO'` excluye al encargado en esos algoritmos. | En NSGA-II, técnico sin disponibilidad explícita se interpreta disponible por defecto, pero igualmente requiere perfil/jornada utilizable. |
| Jornada y ausencias | Perfil operativo de Planta Técnica. | Propuestas de etapa comprueban jornada, ausencias y ocupaciones; NSGA-II global calcula siguiente comienzo de jornada; NSGA-II de equipo filtra fecha/hora concreta. | NSGA-II excluye técnicos sin días y horas configurados. La propuesta genética por etapa, en cambio, solo aplica el filtro de jornada si existen días configurados; sin días puede no aplicar la restricción de jornada. |
| Trabajos asignados / carga | Se calcula desde solicitudes activas y sus asignaciones; helpers en [`views.py:L808-L877`](../DATALAN/DATALAN/views.py#L808) y [`optimization_service.py:L491-L517`](../DATALAN/DATALAN/optimization_service.py#L491). | GA global actualiza carga por solicitud asignada en el cromosoma. La propuesta de etapa usa conteos activos. NSGA-II global recibe la carga inicial y suma las nuevas incidencias. | La unidad es principalmente un conteo, no horas. El resumen `prepare_technician_assignment_summaries()` identifica responsables y miembros de `assignment`, pero no inspecciona todos los `assigned_team` de cada etapa; el conteo de `_active_workload_counts()` sí recorre esos equipos. |
| Prioridad | Se deriva de la fecha de instalación (o inicio eventual) en [`views.py:L752-L794`](../DATALAN/DATALAN/views.py#L752), y se recalcula al preparar la vista en [`views.py:L2096-L2103`](../DATALAN/DATALAN/views.py#L2096). | Peso de prioridad y duración ponderada en GA; tamaño de equipo en propuesta por etapa. | Sin fecha se conserva el valor que tenga la solicitud. En incidencias, urgencia es severidad/prioridad si existe; si no, se usa antigüedad del reporte. |
| Fecha y hora tentativas/aprobadas | Las registra Planta Técnica y las confirma Soporte/Sistemas; manejadores en [`views.py:L1134-L1275`](../DATALAN/DATALAN/views.py#L1134) y [`views.py:L486-L698`](../DATALAN/DATALAN/views.py#L486). | GA por etapa usa horario tentativo para probar disponibilidad. NSGA-II global **no** ordena por horario ya aprobado; estima el siguiente inicio desde el momento de ejecución. NSGA-II de equipo evalúa una fecha/hora fijada. | Propuesta por etapa sin un punto horario válido falla. En la propuesta de equipo de incidencia se usa la hora enviada como hora a estudiar. |
| Duración estimada | Solicitud o evaluación de Planta Técnica; `prepare_request()` y `_stage_total_duration_hours()` en [`optimization_service.py:L2005-L2045`](../DATALAN/DATALAN/optimization_service.py#L2005) y [`optimization_service.py:L296-L309`](../DATALAN/DATALAN/optimization_service.py#L296). | GA general calcula tiempo de finalización acumulado; propuesta por etapa calcula intervalos; resumen de cargas puede mostrar horas explícitas. | GA general estima 4 h para multipunto o 2,5 h para otros tipos, más 0,75 h por capacidad inferida. Etapa usa 0,5 h para inspección y 2 h para instalación/retiro, repartido entre puntos. NSGA-II global no usa duración de reparación. |
| Distancia del enlace | Evaluación de Planta Técnica. | `prepare_request()` la normaliza; se usa para determinar el tamaño de equipo de una solicitud. No es el valor que se suma como distancia fitness del GA global. | Falta/inválida/negativa se convierte a 0 km. |
| Distancia de traslado del técnico | Perfil del técnico. | Puntaje de viaje para equipos; en el GA global, la distancia de equipo es promedio de los `travel_distance_km`; en la propuesta NSGA-II de equipo de incidencia también entra al fitness. | Valor inválido se normaliza a cero en la propuesta de incidencia; el GA general toma los perfiles técnicos disponibles. |
| Número de integrantes | Regla `activity_team_size()` en [`optimization_service.py:L228-L241`](../DATALAN/DATALAN/optimization_service.py#L228). | Propuestas por etapa; la optimización general de solicitudes también calcula tamaño de equipo de instalación según prioridad/distancia. | No es un campo calculado a partir de la solicitud por otra API; se deriva de prioridad y distancia con reglas fijas detalladas en la sección 8. |
| Responsable técnico inicial | `plant_technician_assignee` se asigna en la pantalla de Soporte o en Planta Técnica para incidencias. Ramas en [`views.py:L546-L575`](../DATALAN/DATALAN/views.py#L546) y [`views.py:L2732-L2763`](../DATALAN/DATALAN/views.py#L2732). | No se usa como restricción que obligue a incluirlo en los equipos genéticos. | El efecto de aceptar una propuesta es diferente entre solicitudes e incidencias; ver sección 6. |

**Separación y reutilización:** capacidades generales, experiencia, jornada, ausencias, estado y disponibilidad pertenecen al perfil operativo común. Las capacidades específicas de incidencia y el permiso para dirigir incidencias se guardan en `incident_profile`. OTDR y fusiones de incidencias apuntan al perfil operativo compartido. Carga, asignación y cronogramas se calculan desde las solicitudes/incidencias; no son los campos de capacidad.

## 4. Algoritmo genético con codificación permutacional

### 4.1 Modalidad global: orden de solicitudes

**Representación.** Un gen es el índice de una solicitud elegible; el cromosoma es un orden de todos esos índices. Por ejemplo, `[R2, R1, R3]` significa atender primero R2, luego R1 y después R3. No se permutan técnicos ni actividades. El técnico/equipo se determina después al decodificar el orden. Inicialización, evaluación, selección y archivo están en [`optimization_service.py:L2341-L2440`](../DATALAN/DATALAN/optimization_service.py#L2341); decodificación en [`optimization_service.py:L2138-L2325`](../DATALAN/DATALAN/optimization_service.py#L2138).

**Población inicial.** El primer cromosoma ordena por prioridad descendente y, en empate, por duración estimada menor. El resto son permutaciones aleatorias. Una solución contiene cada solicitud exactamente una vez.

**Decodificación.** Recorre las solicitudes en el orden del cromosoma. Con los perfiles actuales crea equipos compatibles con la capacidad requerida y el tamaño derivado para instalación; elige el equipo con mejor valoración y actualiza las cargas para las siguientes solicitudes. Si no hay equipo compatible, deja la solicitud en el orden con `SIN TÉCNICO COMPATIBLE`, y la cobertura baja. Los candidatos deben ser técnicos, activos y disponibles; las capacidades necesarias se construyen a partir del texto y `equipment_enabled`.

**Puntajes normalizados.** Para cada solicitud, los pesos de prioridad son 3 (Alta), 2 (Media) y 1 (Baja). `pos(i)` es el lugar en el orden, empezando por cero:

```text
C_prioridad = Σ prioridad_i × pos(i)
S_prioridad = 100 × (C_peor − C_prioridad) / (C_peor − C_mejor)
```

Si los límites coinciden, el código devuelve 100. El menor costo queda mejor puntuado.

El costo temporal suma la hora acumulada de finalización de cada solicitud multiplicada por su peso de prioridad:

```text
T_i = Σ_{k hasta i en el orden} duración_k
C_tiempo = Σ T_i × prioridad_i
S_tiempo = 100 × (C_tiempo_peor − C_tiempo) / (C_tiempo_peor − C_tiempo_mejor)
```

La normalización temporal compara con un orden de referencia por prioridad/duración y con su inverso. `T_i` y la duración se expresan en horas estimadas.

En el modo con perfiles operativos:

```text
distancia_total = Σ distancia_media_del_equipo_por_solicitud_asignada
S_distancia = 100 × [1 − distancia_total / (distancia_máxima_técnico × número_de_solicitudes)]
S_carga = 100 / [1 + varianza(cargas finales)]
S_equipo = Σ fitness_equipo_de_solicitudes_asignadas / número_de_solicitudes

fitness = cobertura × (
    0,25 S_prioridad + 0,20 S_tiempo + 0,15 S_distancia
  + 0,15 S_carga + 0,25 S_equipo
)
```

`cobertura` es la fracción de solicitudes asignadas (0–1). `distancia_máxima_técnico` es la mayor distancia de traslado del perfil de los técnicos disponibles; una solicitud no asignada no aporta distancia al numerador, pero sí permanece en el denominador. Si no hay solicitudes o la distancia máxima es cero, el código asigna 100 a `S_distancia`. Una asignación sin equipo aporta cero al numerador de `S_equipo`, cuyo denominador también es el total de solicitudes. La distancia del enlace de Planta Técnica interviene en el tamaño del equipo, no en este subpuntaje de traslado. La varianza de carga tiene unidades de conteo al cuadrado; no se transforma en horas.

El `fitness` del equipo contiene: 50 % capacidades, 20 % liderazgo, 15 % experiencia, 10 % carga y 5 % traslado. La capacidad es la media del mejor valor de cada capacidad entre los miembros; experiencia se normaliza respecto a 10 años; carga y traslado se transforman como `1/(1 + valor)`. Valores por capacidad: `SIN_APOYO=1`, `CON_APOYO=0,7`, `SIN_EVALUAR=0,25`, `NO_REALIZA=0`.

**Importante: hay dos fórmulas según la entrada.** El código conserva también una ruta heredada sin perfiles operativos que puntúa 35 % prioridad, 30 % tiempo, 20 % distancia y 15 % carga. Sin embargo, `get_technicians()` entrega perfiles operativos, por lo que el flujo actual de Sistemas entra normalmente en la fórmula de cinco componentes de arriba. La pantalla todavía publica 35/30/20/15 en su bloque de pesos, contradicción que se debe señalar y no copiar como fórmula de runtime. Véase [`workflow.html:L60-L62`](../DATALAN/DATALAN/templates/workflow.html#L60) frente a [`optimization_service.py:L2290-L2320`](../DATALAN/DATALAN/optimization_service.py#L2290).

**Selección y operadores.**

- Torneo de tamaño 3 para escoger cada progenitor.
- Elitismo: el mejor cromosoma pasa directamente a la generación siguiente.
- Cruce OX (*Order Crossover*): copia un segmento del primer progenitor y completa el hijo en orden circular con genes no repetidos del segundo.
- Mutación por intercambio: con la probabilidad indicada por hijo, intercambia dos posiciones.
- Se evalúa desde generación 0 hasta el número configurado de generaciones; no hay parada por convergencia.
- Se conserva un archivo de los tres mejores cromosomas distintos por orden de genes. La lista final puede tener menos de tres elementos si solo se encontraron menos de tres órdenes distintos.

Las alternativas son **órdenes distintos**, no necesariamente asignaciones distintas. Dos órdenes diferentes pueden decodificarse en los mismos equipos.

### 4.2 Modalidad por etapa: equipo genético para solicitud

**Sí existe una propuesta específica para inspección, instalación y retiro eventual desde Soporte.** La función conectada es `run_genetic_team_optimization()`, llamada por el botón de propuesta; el retiro solo se habilita en solicitudes eventuales. Referencias: [`views.py:L1820-L1907`](../DATALAN/DATALAN/views.py#L1820), [`optimization_service.py:L519-L730`](../DATALAN/DATALAN/optimization_service.py#L519).

**Qué representa ahora el cromosoma.** Cada cromosoma es una permutación de los técnicos candidatos disponibles para esa etapa. Al evaluarlo, se toma su prefijo de longitud `team_size`; el resto del cromosoma no integra el equipo de esa alternativa. No ordena las solicitudes. Se evalúa el equipo seleccionado, y el archivo evita repetir el mismo conjunto de `technician_id`. Por tanto, las alternativas que muestra esta modalidad son **equipos distintos**, no órdenes de actividad ni ambos.

La población combina un orden inicial por puntuación de capacidades/liderazgo/carga y permutaciones aleatorias. En la ruta con personal suficiente aplica torneos de tamaño 3, elitismo, cruce OX y mutación por intercambio. La evaluación del equipo usa 50 % capacidades de la etapa, 20 % liderazgo, 15 % experiencia, 10 % carga y 5 % traslado.

**Actividades y requisitos diferentes.** Sí cambia el grupo de capacidades que se puntúa para inspección, instalación y retiro, y también el tamaño de equipo recomendado. Sin embargo, esta propuesta no infiere requisitos de la descripción individual del trabajo como lo hace el GA global: puntúa el conjunto de capacidades de la categoría de etapa. El score parcial puede ser bajo; no se exige que cada miembro cubra todas las capacidades. Tampoco se exige explícitamente que alguien marcado `CON_APOYO` vaya acompañado por alguien `SIN_APOYO`.

**Si no hay suficientes candidatos:** para instalación el código permite una rama `combinatorial_reference`: enumera combinaciones más pequeñas y no ejecuta generaciones (`generations_completed = 0`); reduce fitness por el déficit de personal. Para inspección/retiro, si no alcanza el tamaño requerido, responde con error. El servidor impide confirmar propuestas con `staffing_shortage` mayor que cero. Es evidencia de que no todo botón de propuesta ejecuta realmente evolución genética.

**Confirmación y cantidad de alternativas.** El resultado tiene hasta tres equipos únicos. Si existe solo un equipo válido, el archivo puede devolver una alternativa (no crea alternativas ficticias). Las pruebas comprueban tres equipos únicos en fixtures concretos, no que siempre haya tres en operación.

## 5. NSGA-II para incidencias

### 5.1 Modo general: varias incidencias abiertas

La función conectada es `run_incident_nsga2()`, llamada desde la pantalla de optimización de Sistemas. Excluye estados `CERRADA` y `PENDIENTE DE VALIDACIÓN`. Si alguna incidencia abierta no tiene candidato compatible, termina con error, en vez de inventar una asignación. Véase [`optimization_service.py:L1217-L1253`](../DATALAN/DATALAN/optimization_service.py#L1217), [`optimization_service.py:L1388-L1610`](../DATALAN/DATALAN/optimization_service.py#L1388).

**Representación.** Cada gen corresponde a una incidencia y almacena el índice de un técnico compatible. Un técnico puede aparecer en varios genes. Cada individuo es, por tanto, una asignación de todas las incidencias abiertas, no una permutación.

**Objetivo 1: espera ponderada por urgencia, en minutos ponderados.**

```text
espera_ij = max(0, siguiente_inicio_j − ahora), en minutos
W = Σ_i urgencia_i × espera_i,asignada
```

Pesos de urgencia: 4 para crítica/urgente/alta, 2 para media/moderada y 1 para baja. Si no hay severidad reconocible, se empieza en 1, aumenta 1 por cada dos días de antigüedad y se limita a 4. Sin fecha interpretable, vale 1.

**Objetivo 2: desequilibrio de carga, en conteos al cuadrado.**

```text
L_j = carga_base_j + incidencias_nuevas_asignadas_a_j
L_media = promedio_j(L_j)
D = Σ_j (L_j − L_media)²
```

Se minimizan `(W, D)` sin combinar ambos en una suma ponderada. Una alternativa puede ofrecer menos espera y otra mejor distribución.

**Desde cuándo y qué horarios usa.** El origen es la hora de ejecución (`datetime.now()` si no se inyecta una hora de prueba). Para cada técnico se busca el próximo comienzo de jornada disponible, hasta 366 días, aplicando días laborales y ausencias. Todas las incidencias asignadas a ese técnico reciben ese mismo inicio estimado. El modelo no tiene duración de reparación, no secuencia las incidencias sobre una agenda y no reserva horas. Un trabajo activo alimenta la carga base, pero su intervalo horario no se incorpora a este NSGA-II.

**Población y operadores.** Población inicial aleatoria sobre candidatos válidos por incidencia. En cada generación se toman dos individuos aleatorios; no hay torneo de padres. Con la tasa de cruce, cada gen hereda aleatoriamente el técnico del padre izquierdo o derecho. La mutación se aplica **por gen**: cada posición tiene una probabilidad propia de cambiar a otro candidato compatible. Se combinan padres e hijos, se ordena por frentes no dominados y se completa la población desde los mejores frentes; en el último frente se eligen mayores distancias de crowding.

**Resultados:** recorre los frentes desde el primero, ordena por menor espera y mayor crowding, quita planes idénticos y devuelve hasta tres. Si hay menos de tres planes únicos en el primer frente, continúa a frentes posteriores. Por eso **no está garantizado que todos los resultados mostrados sean del primer frente**, aunque la pantalla se titule “Alternativas Pareto”; `pareto_size` sí es específicamente el tamaño del frente uno. No hay criterio de convergencia anticipada; termina tras las generaciones configuradas.

El modo global vuelve a considerar incidencias abiertas que ya tienen `plant_technician_assignee`: ese campo no se usa para fijar el gen ni excluir la incidencia. Esas incidencias se vuelven a asignar en cada plan. La carga de estas incidencias no se cuenta en la carga base del modo global: se contabilizan como las incidencias que el plan está asignando. No se evita la inclusión por tener responsable.

### 5.2 Propuesta de equipo para incidencia y horario fijado

La función es `run_incident_team_nsga2()`. En la interfaz normal solo se conecta a la etapa `attention` y a un horario tentativo que el usuario introduce o conserva del reporte. El endpoint rechaza `solution`. Referencias: [`views.py:L1910-L2024`](../DATALAN/DATALAN/views.py#L1910), [`optimization_service.py:L1611-L2005`](../DATALAN/DATALAN/optimization_service.py#L1611).

**Decisión y representación.** Decide qué equipo (de dos o tres técnicos) podría atender esa incidencia a esa hora. Un individuo es una combinación de técnicos distintos; se ejecuta una población por tamaño de equipo 2 y otra por tamaño 3. Deben estar activos, disponibles, tener horario configurado, trabajar ese día y no estar ausentes u ocupados a la hora de inicio. Cada capacidad requerida por el texto debe estar cubierta por al menos un miembro con `CON_APOYO` o `SIN_APOYO`.

**Objetivo de calidad de equipo.**

```text
F = 100 × (
    0,50 × capacidades
  + 0,20 × liderazgo
  + 0,15 × experiencia
  + 0,10 × carga
  + 0,05 × traslado
)
```

Capacidades y experiencia se normalizan/valoran en escala 0–1. La carga y el traslado se convierten como `1/(1 + promedio)`. Los valores de capacidad son `SIN_APOYO=1`, `CON_APOYO=0,7`, `SIN_EVALUAR=0,25`, `NO_REALIZA=0`; para validar la cobertura dura, sin embargo, solo cuentan `CON_APOYO` y `SIN_APOYO`.

**Objetivos que realmente minimiza NSGA-II:**

```text
O1 = 100 − F
O2 = promedio, entre integrantes, de (carga_base + 1)
```

El segundo objetivo mide conteos medios proyectados del equipo, no horas. Como la fecha/hora ya está fijada, NSGA-II no elige la hora ni reduce la espera; optimiza calidad del equipo y carga entre integrantes. El tamaño de equipo se explora como dos espacios separados, no como una dimensión objetivo comparada directamente.

**Operadores.** Padres mediante torneo binario: mejor rango de frente, luego mayor crowding. Cruce con probabilidad configurada: toma integrantes únicos de la unión de ambos padres hasta alcanzar el tamaño fijo del equipo. Mutación con probabilidad por equipo: reemplaza un miembro por otro no incluido. Si el hijo no es válido, busca un equipo válido aleatorio y, si no encuentra, conserva el primer padre. Reemplazo combina población y descendencia por rango y crowding.

**Ocupaciones contempladas.** Revisa intervalos aprobados de solicitudes operativas y registros de atención/solución de otras incidencias. Para otras incidencias considera las fechas `ENVIADA` (tentativas) o `APROBADA`, pero solo registra la hora de inicio por técnico responsable y la comparación se hace con igualdad exacta del instante. No modela su duración para bloquear el intervalo completo.

**Resultados:** archiva equipos factibles encontrados, calcula frentes del archivo y devuelve hasta tres recorriendo frentes en orden. Si el primer frente no aporta tres equipos únicos, puede añadir opciones de frentes posteriores; por tanto, tampoco aquí se garantiza que todas las tarjetas sean del frente uno. Si el número de combinaciones de técnicos es pequeño (hasta 5.000 por tamaño), primero enumera equipos válidos y los baraja; para cantidades mayores, muestrea equipos. Aun así ejecuta la evolución posterior.

## 6. Responsable técnico y equipo propuesto

La regla indicada —que el responsable de Planta permanezca en el equipo hasta concluir— **no está garantizada por los algoritmos actuales**.

### Solicitudes operativas

- La selección genética filtra técnicos disponibles por tipo, estado, jornada y compatibilidad; no reserva un lugar para `plant_technician_assignee`.
- El líder sugerido se elige según puntaje de liderazgo/experiencia. Puede ser distinto del responsable inicial.
- El tamaño recomendado es el tamaño de `team_size`; el equipo propuesto cuenta todos sus miembros, incluyendo el líder. El responsable inicial solo cuenta si aparece como miembro.
- Al aprobar, `assigned_team` se guarda en la etapa. `_approved_team_for_schedule()` no cambia `item['plant_technician_assignee']`; por ello el responsable original sigue en el campo de responsable y el equipo de la etapa puede no incluirlo.
- `assigned_technician_names()` incorpora tanto al responsable base como a integrantes de los equipos de etapa; el responsable original puede conservar autorización para completar etapas aunque no pertenezca al equipo propuesto.
- Si el responsable inicial no está disponible, el algoritmo no lo incluye como candidato; puede proponer otro equipo, sujeto a la regla de tamaño/escasez.

### Incidencias

- El NSGA-II de equipo tampoco obliga a incluir a `plant_technician_assignee`; solo evalúa candidatos activos/disponibles y compatibles.
- Al aceptar la propuesta de atención, el manejador cambia `incident['plant_technician_assignee']` al líder seleccionado. En este flujo sí puede reemplazar al responsable original.
- El equipo cuenta a todos los miembros, líder incluido. El líder puede ser otra persona.
- Si el responsable original no está disponible, puede quedar fuera de los candidatos; al aprobar, el líder elegido pasa a ser el responsable guardado.
- El NSGA-II global de incidencias solo recomienda y no actualiza ese campo.

La prueba `test_genetic_team_member_can_complete_their_approved_stage` comprueba que un miembro de equipo puede completar una etapa operativa. La prueba `test_service_incident_runs_through_assignment_approval_and_resolution` sigue un fixture de incidencia y comprueba la asignación del líder de la propuesta. Ninguna demuestra que el responsable inicial permanezca obligatoriamente en todos los equipos.

## 7. Disponibilidad y compatibilidad

| Pregunta | Comportamiento comprobado en el código |
|---|---|
| ¿Solo se comprueba la hora de inicio o todo el intervalo? | GA global de solicitudes no agenda intervalos. GA de propuestas por etapa deriva una duración y comprueba solapamiento de ausencias/intervalos ocupados en toda la duración; el día y horario laboral se comprueban por la hora inicial. Una prueba permite explícitamente una tarea que inicia a las 17:30, dura 3 h y acaba después de una jornada que termina a las 18:00. NSGA-II global de incidencias usa solo el próximo inicio; NSGA-II de equipo comprueba intervalos de solicitudes para el intervalo derivado, pero otras incidencias se comparan por igualdad del inicio. |
| ¿Combina solicitudes e incidencias? | La propuesta genética de solicitud revisa las agendas de solicitudes aprobadas, no las de incidencias. NSGA-II global de incidencias no consulta reservas horarias de solicitudes. La propuesta NSGA-II de equipo sí recibe solicitudes e incidencias, con las limitaciones de intervalos indicadas en la sección 5. |
| ¿Propuestas pendientes ocupan horarios? | Propuesta genética de solicitud sin aprobación no forma parte de las etapas `APROBADA` que construyen `_scheduled_intervals()`. La propuesta de equipo de incidencia sí ve etapas `ENVIADA` de otras incidencias por inicio tentativo y responsable. El NSGA-II global de incidencias no trata esos horarios tentativos como reservas. |
| ¿Se revalida disponibilidad al confirmar? | No se recalculan perfiles, turnos, ausencias ni conflictos con otros trabajos al aceptar. En solicitudes se valida que la propuesta exista, no tenga déficit y que las fechas/horas coincidan con su firma. En incidencias se valida identificador, tamaño, líder, miembros y coincidencia de horario, pero no se vuelve a comprobar disponibilidad/capacidades actuales. |
| ¿Puede confirmarse el mismo técnico/horario desde dos usuarios? | No se encontró una comprobación transaccional de exclusión de conflictos al confirmar ni una restricción única de reserva para técnico/intervalo. **Deducción del código:** puede haber conflicto si dos usuarios aprueban propuestas concurrentes. No se ejecutó prueba de concurrencia; no se afirma que haya ocurrido en producción. |
| ¿Qué sucede si falta horario o duración? | Solicitud: para generar una propuesta se exige al menos un punto con fecha/hora válida; si falta duración, se usan 0,5 h inspección y 2 h instalación/retiro (divididas entre puntos). Incidencia global: necesita que el perfil permita encontrar próximo inicio; sin días/horas/ausencias parseables el técnico no es elegible. Incidencia con hora fijada: debe ser fecha válida y futura. |
| ¿Qué significan los cuatro niveles? | `SIN_EVALUAR` = capacidad no acreditada; `NO_REALIZA` = valor cero/no apto en filtros estrictos; `CON_APOYO` y `SIN_APOYO` puntúan 0,7 y 1 en puntajes de equipo. En filtros duros de capacidades de incidencia, solo los dos últimos califican. |
| ¿“Con apoyo” obliga a un compañero “Sin apoyo”? | No. No se encontró restricción que exija tal acompañamiento. En incidencia, un solo miembro con `CON_APOYO` basta para cubrir la capacidad según el filtro; en propuestas genéticas de solicitud la comprobación por etapa tampoco impone esa combinación. **Pendiente/regla no implementada**, no debe describirse como garantizada. |

`_scheduled_intervals()` excluye del cálculo todas las etapas de la misma CITE que se está optimizando. La verificación posterior a la propuesta tampoco recalcula las ocupaciones; por tanto, los intervalos que eran válidos al generar pueden cambiar antes de aprobar.

## 8. Parámetros y reglas de evaluación

| Configuración | Predeterminados | Rangos validados | Almacenamiento | Usos |
|---|---|---|---|---|
| `genetic` | Población 40, generaciones 100, mutación 10 %, cruce 80 % | 2–200, 1–500, 0–100 %, 0–100 % | `datalan.optimizacion_configuracion`, clave `genetic`. | GA global de solicitudes y propuestas por etapa que genera Soporte. |
| `incident_nsga2` | Población 48, generaciones 80, mutación 15 %, cruce 85 % | 2–200, 1–500, 0–100 %, 0–100 % | Misma tabla, clave `incident_nsga2`. | NSGA-II global de incidencias y propuestas NSGA-II por horario desde el endpoint de Soporte. |

Constantes y lectura/guardado: [`optimization_service.py:L75-L188`](../DATALAN/DATALAN/optimization_service.py#L75). Los formularios son de Sistemas en [`workflow.html:L60-L62`](../DATALAN/DATALAN/templates/workflow.html#L60) y [`workflow.html:L115-L117`](../DATALAN/DATALAN/templates/workflow.html#L115). El rol se valida en `workflow()` y en las APIs; Soporte puede generar propuestas con la configuración existente, pero no se encontró un formulario propio para editarla.

**Mutación:** GA global de solicitudes y GA normal por etapa aplican una probabilidad por individuo/hijo y, si ocurre, un intercambio. NSGA-II global aplica la tasa por gen. NSGA-II de equipo aplica la tasa por equipo y cambia un miembro.

**Otras reglas fijas del código:**

- Equipo por etapa: inspección = 2 si prioridad alta o distancia >10 km, en otro caso 1; instalación = 5 si prioridad alta y distancia >25 km, 4 si prioridad alta o distancia >10 km, en otro caso 3; retiro = 4 si prioridad alta o distancia >25 km, en otro caso 3. Fuente: `activity_team_size()` enlazada arriba.
- Estimaciones de respaldo GA general: 4 h multipunto o 2,5 h otros, más 0,75 h por requisito detectado.
- Estimaciones de respaldo por etapa: inspección 0,5 h; instalación/retiro 2 h.
- Prioridad de instalación: en el helper del código, 0–3 días = Alta, 4–7 = Media, 8 o más = Baja; incidencia usa otra regla de urgencia por severidad/edad.
- En la ficha operativa de técnicos, los valores de perfil sembrados o heredados no equivalen a mediciones de producción; se deben revisar antes de interpretar una recomendación.

No se encontró una justificación aprobada de negocio para los pesos, umbrales, tasas o cantidades anteriores. Deben presentarse como **parámetros/reglas programados**, no como políticas oficialmente validadas. Además, [`guia_interfaz_optimizacion_genetica.md:L70-L98`](./guia_interfaz_optimizacion_genetica.md#L70) documenta la fórmula simplificada 35/30/20/15, mientras que la ejecución normal con perfil operativo usa 25/20/15/15/25. La pantalla repite la fórmula antigua; no es evidencia suficiente de que coincida con el cálculo ejecutado.

## 9. Pruebas y evidencia

### Ejecución realizada para este informe

Comando: `python manage.py test DATALAN.test_optimization_service DATALAN.test_technician_capabilities`, ejecutado desde el proyecto con el intérprete virtual del repositorio.

- **106 pruebas descubiertas; 105 pasaron y 1 terminó con error.**
- El error fue `test_eventual_inspection_deadline_uses_commercial_end_date` (`test_optimization_service.py:L3317-L3355`): al probar una fecha inválida mediante `RequestFactory`, la rama llama `messages.error` sin que el request de prueba tenga `MessageMiddleware`/`_messages`. El error observado no es un fallo de fitness/NSGA-II, pero sí impide declarar verde toda la suite.
- La comprobación de sistema de Django terminó sin problemas. Las pruebas son `SimpleTestCase` y usan mocks; no se ejecutó contra datos productivos.

También se ejecutó un conjunto focal de 12 pruebas específicas de algoritmos y recorridos:

```text
Ran 12 tests ... OK
System check identified no issues
```

Incluyó selección y persistencia de propuesta NSGA-II de incidencia, NSGA-II general y de equipo, renderizado de la pantalla NSGA-II, genes y restricciones del GA de solicitudes, alternativas distintas del GA, propuestas genéticas de etapa, validación de confirmación y acceso de un miembro del equipo a una etapa.

### Evidencia relevante en el código de pruebas

- [`test_optimization_service.py:L2058-L2199`](../DATALAN/DATALAN/test_optimization_service.py#L2058): requisitos, permutación, exclusión de técnicos no disponibles/incompatibles, equipos operativos, OX, tres cromosomas distintos y parámetros inválidos.
- [`test_optimization_service.py:L480-L645`](../DATALAN/DATALAN/test_optimization_service.py#L480): NSGA-II global y equipo, disponibilidad/exclusión, configuración separada y pantalla.
- [`test_optimization_service.py:L105-L212`](../DATALAN/DATALAN/test_optimization_service.py#L105): llamada de vista/API de propuesta de equipo de incidencia, guardado de la alternativa e intento no autorizado.
- [`test_optimization_service.py:L1176-L1334`](../DATALAN/DATALAN/test_optimization_service.py#L1176): flujo de incidencia desde responsable inicial hasta atención/solución y cierre, con funciones de persistencia/mensajes simuladas.
- [`test_technician_capabilities.py:L94-L150`](../DATALAN/DATALAN/test_technician_capabilities.py#L94): duración y disponibilidad por jornada de las propuestas de etapa.
- [`test_technician_capabilities.py:L256-L585`](../DATALAN/DATALAN/test_technician_capabilities.py#L256): carga por equipos aprobados, equipos genéticos, déficit de personal, cronograma y aprobación.

**Qué prueban y qué no prueban.** Hay pruebas de funciones y algunas de vistas/controladores con mocks. No equivalen a un test navegador completo, ni a una ejecución real contra PostgreSQL con el padrón actual. No encontré prueba de doble confirmación concurrente, refresco de disponibilidad entre propuesta y aprobación, cumplimiento de acompañamiento `CON_APOYO`, conservación obligatoria del responsable inicial, o que todos los resultados NSGA-II mostrados sean del primer frente.

## 10. Ejemplos comprensibles

Los ejemplos de esta sección son **ilustrativos**; no son salidas de las pruebas ni resultados de una ejecución real.

### A. Orden genético de solicitudes

Entrada: `R-ALTA` (prioridad Alta, 2 h) y `R-BAJA` (prioridad Baja, 1 h), ambas elegibles, con un técnico/equipo compatible.

```text
Cromosoma 1: [R-ALTA, R-BAJA]
Cromosoma 2: [R-BAJA, R-ALTA]
```

En el primer orden la solicitud Alta tiene posición 0 y la Baja posición 1: costo de prioridad `3×0 + 1×1 = 1`. En el segundo, el costo es `1×0 + 3×1 = 3`. El primero obtiene mayor puntaje normalizado de prioridad. El fitness final también depende de tiempo acumulado, traslados, carga, calidad del equipo y cobertura; no se puede deducir un fitness total solo con esos dos datos.

### B. Propuestas genéticas por etapa

Entrada ilustrativa: una instalación de prioridad Media y distancia de enlace 8 km con una fecha/hora tentativas y seis técnicos operativamente disponibles. La regla deriva tres integrantes. El algoritmo normal puede generar cromosomas de técnicos, decodificarlos como equipos de tres y ordenar hasta tres conjuntos distintos por fitness. Para inspección de prioridad Alta, el tamaño sería dos; para retiro de prioridad Media con distancia 26 km, cuatro.

Si en una instalación solo hay dos candidatos disponibles, el código pasa a enumerar equipos más pequeños, marca el déficit y puede mostrar esos equipos como referenciales. El manejador de aprobación los rechaza si el déficit sigue presente. Este ejemplo describe la rama, no afirma qué equipo saldría para técnicos reales.

### C. Asignación global NSGA-II

Entrada ilustrativa: son las 07:00; dos técnicos compatibles empiezan jornada a las 08:00 y 12:00. Hay dos incidencias Alta (peso 4) y ambos técnicos tienen carga base 0.

- Asignar ambas al técnico que empieza a las 08:00 da espera ponderada `4×60 + 4×60 = 480` minutos ponderados y cargas `[2,0]`, con desequilibrio `(2−1)² + (0−1)² = 2`.
- Repartir una a cada uno da espera ponderada `4×60 + 4×300 = 1.440` y cargas `[1,1]`, con desequilibrio 0.

Ninguno domina al otro: el primer plan empieza antes, el segundo distribuye mejor la carga. Un frente de Pareto puede conservar ambos compromisos.

### D. Equipo NSGA-II a horario fijo

Entrada ilustrativa: Soporte propone atender una incidencia el martes a las 10:00. Dos equipos distintos cubren los requisitos y todos sus miembros pasan la validación de disponibilidad. Supóngase que el equipo A tiene `F=82` y carga media proyectada 1,5; el equipo B `F=75` y carga media 1.

```text
A: objetivos (100−82, 1,5) = (18, 1,5)
B: objetivos (100−75, 1)   = (25, 1)
```

A ofrece mayor puntuación, pero B menor carga media. Ninguno domina al otro. El sistema no decide una hora nueva: evalúa los equipos para las 10:00 elegidas por el usuario.

## 11. Relación con CRISP-DM

Esta organización describe el trabajo técnico verificable para la iteración. No implica entrenamiento de un modelo predictivo.

1. **Comprensión del negocio:** optimizar orden/cobertura de solicitudes y ofrecer compromisos entre espera y carga para incidencias; el usuario conserva decisiones.
2. **Comprensión de los datos:** revisar estados, prioridad, descripción, perfiles, capacidad, horario, ausencias, ubicación, carga y cronogramas; advertir que algunos requisitos se infieren con patrones de texto.
3. **Preparación de los datos:** filtrar solicitudes/estados elegibles, normalizar perfiles y fechas, derivar capacidades, horas de respaldo y candidatos compatibles.
4. **Modelado:** GA de permutación para orden de solicitudes; GA de equipos para etapas (con rama combinatoria si falta personal); NSGA-II de asignación global de incidencias; NSGA-II de equipos para una hora concreta.
5. **Evaluación:** pruebas focales aprobadas y pruebas de integración simuladas; suite combinada con un error de middleware de prueba. No hay evaluación estadística con historial productivo, ni garantías de óptimo global o reducción de tiempo.
6. **Integración en entorno de prueba:** las vistas y endpoints están conectados en el código y se ejecutaron pruebas Django locales sin usar datos reales. Esta revisión no verificó una instalación en producción ni una puesta en marcha productiva.

## 12. Capturas y diagramas para el capítulo

### Pantallas existentes que se pueden capturar

1. **Encargado de Sistemas → Optimización:** parámetros, solicitudes elegibles, botón de ejecución, curva de fitness y pestañas de alternativas. Conviene mostrar que el resultado es una recomendación y señalar la discrepancia de pesos en UI frente al cálculo operativo.
2. **Encargado de Sistemas → Incidencias → Optimización:** parámetros NSGA-II, casos abiertos, alternativas, espera y carga actual/proyectada.
3. **Soporte → Trabajo → inspección/instalación/retiro:** botón **GENERAR PROPUESTA**, modal de equipos y control de confirmación de horario.
4. **Soporte → Incidencias → atención:** fecha/hora aprobable, botón de propuesta, modal de equipos/líder y confirmación.
5. **Planta Técnica → Técnicos / Técnicos incidencias:** fichas que documentan el origen de los perfiles generales y los perfiles de capacidades de incidencias.

Capturar datos anonimizados o sintéticos. No presentar capturas de parámetros o recomendaciones como prueba de que una carga real se asignó o que el horario quedó reservado.

### Diagramas recomendados

- Diagrama de secuencia **pantalla → vista → filtro → servicio → resultado** para los cuatro recorridos.
- Diagrama de cromosoma: índice/CITE por gen, población, OX, mutación por intercambio y decodificación a equipo.
- Diagrama de Pareto de incidencias global: ejes `espera ponderada` y `desequilibrio de carga`; marcar que se minimizan ambos y diferenciar frentes.
- Diagrama del NSGA-II de equipo: filtros de elegibilidad → equipos de tamaño 2/3 → cobertura → objetivos `(100−fitness, carga media)` → selección de alternativa → aprobación.
- Diagrama de estados de confirmación: propuesta almacenada ≠ equipo aprobado ≠ incidencia/reserva confirmada.
- Diagrama de procedencia de datos que separe perfil operativo compartido, perfil de incidencias separado y datos derivados de solicitudes.

Los botones, las páginas, los modales y las funciones anteriores sí existen en el código. Los diagramas son material documental propuesto; no son pantallas ni gráficos de análisis que el sistema genere automáticamente.

## 13. Diferencias, pendientes y conclusiones

| Aspecto | Funcionamiento actual | Evidencia en el código | Limitación o pendiente | Qué puede afirmarse académicamente |
|---|---|---|---|---|
| GA de solicitudes | Ordena CITES con permutación, decodifica equipos y muestra hasta tres cromosomas. | `run_genetic_optimization()`, [`optimization_service.py:L2341-L2440`](../DATALAN/DATALAN/optimization_service.py#L2341); renderizado [`workflow.html:L60-L99`](../DATALAN/DATALAN/templates/workflow.html#L60). | La recomendación no se confirma desde esta pantalla y no se guarda como plan. | Se implementó un GA conectado a la interfaz que genera recomendaciones; no que asigne automáticamente. |
| Pesos del GA | Runtime con perfiles usa 25/20/15/15/25; pantalla/guía muestran 35/30/20/15. | [`optimization_service.py:L2290-L2320`](../DATALAN/DATALAN/optimization_service.py#L2290); [`workflow.html:L60-L62`](../DATALAN/DATALAN/templates/workflow.html#L60). | Inconsistencia visible/documental. | Citar la fórmula ejecutada según el modo; advertir que la pantalla aún enseña pesos distintos. |
| Propuesta genética de etapas | Botones para inspección, instalación y retiro eventual; generación normal usa GA de equipos. | [`support-work-modal.html:L100-L160`](../DATALAN/DATALAN/templates/support-work-modal.html#L100); [`optimization_service.py:L519-L730`](../DATALAN/DATALAN/optimization_service.py#L519). | Insuficiencia para instalación cambia a enumeración combinatoria; otras etapas fallan con personal insuficiente. | La función se llama GA y evoluciona equipos si hay dotación suficiente; no todos los casos recorren generaciones. |
| Capacidades de propuesta de etapa | Puntúa capacidades del grupo de la etapa. | `_team_profile_components()`, [`optimization_service.py:L405-L488`](../DATALAN/DATALAN/optimization_service.py#L405). | No valida capacidades inferidas de la descripción del trabajo ni acompañamiento de nivel CON_APOYO. | No afirmar cobertura dura de cada requisito del trabajo para estas propuestas. |
| NSGA-II global | Optimiza asignaciones abiertas con espera ponderada y carga. | [`optimization_service.py:L1388-L1610`](../DATALAN/DATALAN/optimization_service.py#L1388). | No modela duración/agenda; reevalúa incidencias con responsable; resultados mostrados pueden salir de frentes posteriores al primero. | Se generan planes multiobjetivo de referencia; no una reserva de calendario ni una asignación confirmada. |
| NSGA-II por horario | Propone equipo de atención de incidencia a hora fijada. | [`optimization_service.py:L1611-L2005`](../DATALAN/DATALAN/optimization_service.py#L1611); API [`views.py:L1910-L2024`](../DATALAN/DATALAN/views.py#L1910). | Endpoint de propuesta conectado solo a `attention`; no a `solution`; el inicio no equivale a reservar intervalo de duración real. | La fecha/hora es entrada fija y se comparan composición del equipo y carga. |
| Responsable original | En solicitud permanece en el campo base aunque la propuesta de etapa sea otro equipo; en incidencia la aprobación reemplaza el campo por el líder propuesto. | [`views.py:L2027-L2069`](../DATALAN/DATALAN/views.py#L2027), [`views.py:L680-L698`](../DATALAN/DATALAN/views.py#L680). | No hay regla uniforme que garantice conservarlo dentro del equipo hasta concluir. | Explicar la diferencia por tipo de flujo; no afirmar que todos los algoritmos lo preservan. |
| Disponibilidad y reserva | Se valida al generar propuestas, con alcances distintos; aprobación valida identidad/horario pero no vuelve a consultar disponibilidad. | [`optimization_service.py:L310-L404`](../DATALAN/DATALAN/optimization_service.py#L310); validación de confirmación indicada arriba. | No se ve control de concurrencia ni reserva atómica que evite dos aprobaciones del mismo intervalo. | Describir la validación observada; dejar la prevención de doble reserva como no verificada/pendiente. |
| Con apoyo | El NSGA-II de incidencias lo acepta como capacidad suficiente, y puntúa por debajo de SIN_APOYO. | [`optimization_service.py:L243-L253`](../DATALAN/DATALAN/optimization_service.py#L243); [`optimization_service.py:L1440-L1460`](../DATALAN/DATALAN/optimization_service.py#L1440). | No hay una restricción de compañero SIN_APOYO. | No afirmar que “Con apoyo” siempre implica asignación acompañada por especialista. |
| Pruebas | 12 pruebas focales ejecutadas y aprobadas; suite combinada 105/106 sin errores, una falla de middleware en prueba de fecha inválida. | Clases y métodos en la sección 9. | Sin prueba de navegador, DB productiva, concurrencia o validación temporal entre generación y confirmación. | Reportar pruebas y limitaciones tal como se ejecutaron; no garantizar funcionamiento al 100 %. |
| CRISP-DM / producción | Código conectado a pantallas y pruebas locales; PostgreSQL configurado en el proyecto. | [`settings.py:L74-L90`](../DATALAN/DATALAN/settings.py#L74), rutas y pruebas citadas. | Esta revisión no probó despliegue de producción ni resultados operacionales reales. | Presentar la Iteración 4 como implementación/evaluación en el entorno revisado, sin afirmar puesta en producción ni mejora medida. |

### Conclusión

DATALAN contiene dos familias de optimización genéticas conectadas a la interfaz: un GA permutacional que ordena solicitudes y un GA que propone equipos para etapas de solicitudes. También contiene dos usos de NSGA-II para incidencias: una asignación global multiobjetivo y una propuesta de equipo para la atención a horario fijado. El primero de cada familia entrega recomendaciones, no acciones operativas automáticas. Las propuestas por etapa/incidencia se guardan como propuestas y solo se vuelven asignaciones o aprobaciones mediante otro paso de confirmación.

La evidencia respalda la existencia y algunos comportamientos centrales mediante pruebas automatizadas, pero no respalda óptimo global, mejora real de tiempos, ausencia de dobles reservas, cobertura perfecta, persistencia del responsable inicial en todos los flujos ni despliegue productivo. La Iteración 4 debe reportar estas limitaciones y la diferencia entre lo que muestra la pantalla, lo que calcula el servicio y lo que confirman los tests.
