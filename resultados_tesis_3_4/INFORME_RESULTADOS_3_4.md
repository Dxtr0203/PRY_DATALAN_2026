# Informe de resultados de la propuesta — apartado 3.4

## 1. Alcance y fecha

El escenario previsto fue octubre de 2026. Las pruebas se ejecutaron el **9 de noviembre de 2026** en una base PostgreSQL aislada llamada `datalan_tesis_20261109_test`. No se cambió el reloj del equipo ni se forzaron estados para completar etapas. No se usaron datos personales ni contraseñas en este informe.

El escenario y todas las operaciones propuestas son simulados. Los nombres de clientes, usuarios, técnicos y enlaces son ficticios. Las referencias de origen se sustituyeron por identificadores `CLIENTE-PRUEBA-*`; por tanto, no se afirma que las solicitudes o fallas propuestas hayan ocurrido a los clientes usados como referencia. Las pruebas descritas aquí no modificaron la base productiva.

## 2. Datos preparados y alcance real

| Elemento | Preparado | Guardado/ejecutado |
|---|---:|---|
| Solicitudes propuestas, identificadas S01–S30 | 30 filas | Los primeros 30 intentos con fechas de octubre fueron bloqueados; en la actualización posterior se guardaron 30 como `REGISTRADA` en la base aislada |
| Incidencias propuestas, identificadas I01–I12 | 12 filas | Los 12 intentos iniciales fueron bloqueados; siguen sin incidencias persistidas porque no hay servicios de prueba instalados, concluidos y activos |
| Usuarios ficticios | 16 cuentas | 16 en la base aislada: 9 técnicos, 3 de Soporte y 4 perfiles de administración/coordinación/comercial |
| Perfiles técnicos de Planta Técnica | 9 | Preparados en la base aislada, con capacidades y disponibilidad ficticias |
| Algoritmos | 4 modalidades, 3 ejecuciones por modalidad | 12 ejecuciones sintéticas; configuraciones guardadas en la base aislada y salidas conservadas en JSON |
| Historial de asignación de incidencias | — | 3 registros en la base aislada |

El formulario de solicitud rechazó las fechas de instalación de octubre porque ya eran anteriores a la fecha real del sistema. En consecuencia, ninguna solicitud alcanzó revisión, factibilidad, decisión comercial, coordinación, asignación, inspección, instalación o conclusión. El formulario de incidencias exigió un servicio PP/MP instalado, concluido y activo. Como no se pudo crear ni concluir una solicitud de prueba, las 12 incidencias quedaron bloqueadas en ese requisito previo.

Los mensajes de validación llegaron en respuestas HTTP 200; esto significa que el formulario volvió a mostrarse con el error, no que la operación se guardara. La comprobación de base de datos registró cero solicitudes e incidencias.

## 3. Referencias y archivos de datos

Se conservaron los clientes como alias ficticios y se añadieron orígenes, destinos, enlaces, síntomas y datos de prueba sintéticos donde el escenario los requería. No se copiaron datos personales al paquete. Las filas fuente, sus identificadores S01–S30 e I01–I12, y las ubicaciones eventuales se pueden revisar en:

- [datos/solicitudes_30_prueba.csv](./datos/solicitudes_30_prueba.csv)
- [datos/incidencias_12_prueba.csv](./datos/incidencias_12_prueba.csv)
- [datos/usuarios_prueba.csv](./datos/usuarios_prueba.csv)
- [datos/tecnicos_prueba.csv](./datos/tecnicos_prueba.csv)

Las 30 filas de solicitudes comprenden 20 PP permanentes, 6 PP eventuales y 4 propuestas multipunto. Las seis eventuales conservan el destino **UNIDAD MÓVIL** y las ubicaciones ficticias de La Paz. Las 12 incidencias comprenden 10 PP y 2 propuestas multipunto.

### Comprobación de MP y PM

El formulario ofrece los tipos “Instalación Punto a Punto”, “Instalación Punto Multipunto” e “Instalación Eventual”; no ofrece opciones literales `MP` o `PM`. Se enviaron además cuatro pruebas de etiqueta sin guardar datos: `MP` (S21 y S22) y `PM` (S23 y S24). En ambos casos el sistema respondió “Selecciona un tipo de solicitud válido.” Por ello **no se equiparó PM con MP**. En los intentos de registro por el formulario, las cuatro filas propuestas como multipunto se presentaron usando la opción visible “Instalación Punto Multipunto”; esa conversión no demuestra que las etiquetas fuente MP y PM sean equivalentes en el modelo del sistema.

Evidencia: [evidencias/validacion_etiquetas_mp_pm.json](./evidencias/validacion_etiquetas_mp_pm.json).

