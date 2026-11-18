# Guía de capturas pendientes — Iteración 5

No se completaron recorridos funcionales con navegador y no hay capturas de etapas que puedan presentarse como realizadas. La página de login abierta en el servidor aislado no demuestra un recorrido. Esta guía indica qué capturar cuando se ejecuten los casos en un entorno de pruebas con los datos ficticios.

## Solicitud permanente — `CITE-IT5-PER-001`

| Orden | Rol | Pantalla/acción | Resultado que se debe comprobar | Captura a guardar |
|---|---|---|---|---|
| 1 | Comercial | Solicitudes → Nueva solicitud; registrar servicio permanente y puntos del enlace | CITE generada, solicitante y datos obligatorios visibles | `PER-01-comercial-registro.png` |
| 2 | Comercial | Abrir la solicitud y remitir a evaluación | Estado remitido y antecedente en historial | `PER-02-comercial-remision.png` |
| 3 | Encargado de Planta Técnica | Solicitudes pendientes → registrar evaluación de factibilidad | Evaluación guardada en la solicitud | `PER-03-planta-evaluacion.png` |
| 4 | Encargado de Sistemas | Solicitudes pendientes → registrar evaluación de Sistemas | Evaluación guardada y visible | `PER-04-sistemas-evaluacion.png` |
| 5 | Comercial | Revisar las dos evaluaciones y aprobar | Decisión aprobada y registro de decisión | `PER-05-comercial-aprobacion.png` |
| 6 | Sistemas | Asignación operativa → asignar Soporte | Responsable de Soporte visible en la misma CITE | `PER-06-sistemas-asignacion.png` |
| 7 | Soporte | Solicitudes → asignar técnico responsable | Técnico asignado visible | `PER-07-soporte-tecnico.png` |
| 8 | Técnico y Soporte | Enviar cronograma tentativo de inspección; Soporte confirma horario/equipo | Horario y equipo confirmados | `PER-08-inspeccion-programada.png` |
| 9 | Técnico | Registrar inspección realizada | Resultado de inspección visible | `PER-09-inspeccion-realizada.png` |
| 10 | Técnico y Soporte | Proponer cronograma de instalación y aprobarlo | Horario/equipo aprobados | `PER-10-instalacion-programada.png` |
| 11 | Técnico | Registrar instalación realizada | Resultado de instalación visible | `PER-11-instalacion-realizada.png` |
| 12 | Técnico y Soporte | Enviar conclusión; Soporte la revisa y aprueba | Conclusión aprobada y estado final mostrado | `PER-12-conclusion-aprobada.png` |
| 13 | Soporte o lectura autorizada | Volver a consultar la misma CITE | Conclusión, asignaciones e historial persisten | `PER-13-reconsulta-persistencia.png` |

## Solicitud eventual — `CITE-IT5-EVE-001`

| Orden | Rol | Pantalla/acción | Resultado que se debe comprobar | Captura a guardar |
|---|---|---|---|---|
| 1 | Comercial | Nueva solicitud eventual; ingresar inicio y finalización | Período visible asociado a la CITE | `EVE-01-periodo-registrado.png` |
| 2 | Comercial, Planta Técnica, Sistemas | Remitir, evaluar en ambas áreas y aprobar comercialmente | Antecedentes y decisiones visibles | `EVE-02-evaluaciones-aprobacion.png` |
| 3 | Sistemas y Soporte | Asignar responsables | Personal asignado visible | `EVE-03-responsables.png` |
| 4 | Técnico y Soporte | Programar/aprobar inspección; registrar su resultado | Inspección aprobada y realizada | `EVE-04-inspeccion.png` |
| 5 | Técnico y Soporte | Programar/aprobar instalación; registrar su resultado | Instalación aprobada y realizada | `EVE-05-instalacion.png` |
| 6 | Técnico y Soporte | Programar y aprobar retiro después de la fecha eventual final | Retiro asociado al período y horario aprobado | `EVE-06-retiro-programado.png` |
| 7 | Técnico | Registrar retiro realizado | Resultado de retiro guardado | `EVE-07-retiro-realizado.png` |
| 8 | Técnico y Soporte | Enviar conclusión final y aprobarla | Conclusión aprobada solo después del retiro | `EVE-08-conclusion-final.png` |
| 9 | Soporte o lectura autorizada | Reconsultar la CITE | Período, retiro, conclusión e historial persisten | `EVE-09-reconsulta-persistencia.png` |

**Condición temporal:** las fechas ficticias preparadas comienzan el 28/10/2026 y terminan el 29/10/2026. No completar el retiro antes de que el sistema lo permita ni alterar el reloj o los estados para acelerar la captura.

## Incidencia — `CITE-IT5-INC-001`

| Orden | Rol | Pantalla/acción | Resultado que se debe comprobar | Captura a guardar |
|---|---|---|---|---|
| 1 | Soporte | Abrir servicio finalizado y reportar incidencia `INC-IT5-CAMPO-001` | CITE e identificador de incidencia visibles | `INC-01-reporte.png` |
| 2 | Encargado de Planta Técnica | Asignar técnico | Responsable visible | `INC-02-asignacion.png` |
| 3 | Técnico y Soporte | Proponer y confirmar horario/equipo de atención | Equipo confirmado; líder mostrado como responsable | `INC-03-equipo-confirmado.png` |
| 4 | Técnico | Registrar atención realizada | Resultado de atención persistido | `INC-04-atencion-realizada.png` |
| 5 | Técnico | Registrar solución | Descripción de lo realizado visible | `INC-05-solucion.png` |
| 6 | Técnico y Soporte | Enviar conclusión y revisar/aprobar cierre | Decisión de revisión y estado final visibles | `INC-06-cierre-revisado.png` |
| 7 | Soporte | Reconsultar servicio e incidencia | Equipo, resultados, conclusión e historial persisten | `INC-07-reconsulta-persistencia.png` |

### Incidencias complementarias de validación

- Para `INC-IT5-REMOTO-001`, documentar el resultado escrito por el técnico e indicar explícitamente si el sistema presenta una modalidad remota o solo almacena texto libre. No registrar una visita que no ocurrió.
- Para `INC-IT5-CONTINUA-001`, registrar que la falla persiste, enviar conclusión y solicitar una revisión observada. Capturar que el caso no queda cerrado y que se conserva la observación.
- No sustituir esas pruebas por un cambio manual del estado de la base.

## Reglas para capturas

- Mantener cada CITE constante y visible durante su recorrido. Mostrar también el identificador de incidencia cuando corresponda.
- Incluir en cada imagen la etapa, rol y número del paso; ocultar credenciales y cualquier dato real.
- Guardar únicamente capturas de acciones realmente ejecutadas y resultados observados. Si una etapa queda bloqueada, capturar el mensaje de bloqueo y documentarlo sin marcar el recorrido como completo.
