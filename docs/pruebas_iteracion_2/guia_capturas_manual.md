# Guía manual de capturas — Iteración 2

## Condiciones para iniciar

1. Ejecutar solo en una instancia local con **base de datos desechable aislada** y cuentas ficticias habilitadas para Comercial, Encargado de Planta Técnica, Encargado de Sistemas, Soporte de Sistemas y Técnico. La configuración actual de Django apunta a PostgreSQL `datalan`; no abrir esa conexión para esta guía hasta que se haya confirmado que apunta a una base de pruebas aislada.
2. No reutilizar clientes, solicitudes, cuentas, contactos ni citas reales. No copiar datos personales a capturas.
3. Usar correos bajo `.invalid` y nombres claramente ficticios, por ejemplo `Empresa ficticia IT2`, `Nodo QA Norte`, `Sucursal QA Sur` y `qa+it2@example.invalid`.
4. Registrar en la hoja de resultados la CITE que genere la propia aplicación y conservar esa misma CITE en cada captura del recorrido. No inventar una CITE ni usar la de otra solicitud.
5. Para el caso eventual, registrar un período futuro realista. Inspección e instalación deben respetar los límites del código; el retiro se programa desde la fecha **HASTA** en adelante. No adelantar etapas, simular que el servicio ocurrió, cambiar el reloj ni registrar resultados antes de realizar los trabajos.
6. Para confirmar cada equipo, Soporte debe usar **GENERAR PROPUESTA**, seleccionar una alternativa y confirmar el horario. La propuesta es una dependencia funcional del proceso; no se evalúa aquí la calidad ni el rendimiento del algoritmo.

## Convención para los archivos de captura

Guardar PNG legibles en esta carpeta con patrón:

`IT2-PER-paso-rol-etapa-CITE.png` o `IT2-EVE-paso-rol-etapa-CITE.png`

Ejemplo de patrón (no es una evidencia ya tomada): `IT2-PER-08-soporte-inspeccion-CITE-generada.png`. Mostrar la CITE, etapa, decisión/resultado y, si aplica, el equipo; evitar incluir contraseñas, correo personal u otras solicitudes en el encuadre. Las capturas aún no existen y no deben citarse como evidencia hasta tomarlas.

## A. Solicitud permanente

| Paso / captura | Usuario o rol requerido | Pantalla y acción | Resultado que se debe observar antes de capturar |
|---|---|---|---|
| IT2-PER-01 — Registro | Comercial ficticio | **Nueva solicitud** (`/comercial/solicitudes/nueva/`). Completar datos obligatorios, tipo permanente y puntos de origen/destino; guardar. | Confirmación de registro y CITE que se utilizará durante todo el caso. |
| IT2-PER-02 — Remisión | Comercial ficticio | **Solicitudes** (`/comercial/solicitudes/`). Abrir la solicitud recién creada y elegir **Derivar**. | Estado de revisión de Planta Técnica y la misma CITE. |
| IT2-PER-03 — Evaluación técnica | Encargado de Planta Técnica | **Solicitudes** (`/planta-tecnica/encargado/solicitudes/`). Abrir la CITE, registrar factibilidad, distancia y observación/motivo si corresponde. | Evaluación de Planta guardada y derivación visible a Sistemas. |
| IT2-PER-04 — Evaluación de Sistemas | Encargado de Sistemas | **Solicitudes** (`/sistemas/solicitudes/`). Abrir la misma CITE, registrar decisión y observación cuando corresponda. | Evaluación de Sistemas asociada a la CITE. |
| IT2-PER-05 — Decisión comercial | Comercial ficticio | **En proceso** (`/comercial/en-proceso/`). Consultar las dos evaluaciones y aprobar la solicitud, registrando la decisión. | Ambas evaluaciones y decisión final comercial visibles. Si un área rechazó, no presentar la aprobación como validación unánime: el código permite que la decisión comercial prevalezca. |
| IT2-PER-06 — Responsables de Soporte | Encargado de Sistemas | **Solicitudes aprobadas** (`/sistemas/solicitudes/`). Asignar principal y secundario distintos, activos y ficticios. | Responsables y CITE visibles; no duplicar la misma persona en ambos campos. |
| IT2-PER-07 — Técnico responsable | Soporte asignado | **Solicitudes / Mis trabajos** (`/sistemas/soporte/solicitudes/`). Abrir el modal y asignar técnico disponible de Planta Técnica. | Nombre del técnico y CITE asociados a la solicitud. |
| IT2-PER-08a — Inspección programada | Técnico asignado | **Mis trabajos** (`/planta-tecnica/tecnico/trabajos/`). Registrar fecha/hora tentativa y trabajo por punto; enviar a Soporte. | Modal de Soporte con los puntos y cronograma tentativo de la misma CITE. |
| IT2-PER-08b — Horario y equipo de inspección | Soporte asignado | Abrir el trabajo, fijar horarios, elegir **GENERAR PROPUESTA**, seleccionar equipo y confirmar horario. | Horario aprobado y tarjeta de equipo debajo de los cronogramas; capturar propuesta y confirmación por separado si no caben legiblemente. |
| IT2-PER-09 — Inspección realizada | Técnico asignado | Volver a **Mis trabajos** después de realizar la inspección. Ingresar el resultado y registrar la inspección. | Resultado del técnico guardado en la sección de inspección; capturar la tarjeta debajo del equipo asignado. |
| IT2-PER-10 — Instalación programada | Técnico asignado y Soporte asignado | Tras completar la inspección, el técnico envía fechas/horas/trabajos por punto; Soporte genera propuesta, elige equipo y confirma. | Cronograma de instalación aprobado y equipo asignado en la etapa de instalación. |
| IT2-PER-11 — Instalación realizada | Técnico asignado | Después de realizar la instalación en las fechas coordinadas, registrar el resultado de instalación. | Resultado del técnico visible en instalación y mismo CITE. |
| IT2-PER-12 — Conclusión revisada | Técnico asignado y Soporte asignado | Técnico envía resultado final; Soporte abre la etapa y aprueba. | Conclusión, aprobador, fecha/hora y estado final `FINALIZADA` visibles. |
| IT2-PER-13 — Consulta posterior | Comercial o rol autorizado de consulta | Volver a abrir la solicitud o registro de Comercial con la misma CITE. | Datos y resultados siguen presentes tras nueva consulta; tomar captura separada de la vista persistida. |