## 4. Resultados de las solicitudes S01–S30

**Resultado esperado** en los casos ordinarios: el registro debía permitir recorrer las etapas existentes hasta la conclusión. En S04 y S13 se propuso observar una factibilidad desfavorable; en S08 y S19 se propuso comprobar observación y eventual subsanación, solo si el sistema la permite. Para las eventuales se esperaba además el período de servicio y el retiro antes de la conclusión final. Estos resultados esperados no implican que las etapas se hayan ejecutado.

**Resultado obtenido en todos los intentos:** bloqueo antes de guardar, con el mensaje de que la fecha de instalación debía ser igual o posterior a la fecha actual. “Flujo pendiente” significa que las etapas posteriores no se ejecutaron.

| ID | Cliente de prueba | Origen → destino de prueba | Modalidad / resultado esperado particular | Resultado obtenido |
|---|---|---|---|---|
| S01 | CLIENTE-PRUEBA-F4 | SEDE SINTÉTICA F4 → SEDE DESTINO SINTÉTICA F4 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S02 | CLIENTE-PRUEBA-F8 | SEDE SINTÉTICA F8 → SEDE DESTINO SINTÉTICA F8 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S03 | CLIENTE-PRUEBA-F11 | SEDE SINTÉTICA F11 → SEDE DESTINO SINTÉTICA F11 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S04 | CLIENTE-PRUEBA-F14 | SEDE SINTÉTICA F14 → SEDE DESTINO SINTÉTICA F14 | PP permanente; proponer factibilidad desfavorable | Bloqueada antes de evaluar factibilidad |
| S05 | CLIENTE-PRUEBA-F19 | SEDE SINTÉTICA F19 → SEDE DESTINO SINTÉTICA F19 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S06 | CLIENTE-PRUEBA-F21 | SEDE SINTÉTICA F21 → SEDE DESTINO SINTÉTICA F21 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S07 | CLIENTE-PRUEBA-F28 | SEDE SINTÉTICA F28 → SEDE DESTINO SINTÉTICA F28 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S08 | CLIENTE-PRUEBA-F58 | SEDE SINTÉTICA F58 → SEDE DESTINO SINTÉTICA F58 | PP permanente; observación y subsanación si existe | Bloqueada antes de revisión; subsanación no probada |
| S09 | CLIENTE-PRUEBA-F71 | SEDE SINTÉTICA F71 → SEDE DESTINO SINTÉTICA F71 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S10 | CLIENTE-PRUEBA-F74 | SEDE SINTÉTICA F74 → SEDE DESTINO SINTÉTICA F74 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S11 | CLIENTE-PRUEBA-F77 | SEDE SINTÉTICA F77 → SEDE DESTINO SINTÉTICA F77 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S12 | CLIENTE-PRUEBA-F81 | SEDE SINTÉTICA F81 → SEDE DESTINO SINTÉTICA F81 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S13 | CLIENTE-PRUEBA-F86 | SEDE SINTÉTICA F86 → SEDE DESTINO SINTÉTICA F86 | PP permanente; proponer factibilidad desfavorable | Bloqueada antes de evaluar factibilidad |
| S14 | CLIENTE-PRUEBA-F87 | SEDE SINTÉTICA F87 → SEDE DESTINO SINTÉTICA F87 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S15 | CLIENTE-PRUEBA-F88 | SEDE SINTÉTICA F88 → SEDE DESTINO SINTÉTICA F88 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S16 | CLIENTE-PRUEBA-F89 | SEDE SINTÉTICA F89 → SEDE DESTINO SINTÉTICA F89 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S17 | CLIENTE-PRUEBA-F1019 | SEDE SINTÉTICA F1019 → SEDE DESTINO SINTÉTICA F1019 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S18 | CLIENTE-PRUEBA-F1024 | SEDE SINTÉTICA F1024 → SEDE DESTINO SINTÉTICA F1024 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S19 | CLIENTE-PRUEBA-F1030 | SEDE SINTÉTICA F1030 → SEDE DESTINO SINTÉTICA F1030 | PP permanente; observación y subsanación si existe | Bloqueada antes de revisión; subsanación no probada |
| S20 | CLIENTE-PRUEBA-F1063 | SEDE SINTÉTICA F1063 → SEDE DESTINO SINTÉTICA F1063 | PP permanente; recorrido ordinario | Bloqueada al registrar; flujo pendiente |
| S21 | CLIENTE-PRUEBA-F27 | SEDE SINTÉTICA F27 → SEDE DESTINO SINTÉTICA F27 | Permanente; etiqueta fuente MP, topología pendiente de validar | Bloqueada por fecha; equivalencia de etiqueta no validada |
| S22 | CLIENTE-PRUEBA-F29 | SEDE SINTÉTICA F29 → SEDE DESTINO SINTÉTICA F29 | Permanente; etiqueta fuente MP, topología pendiente de validar | Bloqueada por fecha; equivalencia de etiqueta no validada |
| S23 | CLIENTE-PRUEBA-F283 | SEDE SINTÉTICA F283 → SEDE DESTINO SINTÉTICA F283 | Permanente; etiqueta fuente PM, topología pendiente de validar | Bloqueada por fecha; equivalencia de etiqueta no validada |
| S24 | CLIENTE-PRUEBA-F365 | SEDE SINTÉTICA F365 → SEDE DESTINO SINTÉTICA F365 | Permanente; etiqueta fuente PM, topología pendiente de validar | Bloqueada por fecha; equivalencia de etiqueta no validada |
| S25 | CLIENTE-PRUEBA-F11 | SEDE SINTÉTICA F11 → UNIDAD MÓVIL — Avenida Camacho — La Paz (ficticio) | PP eventual; servicio 20–26 oct.; retiro y conclusión | Bloqueada por fecha; servicio y retiro no ejecutados |
| S26 | CLIENTE-PRUEBA-F1056 | SEDE SINTÉTICA F1056 → UNIDAD MÓVIL — Calle Comercio — La Paz (ficticio) | PP eventual; servicio 21–27 oct.; retiro y conclusión | Bloqueada por fecha; servicio y retiro no ejecutados |
| S27 | CLIENTE-PRUEBA-F11 | SEDE SINTÉTICA F11 → UNIDAD MÓVIL — Plaza del Estudiante — La Paz (ficticio) | PP eventual; servicio 21–28 oct.; retiro y conclusión | Bloqueada por fecha; servicio y retiro no ejecutados |
| S28 | CLIENTE-PRUEBA-F1056 | SEDE SINTÉTICA F1056 → UNIDAD MÓVIL — Avenida Arce — La Paz (ficticio) | PP eventual; servicio 22–29 oct.; retiro y conclusión | Bloqueada por fecha; servicio y retiro no ejecutados |
| S29 | CLIENTE-PRUEBA-F11 | SEDE SINTÉTICA F11 → UNIDAD MÓVIL — Calle 21 de Calacoto — La Paz (ficticio) | PP eventual; servicio 23–30 oct.; retiro y conclusión | Bloqueada por fecha; servicio y retiro no ejecutados |
| S30 | CLIENTE-PRUEBA-F1056 | SEDE SINTÉTICA F1056 → UNIDAD MÓVIL — Avenida Saavedra, Miraflores — La Paz (ficticio) | PP eventual; servicio 24–26 oct.; retiro y conclusión | Bloqueada por fecha; servicio y retiro no ejecutados |