## B. Solicitud eventual

| Paso / captura | Usuario o rol requerido | Pantalla y acción | Resultado que se debe observar antes de capturar |
|---|---|---|---|
| IT2-EVE-01 — Período | Comercial ficticio | **Nueva solicitud**, seleccionar servicio eventual, registrar fechas **DE** y **HASTA**, datos y puntos; guardar. | Período y CITE mostrados en la solicitud. |
| IT2-EVE-02 — Evaluaciones, decisión y asignaciones | Planta Técnica, Sistemas, Comercial y responsables de Sistemas/Soporte | Seguir las pantallas del flujo permanente con la misma CITE eventual: evaluación técnica, evaluación de Sistemas, decisión comercial y asignaciones. | Cada estado y responsable visibles; no avanzar a operación antes de la decisión comercial y las asignaciones. |
| IT2-EVE-03a — Inspección eventual programada y aprobada | Técnico asignado y Soporte asignado | Técnico registra cronograma dentro de los límites aplicables; Soporte revisa puntos, genera propuesta, selecciona equipo y confirma. | Fechas, equipo y aprobación de inspección vinculados a la CITE eventual. |
| IT2-EVE-03b — Inspección eventual realizada | Técnico asignado | Después de realizar la inspección, registrar el resultado técnico. | Resultado persistido y visible debajo del equipo asignado. |
| IT2-EVE-04a — Instalación eventual programada y aprobada | Técnico asignado y Soporte asignado | Tras completar inspección, enviar cronograma de instalación; Soporte genera propuesta, selecciona equipo y confirma. | Cronograma, equipo y confirmación en la etapa de instalación. |
| IT2-EVE-04b — Instalación eventual realizada | Técnico asignado | Después de ejecutar la instalación, registrar su resultado. | Resultado visible en instalación; no registrar antes del trabajo. |
| IT2-EVE-05a — Retiro programado | Técnico asignado | En **Retiro eventual**, proponer fechas desde **HASTA** en adelante y descripción por punto; enviar a Soporte. | Fechas tentativas iguales o posteriores a HASTA en el modal de Soporte. |
| IT2-EVE-05b — Retiro aprobado y equipo | Soporte asignado | Revisar propuesta, generar equipo, elegir alternativa y confirmar horarios del retiro. | Retiro aprobado, horarios posteriores o iguales a HASTA y equipo seleccionado. |
| IT2-EVE-06 — Retiro realizado | Técnico asignado | Una vez efectuado el retiro real, registrar el resultado. | Resultado del retiro visible antes de abrir la conclusión final. |
| IT2-EVE-07 — Conclusión eventual | Técnico asignado y Soporte asignado | Técnico envía conclusión; Soporte la revisa y aprueba después de completar el retiro. | Conclusión aprobada y solicitud finalizada; el historial muestra retiro anterior a la conclusión. |
| IT2-EVE-08 — Validaciones de retiro y conclusión | Soporte asignado y Técnico | En entorno aislado, comprobar que una solicitud permanente no ofrece/no acepta retiro eventual y que la conclusión eventual no se habilita antes del retiro realizado. | Evidencia de los mensajes/estados de bloqueo en las dos validaciones. |
| IT2-EVE-09 — Consulta posterior | Comercial o rol autorizado de consulta | Abrir nuevamente la misma CITE. | Período DE/HASTA, inspección, instalación, retiro, conclusión e historial permanecen visibles. |

## C. Rechazo y validaciones

| Paso / captura | Usuario o rol requerido | Pantalla y acción | Resultado que se debe observar antes de capturar |
|---|---|---|---|
| IT2-VAL-01 — Rechazo comercial | Comercial ficticio; usar otra CITE ficticia | Con ambas evaluaciones ya registradas, abrir **En proceso**, rechazar e ingresar motivo. | Estado rechazado y motivo visible en la misma solicitud. |
| IT2-VAL-02 — Historial de rechazo | Comercial o rol autorizado de consulta | Volver a abrir la CITE rechazada y mostrar recorrido/historial. | Solicitud no desaparece; decisión y motivo permanecen registrados. |
| IT2-VAL-03 — Sin aprobación | Rol de Sistemas con una CITE ficticia sin aprobaciones completas | Intentar asignar Soporte solo en el entorno desechable y registrar el mensaje de validación. | La asignación es rechazada y no se agrega responsable. Detenerse tras la validación; no forzar otros estados. |
| IT2-VAL-04 — Rol/responsable incorrecto | Cuenta de prueba de rol distinto o Soporte no asignado | Intentar una acción no autorizada en una CITE ficticia controlada. | Acceso/rechazo explícito y solicitud sin cambios. Repetir solo con autorización del responsable del entorno de pruebas. |

## Cierre de la ejecución manual

Al completar cada caso, descargar/capturar la consulta final y añadir a la tabla de resultados la fecha real, CITE, rol, resultado observado y nombre exacto del PNG. Si el calendario o una operación real impide avanzar, registrar **Bloqueado** con causa; no cambiar el reloj ni fabricar el evento.