Detalle de los 30 mensajes y verificación de persistencia: [evidencias/intentos_registro_solicitudes.json](./evidencias/intentos_registro_solicitudes.json).

## 5. Resultados de las incidencias I01–I12

**Resultado esperado:** registrar el síntoma ficticio y recorrer evaluación, prioridad, asignación de responsable/equipo, programación, atención, resolución y cierre, en la medida en que el sistema lo permita. **Resultado obtenido en los 12 intentos:** el sistema exigió que el servicio PP/MP ya estuviera instalado y concluido, con conclusión aprobada y activo. No había servicios de prueba que cumplieran esa condición; el formulario rechazó cada intento y no se guardó incidencia.

| ID | Enlace ficticio | Tipo propuesto | Síntoma / prioridad propuesta | Resultado obtenido |
|---|---|---|---|---|
| I01 | ENLACE-PRUEBA-F4 | PP | Pérdida total de conectividad / alta | Bloqueada por falta de servicio activo instalado y concluido |
| I02 | ENLACE-PRUEBA-F8 | PP | Degradación intermitente / media | Bloqueada por falta de servicio activo instalado y concluido |
| I03 | ENLACE-PRUEBA-F14 | PP | Potencia óptica fuera del umbral de prueba / baja | Bloqueada por falta de servicio activo instalado y concluido |
| I04 | ENLACE-PRUEBA-F28 | PP | Intermitencia de enlace / alta; se propuso revisar reapertura | Bloqueada; no se alcanzó resolución ni se probó reapertura |
| I05 | ENLACE-PRUEBA-F58 | PP | Pérdida parcial de paquetes / media | Bloqueada por falta de servicio activo instalado y concluido |
| I06 | ENLACE-PRUEBA-F71 | PP | Sin conectividad en extremo destino / baja | Bloqueada por falta de servicio activo instalado y concluido |
| I07 | ENLACE-PRUEBA-F77 | PP | Latencia elevada / alta | Bloqueada por falta de servicio activo instalado y concluido |
| I08 | ENLACE-PRUEBA-F81 | PP | Inestabilidad de enlace / media; reasignación/escalamiento propuesto | Bloqueada; no se alcanzó asignación ni se probó reasignación |
| I09 | ENLACE-PRUEBA-F1024 | PP | Interrupción de servicio / baja | Bloqueada por falta de servicio activo instalado y concluido |
| I10 | ENLACE-PRUEBA-F1030 | PP | Degradación de transferencia / alta | Bloqueada por falta de servicio activo instalado y concluido |
| I11 | ENLACE-PRUEBA-F283 | PM, multipunto por validar | Afectación de un extremo multipunto / media | Bloqueada por falta de servicio activo; PM no equiparado a MP |
| I12 | ENLACE-PRUEBA-F365 | PM, multipunto por validar | Intermitencia multipunto / baja | Bloqueada por falta de servicio activo; PM no equiparado a MP |

La prioridad/severidad de la tabla es la propuesta de los datos de prueba; no se registró ni se evaluó dentro del flujo operativo. La pantalla de reporte examinada no ofreció una entrada de severidad que se guardara con el reporte. Tampoco se verificaron resolución, cierre, reapertura o reasignación en una incidencia persistida.

Evidencia: [evidencias/validaciones_y_permisos.json](./evidencias/validaciones_y_permisos.json).

## 6. Recorridos representativos

### S01 — PP permanente

- **Esperado:** registrar S01 y continuar revisión, factibilidad, decisión comercial, coordinación, asignación, inspección, instalación y conclusión.
- **Ejecutado:** se envió como solicitud PP permanente de `CLIENTE-PRUEBA-F4`, con origen y destino ficticios de la fila S01 y fecha de escenario 1 de octubre de 2026.
- **Obtenido:** el validador mostró “La fecha de instalación debe ser igual o posterior a la fecha actual.” El registro no se persistió. Ninguna etapa posterior comenzó.
- **Estado:** bloqueada. Evidencia por intento: `intentos_registro_solicitudes.json`; pantalla real del formulario en `capturas/formulario_solicitud_prueba.png`.

### S25 — PP eventual con retiro

- **Esperado:** registro, inspección e instalación, período de servicio del 20 al 26 de octubre, retiro y conclusión.
- **Ejecutado:** se conservó como destino `UNIDAD MÓVIL — Avenida Camacho — La Paz (ficticio)`, con fechas ficticias de la fila S25.
- **Obtenido:** la misma validación de fecha impidió guardar el registro. No se creó el período de servicio ni se ejecutaron retiro o conclusión. No se alteró artificialmente el estado.
- **Estado:** bloqueada. No existe captura de aprobación de retiro; queda pendiente: **(Insertar captura real de la aprobación del retiro de la solicitud eventual S25; pendiente de obtener).**

### S21 — propuesta multipunto

- **Esperado:** comprobar el tratamiento del servicio etiquetado MP y, si el tipo correspondía, continuar el flujo permanente multipunto.
- **Ejecutado:** el intento con la opción visible “Instalación Punto Multipunto” se bloqueó por la fecha histórica. En pruebas independientes, enviar `MP` literalmente como tipo fue rechazado como valor inválido. El formulario tampoco presentó una opción literal `PM`.
- **Obtenido:** no se creó S21 ni se confirmó la semántica de MP/PM. Las recomendaciones sintéticas de equipos son independientes de un registro operativo guardado.
- **Estado:** bloqueada / semántica pendiente. Evidencia: `validacion_etiquetas_mp_pm.json` e `intentos_registro_solicitudes.json`.

### I01 — incidencia PP

- **Esperado:** reporte, evaluación, prioridad, asignación, programación, atención, resolución y cierre para `ENLACE-PRUEBA-F4`.
- **Ejecutado:** se intentó reportar el síntoma ficticio en el rol de Soporte.
- **Obtenido:** el selector no tenía un enlace de prueba elegible y el servidor indicó que solo se aceptaban servicios PP/MP con instalación y conclusión aprobadas. No se guardó incidencia ni se alcanzaron pasos posteriores.
- **Estado:** bloqueada. Capturas auténticas del área de Soporte y del selector sin servicios disponibles en la carpeta `capturas`.

## 7. Usuarios, permisos y disponibilidad

Se prepararon 16 cuentas ficticias con roles `admin`, `comercial`, `planta_encargado`, `sistemas_encargado`, `tecnico` y `soporte_sistemas`. Las nueve cuentas técnicas se asociaron a perfiles de Planta Técnica con horarios de prueba, capacidades y registros de disponibilidad en [datos/tecnicos_prueba.csv](./datos/tecnicos_prueba.csv). Se crearon tres usuarios ficticios de Soporte. El archivo [datos/usuarios_prueba.csv](./datos/usuarios_prueba.csv) contiene identificadores, nombres y correos reservados para pruebas; no contiene contraseñas.

Se comprobó que un usuario con rol técnico no podía abrir la ruta de nueva solicitud comercial ni el área de incidencias de sistemas: ambos intentos redirigieron (HTTP 302). **Resultado esperado:** denegar acceso a funciones ajenas al rol. **Resultado obtenido:** denegación en ambas rutas. Evidencia: `validaciones_y_permisos.json`.

Para escenarios algorítmicos se modelaron una ausencia ficticia del Técnico de Prueba 08 durante el 1 de octubre–1 de noviembre de 2026, con su perfil marcado disponible, y ocupación sintética de los Técnicos 01 y 02 entre las 10:00 y 12:00 del 2 de octubre. Las recomendaciones de equipos excluyeron esos perfiles en los escenarios pertinentes. En cambio, la modalidad de asignación de solicitudes incluyó al técnico ausente en todas las alternativas observadas. En asignación de incidencias se encontraron asignaciones en una misma hora. No se verificó un caso de cero candidatos/capacidad ni la disponibilidad real de turnos desde un flujo confirmado.

La modificación de disponibilidad entre obtener una recomendación y confirmarla **no se pudo ejecutar** porque ninguna solicitud o incidencia llegó a esa pantalla de trabajo. Por tanto, no se afirma que el sistema revalide o ignore los cambios en ese momento.

## 8. Ejecuciones de algoritmos

Las cuatro modalidades se ejecutaron tres veces, con entradas y horarios sintéticos de octubre, directamente a través de los servicios del sistema. Estas pruebas no fueron transiciones de un flujo web con solicitudes o incidencias persistidas. Los valores son tiempos de cálculo de la recomendación, no tiempos de atención ni de reparación. Las configuraciones, alternativas y salidas detalladas están en [evidencias/resultados_algoritmos.json](./evidencias/resultados_algoritmos.json).

### 8.1 Organización y asignación de solicitudes

| Ejecución | Casos / candidatos | Configuración (población, generaciones, mutación, cruce) | Tiempo (ms) | Mejor alternativa: puntuación / cobertura | Observación |
|---:|---|---|---:|---|---|
| 1 | 30 / 9 | 40, 100, 10%, 80% — semilla 701 | 41 163,729 | 71,84 / 100% | 3 alternativas incluyeron al técnico ausente |
| 2 | 30 / 9 | 40, 100, 10%, 80% — semilla 702 | 40 096,397 | 71,84 / 100% | 3 alternativas incluyeron al técnico ausente |
| 3 | 30 / 9 | 40, 100, 10%, 80% — semilla 703 | 31 904,909 | 71,84 / 100% | 3 alternativas incluyeron al técnico ausente |

**Resultado:** fallida respecto a la comprobación de disponibilidad. La cobertura y puntuación no compensan que se recomiende a un técnico ausente. La función no aplicó esa ausencia al construir las alternativas examinadas.

### 8.2 Recomendación de equipos para solicitudes

Las tres ejecuciones usaron S01, etapa de instalación, 2 de octubre a las 10:00, seis candidatos compatibles y ocupación sintética de los Técnicos 01 y 02. La configuración fue población 40, 100 generaciones, mutación 10%, cruce 80%; las semillas fueron 801, 802 y 803.

| Ejecución | Tiempo (ms) | Puntuación de la mejor alternativa | Equipo recomendado |
|---:|---:|---:|---|
| 1 | 783,011 | 90,47 | Técnicos 03, 05, 06 y 07 |
| 2 | 835,116 | 90,47 | Técnicos 03, 05, 06 y 07 |
| 3 | 922,686 | 90,47 | Técnicos 03, 05, 06 y 07 |

**Resultado:** aprobada para el criterio acotado de excluir en este escenario al técnico ausente y a los dos ocupados, y sugerir un equipo con capacidades compatibles. No prueba asignación operacional ni ausencia de conflictos en otros escenarios.

### 8.3 Asignación de incidencias

Las tres ejecuciones usaron 12 incidencias y 9 candidatos, con población 48, 80 generaciones, mutación 15%, cruce 85%, semillas 901–903 y hora base sintética 1 de octubre a las 08:00. Cada ejecución devolvió tres alternativas; la evidencia registró tamaño de conjunto Pareto de 48.

| Ejecución | Tiempo (ms) | Espera ponderada (h), primera alternativa | Desequilibrio de carga | Asignaciones en mismo horario |
|---:|---:|---:|---:|---:|
| 1 | 246,598 | 0,0 | 6,0 | 5 |
| 2 | 249,829 | 0,0 | 6,0 | 5 |
| 3 | 257,718 | 0,0 | 6,0 | 5 |

**Resultado:** fallida para el criterio de evitar solapamientos. Se observaron cinco asignaciones a la misma hora en la primera alternativa de cada ejecución. El conjunto de datos no aportó duración de cada atención, por lo que la coincidencia horaria es evidencia de riesgo de conflicto, no medición de duración o de un solapamiento temporal confirmado.

### 8.4 Recomendación de equipos para incidencias

Las ejecuciones usaron I01, 2 de octubre a las 10:30, ocupación de los Técnicos 01 y 02 hasta las 12:00 y seis candidatos compatibles. Se usaron población 48, 80 generaciones, mutación 15%, cruce 85% y semillas 1001–1003.

| Ejecución | Tiempo (ms) | Puntuación de la mejor alternativa | Equipo recomendado |
|---:|---:|---:|---|
| 1 | 403,733 | 85,60 | Técnicos 03, 06 y 07 |
| 2 | 391,743 | 85,60 | Técnicos 03, 06 y 07 |
| 3 | 367,779 | 85,60 | Técnicos 03, 06 y 07 |

**Resultado:** aprobada para el criterio acotado de recomendar un equipo entre los seis perfiles compatibles, excluyendo en esta configuración a los dos ocupados y al ausente. No demuestra una atención real, ni que una asignación se confirmara.

## 9. Relación con prácticas de ITIL 4

La revisión se relacionó de manera orientativa con **gestión de solicitudes de servicio** y **gestión de incidentes** de ITIL 4. La primera práctica busca gestionar solicitudes de servicio acordadas; la segunda, restaurar el servicio normal tan pronto como sea posible y reducir el impacto de incidentes. En DATALAN se observaron validaciones de fecha y dependencia de un servicio instalado para permitir el reporte de incidencias, además de separación de acceso por rol.

Las etapas de evaluación, factibilidad, decisión comercial, coordinación, inspección, instalación, retiro o cierre descritas aquí son etapas propias del flujo de DATALAN y de este escenario; no se presentan como una secuencia obligatoria de ITIL 4. Debido a que los recorridos quedaron bloqueados, esta prueba no demuestra el desempeño integral de esas prácticas ni una certificación ITIL.

## 10. Pendientes, limitaciones y evidencia visual

- No se pudieron completar solicitudes ni incidencias debido a las condiciones reales de fecha y de servicio activo; no se forzó el reloj ni el estado de datos para sortearlas.
- Factibilidad negativa, observaciones y su eventual subsanación, horarios ocupados en una asignación confirmada, falta total de personal/capacidad, instalación, conclusión, período eventual, retiro, atención, resolución, cierre y reapertura quedaron sin ejecutar en el flujo web.
- La severidad propuesta en el CSV no se registró en el flujo de incidencia examinado.
- No se probó qué ocurre si cambia la disponibilidad entre recomendación y confirmación.
- Las recomendaciones algorítmicas son ejecuciones sintéticas de servicios; sus puntuaciones y tiempos no prueban una mejora de la atención real de la empresa.
- Se conservaron capturas auténticas del inicio comercial, formulario de solicitud y pantalla/selector de incidencias. No hay capturas de etapas de aprobación, instalación, resolución o retiro porque esas etapas no se alcanzaron.
- Se ejecutó `manage.py check` sin errores y pasaron 144 pruebas automatizadas existentes de flujos, técnicos y algoritmos. Esas pruebas del proyecto no sustituyen los recorridos operacionales pendientes de esta propuesta.

Capturas disponibles:

- [capturas/inicio_comercial_prueba.png](./capturas/inicio_comercial_prueba.png)
- [capturas/formulario_solicitud_prueba.png](./capturas/formulario_solicitud_prueba.png)
- [capturas/incidencias_soporte_sin_registros.png](./capturas/incidencias_soporte_sin_registros.png)
- [capturas/selector_incidencia_pp_mp.png](./capturas/selector_incidencia_pp_mp.png)

## 11. Resumen de estados de prueba

Las cantidades siguientes cuentan comprobaciones ejecutadas y recorridos completos por separado. Un bloqueo no equivale a aprobación; una operación preparada no equivale a prueba ejecutada.

| Grupo de comprobaciones | Aprobadas | Fallidas | Bloqueadas | Sin ejecutar |
|---|---:|---:|---:|---:|
| Intentos individuales de registro de solicitudes S01–S30 | 0 | 0 | 30 | — |
| Intentos individuales de reporte de incidencias I01–I12 | 0 | 0 | 12 | — |
| Validación de etiquetas literales MP/PM | 4 | 0 | 0 | — |
| Acceso de rol técnico a dos rutas restringidas | 2 | 0 | 0 | — |
| Ejecuciones de algoritmos: equipos de solicitudes e incidencias | 6 | 0 | 0 | — |
| Ejecuciones de algoritmos: asignación de solicitudes e incidencias | 0 | 6 | 0 | — |
| Recorridos completos de solicitudes (30 casos) | 0 | 0 | 30 bloqueados al inicio | 0 completados |
| Recorridos completos de incidencias (12 casos) | 0 | 0 | 12 bloqueados al inicio | 0 completados |

Las cuatro validaciones MP/PM se consideran aprobadas únicamente como comprobaciones de rechazo de etiquetas no válidas; no como solicitudes aceptadas. Las seis recomendaciones de equipos pasaron solo los criterios de compatibilidad/disponibilidad del escenario sintético. Se verificó la persistencia de configuración algorítmica y tres entradas de historial en la base aislada; no se persistieron las 42 operaciones propuestas.

## 12. Actualización posterior: solicitudes visibles en el sistema de pruebas

Después de la primera ejecución y con autorización para reprogramar el escenario, se registraron nuevamente las 30 solicitudes en la **misma base aislada**. Para cumplir la validación real de fecha sin alterar el reloj, cada fecha del escenario original se desplazó **40 días**: la primera fecha pasó del 1 de octubre al **10 de noviembre de 2026**. Las fechas relativas y la duración eventual se conservaron. Los archivos originales de octubre permanecen intactos; las fechas usadas en esta carga se encuentran en [datos/solicitudes_30_prueba_escenario_futuro.csv](./datos/solicitudes_30_prueba_escenario_futuro.csv) y [datos/incidencias_12_prueba_escenario_futuro.csv](./datos/incidencias_12_prueba_escenario_futuro.csv).

**Resultado obtenido:** los 30 envíos pasaron por el formulario comercial de DATALAN y quedaron guardados con estado inicial `REGISTRADA`, CITE `01-26` a `30-26`. No se derivaron ni se avanzaron a factibilidad, decisiones, asignaciones, inspecciones, instalación o conclusión. La pantalla real de solicitudes pendientes mostró los 30 clientes ficticios. El JSON [evidencias/registro_solicitudes_escenario_futuro.json](./evidencias/registro_solicitudes_escenario_futuro.json) registra la fecha real de ejecución, el desplazamiento, la correspondencia S01–S30/CITE y la verificación de persistencia.

Las 6 solicitudes eventuales conservan `UNIDAD MÓVIL` y cada ubicación ficticia de La Paz; sus períodos también se desplazaron 40 días. Para las cuatro filas de origen MP/PM se seleccionó en el formulario el tipo visible “Instalación Punto Multipunto” porque el sistema no acepta literalmente MP ni PM. El dato fuente y la aclaración de equivalencia pendiente quedaron anotados en el detalle de prueba. Esto permitió guardar las solicitudes de prueba, pero **no confirma** que MP y PM sean sinónimos ni que la topología de origen corresponda al tipo elegido.

**Incidencias:** se registraron **0 de 12**. No se repitieron los envíos del formulario de incidencias en esta actualización; los 12 envíos ejecutados durante la primera vuelta habían sido bloqueados. Para la carga futura las fechas se prepararon con el mismo desplazamiento, pero las propuestas quedaron **sin ejecutar** porque el sistema exige un servicio PP/MP instalado y concluido, con conclusión aprobada y activo. Las 30 solicitudes continúan en `REGISTRADA`, así que no cumplen ese requisito. No se crearon enlaces ni estados de instalación/conclusión ficticios para hacer aparecer incidencias operativas.

| Estado actual de los casos | Cantidad |
|---|---:|
| Solicitudes guardadas y visibles en DATALAN de pruebas, estado `REGISTRADA` | 30 |
| Solicitudes que alcanzaron el recorrido completo | 0 |
| Incidencias guardadas | 0 |
| Propuestas de incidencia futuras sin ejecutar, a la espera del servicio requerido | 12 |

La vista `/comercial/pendientes/` devolvió 30 tarjetas con CITE distintos y se confirmó la correspondencia de los 30 casos S01–S30. Evidencia de la página servida: [evidencias/visibilidad_solicitudes_sistema.json](./evidencias/visibilidad_solicitudes_sistema.json). También se obtuvo una captura visual real de las tarjetas en la página compartida de esta conversación. Las fechas y el estado de cada fila están en el CSV de escenario futuro.

El resumen de la sección 11 corresponde a la primera ejecución con fechas de octubre. Para el estado posterior de los datos, prevalece esta actualización: hay 30 solicitudes ficticias guardadas en el entorno aislado y ninguna incidencia guardada. La pantalla de solicitudes pendientes se dejó abierta en la sesión compartida del sistema de pruebas; la evidencia JSON permite volver a consultar los identificadores y sus CITE.

## 13. Carga autorizada en la base productiva

Posteriormente, el usuario autorizó expresamente cargar los casos en el sistema productivo. Antes de escribir se comprobó que la base PostgreSQL `datalan` (esquema `datalan`) contenía 0 solicitudes, 0 incidencias y 0 clientes `CLIENTE-PRUEBA-*`; por ello no se reemplazaron registros previos. Se guardaron **30 solicitudes ficticias** mediante la capa de persistencia de DATALAN, asociadas al único perfil comercial activo encontrado. La relación de usuario fue necesaria por el esquema; no se usó su contraseña y el historial de cada solicitud identifica la acción como carga autorizada, no como una sesión autenticada de ese trabajador. Se verificó una lectura posterior de los 30 registros y todos quedaron en estado `REGISTRADA`, con CITE `01-26` a `30-26`. No se derivaron ni se modificaron sus aprobaciones.

Las fechas de octubre se desplazaron 40 días, sin cambiar el reloj: las solicitudes permanentes comienzan entre el 10 y el 25 de noviembre de 2026; las seis eventuales conservan sus períodos relativos y las ubicaciones ficticias de La Paz, ahora entre el 29 de noviembre y el 9 de diciembre. El puerto LC se completó como dato ficticio requerido por el sistema. Las etiquetas MP/PM se documentaron en los requisitos; para las cuatro propuestas multipunto se usó el tipo disponible en DATALAN, sin afirmar equivalencia semántica entre las etiquetas fuente.

La vista comercial real `/comercial/pendientes/` generó 30 tarjetas con CITE distintos al consultar la base productiva. Las seis tarjetas eventuales mostraron además los destinos y períodos ficticios reprogramados. El servidor local compartido se conectó a `datalan` en `127.0.0.1:8011`; se requiere iniciar sesión con una cuenta comercial válida del sistema. Evidencia: [evidencias/registro_solicitudes_produccion.json](./evidencias/registro_solicitudes_produccion.json), [evidencias/visibilidad_solicitudes_produccion.json](./evidencias/visibilidad_solicitudes_produccion.json) y el CSV con los CITE persistidos [datos/solicitudes_30_produccion.csv](./datos/solicitudes_30_produccion.csv).

**No se crearon incidencias en producción.** Siguen siendo 0 porque el sistema requiere servicios PP/MP instalados, concluidos y con aprobación, mientras las 30 solicitudes nuevas están solo en estado `REGISTRADA`. Tampoco se alteró ningún registro existente ni se marcaron trabajos como completados para saltar ese requisito.

## 14. Retiro de la carga productiva

El usuario informó que las solicitudes estaban mal completadas y pidió retirar todas las que se habían cargado. El 9 de noviembre de 2026 se identificaron por los CITE `01-26`–`30-26`, el estado `REGISTRADA`, los nombres `CLIENTE-PRUEBA-*` y las marcas de caso de prueba. Se eliminaron **solo esas 30 solicitudes**. También se eliminaron los 25 registros de cliente ficticio creados exclusivamente por esa carga, después de comprobar que ya no tenían solicitudes asociadas. Las dependencias relacionadas se eliminaron por las reglas `ON DELETE CASCADE` del esquema.

La eliminación se ejecutó en una transacción y se verificó después en la base `datalan`: quedaron 0 solicitudes, 0 de esos clientes ficticios y 0 incidencias; no se modificaron registros ajenos. La vista comercial de pendientes respondió y mostró 0 tarjetas. Evidencias: [evidencias/eliminacion_solicitudes_produccion.json](./evidencias/eliminacion_solicitudes_produccion.json) y [evidencias/verificacion_posterior_eliminacion.json](./evidencias/verificacion_posterior_eliminacion.json).

La carga autorizada y luego retirada queda documentada para mantener trazabilidad; el CSV de CITE productivos y las capturas anteriores son evidencia histórica, no registros que sigan presentes en el sistema.
