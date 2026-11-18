# Medición COSMIC y evidencia para estimación de costos — DATALAN

## Alcance y versión revisada

Revisión de solo lectura del árbol de trabajo disponible. Rama `master`; commit del repositorio raíz `6c1252b49a79be5ce563fb6ac700864df02fe04e`; proyecto DATALAN anidado en `4b3dbbf1f87645f736ddc3432f4d366b79def049`. Ambos árboles presentan modificaciones locales y archivos sin seguimiento, incluidos fuentes, pruebas y documentación. La revisión describe esos archivos locales; no se debe atribuir íntegramente a los commits publicados.

Los IDs `I#-P##` son etiquetas creadas para esta matriz, no identificadores del sistema. La trazabilidad usa la matriz local HU-01–HU-15 de [INFORME_ACTUALIZADO_DATALAN.md](INFORME_ACTUALIZADO_DATALAN.md#2-cambios-respecto-al-informe-anterior) y las evidencias P1–P4. No se encontró un catálogo oficial completo de HU/RF.

## Regla de conteo

- **E**: dato o acción que entra desde el usuario.
- **R**: grupo recuperado de almacenamiento.
- **W**: grupo persistido.
- **X**: respuesta observable por el usuario.
- La confirmación o el error de una operación está incluido en su X; no se cuenta como otro movimiento.
- Se agrupa cada solicitud con su flujo e historial anidado, y cada incidencia con su flujo. No se separan campos JSONB, consultas SQL ni llamadas repetidas a `get_requests`/`save_requests`.
- Se cuentan consultas que constituyen una función iniciada por el actor, no automáticamente cada pantalla.
- Las filas describen la ruta nominal; la misma operación puede responder con error de validación o autorización, sin que ese error agregue otro movimiento.

## Movimientos candidatos

### Iteración 1 — acceso y perfiles

| Iteración | HU/RF | ID proceso | Usuario funcional | Evento disparador | Movimiento | Grupo de datos | Explicación | Archivo / símbolo |
|---|---|---|---|---|---|---|---|---|
| 1 | HU-01 | I1-P01 | Usuario | Enviar credenciales | E | Credenciales | Recibe usuario y contraseña. | [login_view()](../DATALAN/DATALAN/views.py#L2392) |
| 1 | HU-01 | I1-P01 | Usuario | Enviar credenciales | R | Cuenta | Recupera la cuenta activa para autenticar. | [authenticate()](../DATALAN/DATALAN/auth_service.py#L57) |
| 1 | HU-01 | I1-P01 | Usuario | Enviar credenciales | R | Rol asignado | Recupera el rol asociado a la cuenta. | [authenticate()](../DATALAN/DATALAN/auth_service.py#L57) |
| 1 | HU-01 | I1-P01 | Usuario | Autenticación válida | W | Último acceso | Actualiza el último acceso de la cuenta. | [authenticate()](../DATALAN/DATALAN/auth_service.py#L57) |
| 1 | HU-01 | I1-P01 | Usuario | Autenticación válida | W | Sesión | Guarda identidad y rol en la sesión persistida. | [login_view()](../DATALAN/DATALAN/views.py#L2392); [settings.py](../DATALAN/DATALAN/settings.py#L150) |
| 1 | HU-01 | I1-P01 | Usuario | Resultado de autenticación | X | Resultado de acceso | Redirige al inicio del rol o presenta error de credenciales/cuenta inactiva. | [login_view()](../DATALAN/DATALAN/views.py#L2392) |
| 1 | HU-01 | I1-P02 | Usuario autenticado | Cerrar sesión | E | Acción de cierre | Recibe la acción del usuario. | [logout_view()](../DATALAN/DATALAN/views.py#L2411) |
| 1 | HU-01 | I1-P02 | Usuario autenticado | Cerrar sesión | W | Sesión | Vacía la sesión persistida. | [logout_view()](../DATALAN/DATALAN/views.py#L2411) |
| 1 | HU-01 | I1-P02 | Usuario autenticado | Resultado del cierre | X | Confirmación | Muestra confirmación del cierre. | [logout_view()](../DATALAN/DATALAN/views.py#L2411) |
| 1 | HU-01 | I1-P03 | Administrador | Consultar accesos de roles | E | Consulta de accesos | Solicita ver los accesos configurados. | [roles_access()](../DATALAN/DATALAN/views.py#L2617) |
| 1 | HU-01 | I1-P03 | Administrador | Consultar accesos de roles | R | Accesos por rol | Recupera los módulos configurados desde almacenamiento. | [get_role_module_access()](../DATALAN/DATALAN/auth_service.py) |
| 1 | HU-01 | I1-P03 | Administrador | Mostrar accesos | X | Accesos por rol | Muestra los módulos habilitados por rol. | [roles_access()](../DATALAN/DATALAN/views.py#L2617) |
| 1 | HU-01 | I1-P04 | Administrador | Guardar accesos de un rol | E | Rol y módulos | Recibe la selección de módulos. | [roles_access()](../DATALAN/DATALAN/views.py#L2617) |
| 1 | HU-01 | I1-P04 | Administrador | Guardar accesos de un rol | R | Rol | Comprueba que el rol exista. | [save_role_module_access()](../DATALAN/DATALAN/auth_service.py#L218) |
| 1 | HU-01 | I1-P04 | Administrador | Guardar accesos de un rol | W | Accesos por rol | Inserta o actualiza los módulos habilitados. | [save_role_module_access()](../DATALAN/DATALAN/auth_service.py#L218) |
| 1 | HU-01 | I1-P04 | Administrador | Resultado del guardado | X | Resultado de guardado | Muestra confirmación o error de selección. | [roles_access()](../DATALAN/DATALAN/views.py#L2617) |
| 1 | HU-06? | I1-P05 | Encargado de Planta Técnica | Consultar perfiles operativos | E | Consulta de perfiles | Solicita consultar técnicos/perfiles. | [urls.py](../DATALAN/DATALAN/urls.py#L70); [workflow()](../DATALAN/DATALAN/views.py#L3845) |
| 1 | HU-06? | I1-P05 | Encargado de Planta Técnica | Consultar perfiles operativos | R | Perfil operativo | Recupera capacidades, disponibilidad y horario. | [get_technicians()](../DATALAN/DATALAN/optimization_service.py#L1119) |
| 1 | HU-06? | I1-P05 | Encargado de Planta Técnica | Mostrar perfiles | X | Perfil operativo | Muestra los datos del perfil consultado. | [get_technicians()](../DATALAN/DATALAN/optimization_service.py#L1119); [technician-capabilities-modal.html](../DATALAN/DATALAN/templates/technician-capabilities-modal.html) |
| 1 | HU-06? | I1-P06 | Encargado de Planta Técnica | Guardar perfil operativo | E | Perfil operativo | Recibe los cambios del perfil. | [update_technician_profile()](../DATALAN/DATALAN/views.py#L3129) |
| 1 | HU-06? | I1-P06 | Encargado de Planta Técnica | Guardar perfil operativo | W | Perfil operativo | Actualiza el perfil operativo del técnico. | [update_technician()](../DATALAN/DATALAN/optimization_service.py#L1254) |
| 1 | HU-06? | I1-P06 | Encargado de Planta Técnica | Resultado del guardado | X | Resultado de guardado | Muestra confirmación o error de validación. | [update_technician_profile()](../DATALAN/DATALAN/views.py#L3129) |
| 1 | HU-06? | I1-P07 | Encargado de Planta Técnica | Consultar perfiles de incidencias | E | Consulta de perfiles | Solicita perfiles específicos de incidencias. | [urls.py](../DATALAN/DATALAN/urls.py#L72); [workflow()](../DATALAN/DATALAN/views.py#L3845) |
| 1 | HU-06? | I1-P07 | Encargado de Planta Técnica | Consultar perfiles | R | Perfil de incidencias | Recupera valoración y capacidades para incidentes. | [get_technicians()](../DATALAN/DATALAN/optimization_service.py#L1119) |
| 1 | HU-06? | I1-P07 | Encargado de Planta Técnica | Mostrar perfiles | X | Perfil de incidencias | Muestra los datos del perfil consultado. | [technician-incident-capabilities.html](../DATALAN/DATALAN/templates/technician-incident-capabilities.html) |
| 1 | HU-06? | I1-P08 | Encargado de Planta Técnica | Guardar perfil de incidencias | E | Perfil de incidencias | Recibe valoración/capacidades editadas. | [update_incident_technician_profile()](../DATALAN/DATALAN/views.py#L3145) |
| 1 | HU-06? | I1-P08 | Encargado de Planta Técnica | Guardar perfil | W | Perfil de incidencias | Actualiza el JSONB de perfil de incidencias. | [update_incident_technician()](../DATALAN/DATALAN/optimization_service.py#L1267) |
| 1 | HU-06? | I1-P08 | Encargado de Planta Técnica | Resultado del guardado | X | Resultado de guardado | Muestra confirmación o error de validación. | [update_incident_technician_profile()](../DATALAN/DATALAN/views.py#L3145) |

### Iteración 2 — solicitudes, evaluaciones, asignaciones y cronogramas

| Iteración | HU/RF | ID proceso | Usuario funcional | Evento disparador | Movimiento | Grupo de datos | Explicación | Archivo / símbolo |
|---|---|---|---|---|---|---|---|---|
| 2 | HU-02? | I2-P01 | Comercial / Planta / Sistemas / Soporte | Consultar solicitudes | E | Consulta | Pide los casos visibles para su rol. | [workflow()](../DATALAN/DATALAN/views.py#L3845) |
| 2 | HU-02? | I2-P01 | Comercial / Planta / Sistemas / Soporte | Consultar solicitudes | R | Solicitud y flujo | Recupera datos y estado del caso. | [get_requests()](../DATALAN/DATALAN/workflow_service.py#L101) |
| 2 | HU-02? | I2-P01 | Comercial / Planta / Sistemas / Soporte | Mostrar solicitudes | X | Solicitudes filtradas | Presenta datos/estado pertinentes al rol. | [workflow()](../DATALAN/DATALAN/views.py#L3845) |
| 2 | HU-02 | I2-P02 | Comercial | Registrar solicitud | E | Solicitud | Recibe cliente, tipo, requisitos, ubicación y fechas. | [workflow()](../DATALAN/DATALAN/views.py#L3845) |
| 2 | HU-02 | I2-P02 | Comercial | Registrar solicitud | R | Solicitudes existentes | Consulta casos existentes para CITE/validación. | [get_requests()](../DATALAN/DATALAN/workflow_service.py#L101) |
| 2 | HU-02 | I2-P02 | Comercial | Registrar solicitud | W | Solicitud y flujo | Persiste solicitud, estado e historial inicial. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-02 | I2-P02 | Comercial | Resultado del registro | X | CITE y resultado | Muestra confirmación/CITE o errores de validación. | [workflow()](../DATALAN/DATALAN/views.py#L4320) |
| 2 | HU-02 | I2-P03 | Comercial | Editar solicitud registrada | E | Solicitud | Recibe cambios antes de derivación. | [workflow()](../DATALAN/DATALAN/views.py#L4375) |
| 2 | HU-02 | I2-P03 | Comercial | Editar solicitud registrada | R | Solicitud y flujo | Verifica que siga pendiente de derivación. | [workflow()](../DATALAN/DATALAN/views.py#L4375) |
| 2 | HU-02 | I2-P03 | Comercial | Editar solicitud registrada | W | Solicitud y flujo | Guarda cambios e historial. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-02 | I2-P03 | Comercial | Resultado de edición | X | Resultado de edición | Muestra confirmación/error. | [workflow()](../DATALAN/DATALAN/views.py#L4385) |
| 2 | HU-02 | I2-P04 | Comercial | Derivar solicitud | E | CITE y confirmación | Recibe confirmación para derivar. | [workflow()](../DATALAN/DATALAN/views.py#L4400) |
| 2 | HU-02 | I2-P04 | Comercial | Derivar solicitud | R | Solicitud y flujo | Valida que el caso esté recién registrado. | [workflow()](../DATALAN/DATALAN/views.py#L4400) |
| 2 | HU-02 | I2-P04 | Comercial | Derivar solicitud | W | Solicitud y flujo | Guarda fecha y estado de derivación. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-02 | I2-P04 | Comercial | Resultado de derivación | X | Confirmación/error | Confirma derivación o informa que ya no procede. | [workflow()](../DATALAN/DATALAN/views.py#L4400) |
| 2 | HU-02? | I2-P05 | Comercial | Cancelar antes de derivar | E | CITE y confirmación | Recibe solicitud de cancelación. | [workflow()](../DATALAN/DATALAN/views.py#L4416) |
| 2 | HU-02? | I2-P05 | Comercial | Cancelar antes de derivar | R | Solicitud y flujo | Comprueba estado registrado. | [workflow()](../DATALAN/DATALAN/views.py#L4416) |
| 2 | HU-02? | I2-P05 | Comercial | Cancelar antes de derivar | W | Solicitud y flujo | Persiste estado cancelado e historial. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-02? | I2-P05 | Comercial | Resultado de cancelación | X | Confirmación/error | Confirma o rechaza por estado no elegible. | [workflow()](../DATALAN/DATALAN/views.py#L4416) |
| 2 | HU-03 | I2-P06 | Encargado de Planta Técnica | Registrar evaluación técnica | E | Factibilidad, distancia y razón | Recibe decisión/observaciones técnicas. | [workflow()](../DATALAN/DATALAN/views.py#L4475) |
| 2 | HU-03 | I2-P06 | Encargado de Planta Técnica | Registrar evaluación técnica | R | Solicitud y flujo | Recupera requisitos/estado para evaluar. | [workflow()](../DATALAN/DATALAN/views.py#L4475) |
| 2 | HU-03 | I2-P06 | Encargado de Planta Técnica | Registrar evaluación técnica | W | Solicitud y flujo | Persiste evaluación, decisión y estado. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-03 | I2-P06 | Encargado de Planta Técnica | Resultado de evaluación | X | Confirmación/error | Informa envío a Sistemas o error de validación. | [workflow()](../DATALAN/DATALAN/views.py#L4506) |
| 2 | HU-04? | I2-P07 | Encargado de Sistemas | Registrar revisión de Sistemas | E | Decisión y razón | Recibe decisión/observación. | [workflow()](../DATALAN/DATALAN/views.py#L4520) |
| 2 | HU-04? | I2-P07 | Encargado de Sistemas | Registrar revisión de Sistemas | R | Solicitud y flujo | Verifica evaluación previa y estado. | [workflow()](../DATALAN/DATALAN/views.py#L4520) |
| 2 | HU-04? | I2-P07 | Encargado de Sistemas | Registrar revisión de Sistemas | W | Solicitud y flujo | Persiste revisión/decisión y estado. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-04? | I2-P07 | Encargado de Sistemas | Resultado de revisión | X | Confirmación/error | Muestra resultado o rechazo por estado inválido. | [workflow()](../DATALAN/DATALAN/views.py#L4520) |
| 2 | HU-03/04? | I2-P08 | Comercial | Aprobar o rechazar solicitud | E | Decisión y razón | Recibe decisión/razón comercial. | [workflow()](../DATALAN/DATALAN/views.py#L4440) |
| 2 | HU-03/04? | I2-P08 | Comercial | Aprobar o rechazar solicitud | R | Solicitud y evaluaciones | Comprueba evaluaciones de ambas áreas y estado. | [workflow()](../DATALAN/DATALAN/views.py#L4440) |
| 2 | HU-03/04? | I2-P08 | Comercial | Aprobar o rechazar solicitud | W | Solicitud y flujo | Guarda decisión, fecha/razón e historial. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-03/04? | I2-P08 | Comercial | Resultado comercial | X | Confirmación/error | Confirma aprobación/rechazo o informa validación fallida. | [workflow()](../DATALAN/DATALAN/views.py#L4440) |
| 2 | HU-04 | I2-P09 | Encargado de Sistemas | Asignar personal de soporte | E | Responsables seleccionados | Recibe encargados principal/secundario. | [workflow()](../DATALAN/DATALAN/views.py#L4540) |
| 2 | HU-04 | I2-P09 | Encargado de Sistemas | Asignar personal de soporte | R | Solicitud y flujo | Comprueba que la solicitud pueda asignarse. | [workflow()](../DATALAN/DATALAN/views.py#L4540) |
| 2 | HU-04 | I2-P09 | Encargado de Sistemas | Asignar personal de soporte | R | Personal activo de Soporte | Recupera responsables disponibles por rol. | [get_active_users_by_role()](../DATALAN/DATALAN/auth_service.py) |
| 2 | HU-04 | I2-P09 | Encargado de Sistemas | Resultado de asignación | W | Solicitud y flujo | Guarda responsables e historial. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-04 | I2-P09 | Encargado de Sistemas | Resultado de asignación | X | Confirmación/error | Confirma asignación o informa selección inválida. | [workflow()](../DATALAN/DATALAN/views.py#L4540) |
| 2 | HU-05? | I2-P10 | Soporte / Encargado de Sistemas | Asignar técnico | E | Técnico elegido | Recibe técnico propuesto. | [workflow()](../DATALAN/DATALAN/views.py#L4590) |
| 2 | HU-05? | I2-P10 | Soporte / Encargado de Sistemas | Asignar técnico | R | Solicitud y flujo | Valida aprobación y asignación previa a Soporte. | [workflow()](../DATALAN/DATALAN/views.py#L4590) |
| 2 | HU-05? | I2-P10 | Soporte / Encargado de Sistemas | Asignar técnico | R | Técnicos disponibles | Comprueba disponibilidad del técnico. | [get_technicians()](../DATALAN/DATALAN/optimization_service.py#L1119) |
| 2 | HU-05? | I2-P10 | Soporte / Encargado de Sistemas | Resultado de asignación | W | Solicitud y flujo | Persiste el responsable técnico. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-05? | I2-P10 | Soporte / Encargado de Sistemas | Resultado de asignación | X | Confirmación/error | Confirma o informa que el técnico no es elegible. | [workflow()](../DATALAN/DATALAN/views.py#L4590) |
| 2 | HU-07? | I2-P11 | Técnico | Enviar cronograma de inspección | E | Fechas, horas y trabajo previsto | Recibe propuesta por punto. | [workflow()](../DATALAN/DATALAN/views.py#L4036) |
| 2 | HU-07? | I2-P11 | Técnico | Enviar cronograma de inspección | R | Solicitud y puntos | Recupera puntos y fecha límite. | [workflow()](../DATALAN/DATALAN/views.py#L4036) |
| 2 | HU-07? | I2-P11 | Técnico | Enviar cronograma de inspección | W | Solicitud y flujo | Guarda cronograma tentativo y descripciones. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-07? | I2-P11 | Técnico | Resultado de envío | X | Confirmación/error | Confirma envío a Soporte o errores de fecha/datos. | [workflow()](../DATALAN/DATALAN/views.py#L4036) |
| 2 | HU-07? / HU-10? | I2-P12 | Soporte / Sistemas | Aprobar horario de inspección y seleccionar equipo | E | Fechas aprobadas/equipo | Recibe fechas confirmadas y selección. | [workflow()](../DATALAN/DATALAN/views.py#L4156) |
| 2 | HU-07? / HU-10? | I2-P12 | Soporte / Sistemas | Aprobar horario de inspección | R | Inspección y solicitud | Verifica propuesta y datos del horario. | [workflow()](../DATALAN/DATALAN/views.py#L4156) |
| 2 | HU-07? / HU-10? | I2-P12 | Soporte / Sistemas | Aprobar horario de inspección | R | Propuesta de equipo | Comprueba ID, suficiencia y firma del horario. | [_approved_team_for_schedule()](../DATALAN/DATALAN/views.py#L3454) |
| 2 | HU-07? / HU-10? | I2-P12 | Soporte / Sistemas | Aprobar horario de inspección | W | Solicitud y flujo | Guarda horario/equipo aprobados. | [workflow()](../DATALAN/DATALAN/views.py#L4156) |
| 2 | HU-07? / HU-10? | I2-P12 | Soporte / Sistemas | Resultado de aprobación | X | Confirmación/error | Informa aprobación o error de selección/horario. | [workflow()](../DATALAN/DATALAN/views.py#L4156) |
| 2 | HU-08? | I2-P13 | Técnico | Registrar resultado de inspección | E | Resultado de inspección | Recibe resultado técnico. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2099) |
| 2 | HU-08? | I2-P13 | Técnico | Registrar resultado | R | Solicitud/etapa | Comprueba que la inspección esté aprobada. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2248) |
| 2 | HU-08? | I2-P13 | Técnico | Registrar resultado | W | Solicitud/etapa | Persiste resultado y estado completado. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2248) |
| 2 | HU-08? | I2-P13 | Técnico | Resultado de inspección | X | Confirmación/error | Confirma registro o informa etapa/resultado inválido. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2248) |
| 2 | HU-07? | I2-P14 | Técnico | Enviar cronograma de instalación | E | Fechas, horas y descripciones | Recibe propuesta de instalación. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2259) |
| 2 | HU-07? | I2-P14 | Técnico | Enviar cronograma de instalación | R | Solicitud y etapa | Comprueba inspección previa y fechas límite. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2259) |
| 2 | HU-07? | I2-P14 | Técnico | Enviar cronograma de instalación | W | Solicitud y etapa | Guarda horario tentativo. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-07? | I2-P14 | Técnico | Resultado de envío | X | Confirmación/error | Confirma o muestra error de fecha/estado. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2259) |
| 2 | HU-07? / HU-10? | I2-P15 | Soporte / Sistemas | Aprobar horario de instalación y seleccionar equipo | E | Horario y equipo | Recibe selección de equipo y fechas definitivas. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2273) |
| 2 | HU-07? / HU-10? | I2-P15 | Soporte / Sistemas | Aprobar horario de instalación | R | Solicitud/etapa | Recupera cronograma tentativo y estado. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2273) |
| 2 | HU-07? / HU-10? | I2-P15 | Soporte / Sistemas | Aprobar horario de instalación | R | Propuesta de equipo | Revalida equipo seleccionado y firma de fechas. | [_approved_team_for_schedule()](../DATALAN/DATALAN/views.py#L3454) |
| 2 | HU-07? / HU-10? | I2-P15 | Soporte / Sistemas | Aprobar horario de instalación | W | Solicitud/etapa | Guarda horario y equipo aprobados. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2273) |
| 2 | HU-07? / HU-10? | I2-P15 | Soporte / Sistemas | Resultado de aprobación | X | Confirmación/error | Confirma aprobación o informa error de horario/propuesta. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2273) |
| 2 | HU-08? | I2-P16 | Técnico | Registrar instalación realizada | E | Resultado de instalación | Recibe resultado de trabajo. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2278) |
| 2 | HU-08? | I2-P16 | Técnico | Registrar instalación realizada | R | Solicitud/etapa | Verifica horario aprobado y resultado pendiente. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2278) |
| 2 | HU-08? | I2-P16 | Técnico | Registrar instalación realizada | W | Solicitud/etapa | Persiste finalización de instalación. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2278) |
| 2 | HU-08? | I2-P16 | Técnico | Resultado de instalación | X | Confirmación/error | Confirma y habilita siguiente etapa o indica bloqueo. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2278) |
| 2 | HU-08? | I2-P17 | Técnico | Enviar conclusión | E | Resultado final | Recibe texto de conclusión. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2300) |
| 2 | HU-08? | I2-P17 | Técnico | Enviar conclusión | R | Solicitud/etapas | Verifica instalación y, si eventual, retiro completo. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2300) |
| 2 | HU-08? | I2-P17 | Técnico | Enviar conclusión | W | Solicitud/flujo | Guarda conclusión enviada; no finaliza por sí sola. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2300) |
| 2 | HU-08? | I2-P17 | Técnico | Resultado de envío | X | Confirmación/error | Confirma envío a Soporte o informa datos faltantes. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2300) |
| 2 | HU-08? | I2-P18 | Soporte / Sistemas | Revisar conclusión | E | Decisión y nota | Recibe aprobar/observar y nota obligatoria si devuelve. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2317) |
| 2 | HU-08? | I2-P18 | Soporte / Sistemas | Revisar conclusión | R | Solicitud/conclusión | Recupera estado enviado y requisito de retiro eventual. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2317) |
| 2 | HU-08? | I2-P18 | Soporte / Sistemas | Revisar conclusión | W | Solicitud/conclusión | Persiste revisión; aprobación marca FINALIZADA. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2317) |
| 2 | HU-08? | I2-P18 | Soporte / Sistemas | Resultado de revisión | X | Confirmación/error | Confirma aprobación/devolución o informa error. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2317) |
| 2 | HU-08? | I2-P19 | Técnico | Enviar cronograma de retiro eventual | E | Fechas, horas y trabajo | Recibe propuesta de retiro. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2338) |
| 2 | HU-08? | I2-P19 | Técnico | Enviar cronograma de retiro | R | Solicitud/etapa | Comprueba eventualidad e instalación previa. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2338) |
| 2 | HU-08? | I2-P19 | Técnico | Enviar cronograma de retiro | W | Solicitud/etapa | Guarda propuesta de retiro. | [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 2 | HU-08? | I2-P19 | Técnico | Resultado de envío | X | Confirmación/error | Confirma envío o rechaza fecha/no eventualidad. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2338) |
| 2 | HU-08? / HU-10? | I2-P20 | Soporte / Sistemas | Aprobar retiro y seleccionar equipo | E | Horario/equipo | Recibe selección y horario de retiro. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2354) |
| 2 | HU-08? / HU-10? | I2-P20 | Soporte / Sistemas | Aprobar horario de retiro | R | Solicitud/etapa | Valida eventualidad, instalación y cronograma. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2354) |
| 2 | HU-08? / HU-10? | I2-P20 | Soporte / Sistemas | Aprobar horario de retiro | R | Propuesta de equipo | Verifica equipo propuesto y correspondencia temporal. | [_approved_team_for_schedule()](../DATALAN/DATALAN/views.py#L3454) |
| 2 | HU-08? / HU-10? | I2-P20 | Soporte / Sistemas | Aprobar horario de retiro | W | Solicitud/etapa | Guarda horario y equipo aprobados. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2354) |
| 2 | HU-08? / HU-10? | I2-P20 | Soporte / Sistemas | Resultado de aprobación | X | Confirmación/error | Confirma aprobación o error de elegibilidad/fecha. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2354) |
| 2 | HU-08? | I2-P21 | Técnico | Registrar retiro realizado | E | Resultado del retiro | Recibe resultado técnico. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2361) |
| 2 | HU-08? | I2-P21 | Técnico | Registrar retiro realizado | R | Solicitud/etapa | Verifica eventualidad y horario aprobado. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2361) |
| 2 | HU-08? | I2-P21 | Técnico | Registrar retiro realizado | W | Solicitud/etapa | Persiste el retiro completado. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2361) |
| 2 | HU-08? | I2-P21 | Técnico | Resultado del retiro | X | Confirmación/error | Confirma retiro y habilita conclusión final, o informa bloqueo. | [handle_operational_stage_post()](../DATALAN/DATALAN/views.py#L2361) |

### Iteración 3 — incidencias

| Iteración | HU/RF | ID proceso | Usuario funcional | Evento disparador | Movimiento | Grupo de datos | Explicación | Archivo / símbolo |
|---|---|---|---|---|---|---|---|---|
| 3 | HU-11 | I3-P01 | Soporte / Encargado de Sistemas | Reportar incidencia | E | Descripción y CITE | Recibe servicio seleccionado y descripción. | [workflow()](../DATALAN/DATALAN/views.py#L3976) |
| 3 | HU-11 | I3-P01 | Soporte / Encargado de Sistemas | Reportar incidencia | R | Solicitud/enlace activo | Comprueba PP/MP instalado y conclusión aprobada. | [is_completed_active_point_link()](../DATALAN/DATALAN/views.py#L942) |
| 3 | HU-11 | I3-P01 | Soporte / Encargado de Sistemas | Reportar incidencia | W | Incidencia | Persiste reporte, identificador y estado inicial dentro de solicitud. | [workflow()](../DATALAN/DATALAN/views.py#L3976); [save_requests()](../DATALAN/DATALAN/workflow_service.py#L119) |
| 3 | HU-11 | I3-P01 | Soporte / Encargado de Sistemas | Resultado del reporte | X | Identificador y resultado | Confirma derivación o muestra error de enlace/descripción. | [workflow()](../DATALAN/DATALAN/views.py#L3976) |
| 3 | HU-11/12 | I3-P02 | Soporte / Sistemas / Planta | Consultar incidencias | E | Consulta | Solicita listado/estado de incidencias. | [urls.py](../DATALAN/DATALAN/urls.py#L93) |
| 3 | HU-11/12 | I3-P02 | Soporte / Sistemas / Planta | Consultar incidencias | R | Incidencias y flujo | Recupera reporte, estado, atención, solución y conclusión disponibles. | [flatten_service_incidents()](../DATALAN/DATALAN/views.py#L1045); [get_requests()](../DATALAN/DATALAN/workflow_service.py#L101) |
| 3 | HU-11/12 | I3-P02 | Soporte / Sistemas / Planta | Mostrar incidencias | X | Incidencias y estado | Presenta reporte e historial operativo disponible. | [workflow()](../DATALAN/DATALAN/views.py#L3845) |
| 3 | HU-12 | I3-P03 | Encargado de Planta Técnica | Asignar técnico a incidencia | E | Técnico elegido | Recibe técnico seleccionado. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1278) |
| 3 | HU-12 | I3-P03 | Encargado de Planta Técnica | Asignar técnico | R | Incidencia | Verifica estado y responsable actual. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1278) |
| 3 | HU-12 | I3-P03 | Encargado de Planta Técnica | Asignar técnico | R | Técnicos disponibles | Recupera técnicos elegibles. | [get_technicians()](../DATALAN/DATALAN/optimization_service.py#L1119) |
| 3 | HU-12 | I3-P03 | Encargado de Planta Técnica | Asignar técnico | W | Incidencia | Persiste técnico y estado asignado. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1278) |
| 3 | HU-12 | I3-P03 | Encargado de Planta Técnica | Resultado de asignación | X | Confirmación/error | Confirma o rechaza por rol/disponibilidad/estado. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1278) |
| 3 | HU-12 | I3-P04 | Técnico asignado | Proponer horario de atención | E | Fecha, hora y trabajo | Recibe horario tentativo y descripción. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1302) |
| 3 | HU-12 | I3-P04 | Técnico asignado | Proponer horario | R | Incidencia/atención | Comprueba estado, asignación y etapa. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1302) |
| 3 | HU-12 | I3-P04 | Técnico asignado | Proponer horario | W | Incidencia/atención | Guarda propuesta tentativa y estado. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1302) |
| 3 | HU-12 | I3-P04 | Técnico asignado | Resultado de propuesta | X | Confirmación/error | Confirma envío al reportante o expone validación fallida. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1302) |
| 3 | HU-12 | I3-P05 | Técnico asignado | Iniciar atención | E | Orden de inicio | Recibe la acción del técnico. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1423) |
| 3 | HU-12 | I3-P05 | Técnico asignado | Iniciar atención | R | Incidencia/horario | Verifica aprobación previa y que no se haya iniciado. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1423) |
| 3 | HU-12 | I3-P05 | Técnico asignado | Iniciar atención | W | Incidencia/atención | Guarda inicio real y estado en curso. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1423) |
| 3 | HU-12 | I3-P05 | Técnico asignado | Resultado del inicio | X | Confirmación/error | Confirma inicio o informa que falta aprobación/permiso. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1423) |
| 3 | HU-12 | I3-P06 | Técnico asignado | Registrar resultado de atención | E | Resultado | Recibe resultado del trabajo. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1446) |
| 3 | HU-12 | I3-P06 | Técnico asignado | Registrar resultado | R | Incidencia/atención | Verifica inicio real y horario aprobado. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1446) |
| 3 | HU-12 | I3-P06 | Técnico asignado | Registrar resultado | W | Incidencia/atención | Guarda actividad, resultado y estado completado. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1446) |
| 3 | HU-12 | I3-P06 | Técnico asignado | Resultado de atención | X | Confirmación/error | Indica atención registrada o validación fallida. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1446) |
| 3 | HU-12 | I3-P07 | Técnico asignado | Registrar intento de solución | E | Resultado y clasificación | Recibe texto y marca SOLUCIONADA o PERSISTE. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1446) |
| 3 | HU-12 | I3-P07 | Técnico asignado | Registrar intento | R | Incidencia/solución | Verifica atención completada y estado de conclusión. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1446) |
| 3 | HU-12 | I3-P07 | Técnico asignado | Registrar intento | W | Incidencia/solución | Agrega intento; PERSISTE mantiene caso abierto. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1446) |
| 3 | HU-12 | I3-P07 | Técnico asignado | Resultado de intento | X | Confirmación/error | Informa si continúa pendiente o puede concluirse. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1446) |
| 3 | HU-12 | I3-P08 | Técnico asignado | Enviar conclusión de incidencia | E | Resultado final | Recibe conclusión técnica. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1588) |
| 3 | HU-12 | I3-P08 | Técnico asignado | Enviar conclusión | R | Incidencia/solución | Comprueba solución confirmada y que no esté cerrada. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1588) |
| 3 | HU-12 | I3-P08 | Técnico asignado | Enviar conclusión | W | Incidencia/conclusión | Persiste conclusión ENVIADA; no cierra el caso. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1588) |
| 3 | HU-12 | I3-P08 | Técnico asignado | Resultado de envío | X | Confirmación/error | Confirma envío a revisión o informa requisito incumplido. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1588) |
| 3 | HU-12 | I3-P09 | Soporte / Sistemas autorizado | Revisar conclusión y cerrar/devolver | E | Decisión y nota | Recibe aprobar/observar y nota de revisión. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1621) |
| 3 | HU-12 | I3-P09 | Soporte / Sistemas autorizado | Revisar conclusión | R | Incidencia/conclusión y solución | Comprueba conclusión enviada y solución confirmada. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1621) |
| 3 | HU-12 | I3-P09 | Soporte / Sistemas autorizado | Revisar conclusión | W | Incidencia/conclusión | Persiste revisión; aprobación cierra, observación devuelve. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1621) |
| 3 | HU-12 | I3-P09 | Soporte / Sistemas autorizado | Resultado de revisión | X | Confirmación/error | Confirma cierre/devolución o informa falta de permiso/datos. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1621) |

### Iteración 4 — optimización, consulta y selección

| Iteración | HU/RF | ID proceso | Usuario funcional | Evento disparador | Movimiento | Grupo de datos | Explicación | Archivo / símbolo |
|---|---|---|---|---|---|---|---|---|
| 4 | HU-15? | I4-P01 | Encargado de Sistemas | Consultar parámetros del AG | E | Consulta de configuración | Solicita ver parámetros actuales. | [workflow()](../DATALAN/DATALAN/views.py#L3917) |
| 4 | HU-15? | I4-P01 | Encargado de Sistemas | Consultar parámetros del AG | R | Configuración genética | Recupera parámetros guardados. | [get_optimization_config()](../DATALAN/DATALAN/optimization_service.py#L123) |
| 4 | HU-15? | I4-P01 | Encargado de Sistemas | Mostrar parámetros AG | X | Configuración genética | Presenta parámetros actuales, no resultados del algoritmo. | [workflow()](../DATALAN/DATALAN/views.py#L3917) |
| 4 | HU-15? | I4-P02 | Encargado de Sistemas | Consultar parámetros NSGA-II | E | Consulta de configuración | Solicita parámetros actuales de incidencias. | [workflow()](../DATALAN/DATALAN/views.py#L3917) |
| 4 | HU-15? | I4-P02 | Encargado de Sistemas | Consultar parámetros NSGA-II | R | Configuración NSGA-II | Recupera parámetros guardados. | [get_incident_nsga2_config()](../DATALAN/DATALAN/optimization_service.py) |
| 4 | HU-15? | I4-P02 | Encargado de Sistemas | Mostrar parámetros NSGA-II | X | Configuración NSGA-II | Muestra parámetros de ejecución. | [workflow()](../DATALAN/DATALAN/views.py#L3917) |
| 4 | HU-09 | I4-P03 | Encargado de Sistemas | Ejecutar optimización general de solicitudes | E | Parámetros de ejecución | Recibe población, generaciones, mutación y cruce. | [workflow()](../DATALAN/DATALAN/views.py#L4269) |
| 4 | HU-09 | I4-P03 | Encargado de Sistemas | Ejecutar optimización | R | Solicitudes elegibles | Usa casos aprobados/no asignados y estado actual. | [optimization_candidates()](../DATALAN/DATALAN/views.py) |
| 4 | HU-09 | I4-P03 | Encargado de Sistemas | Ejecutar optimización | R | Técnicos y perfiles | Recupera disponibilidad/perfiles para evaluar asignación. | [get_technicians()](../DATALAN/DATALAN/optimization_service.py#L1119) |
| 4 | HU-09 | I4-P03 | Encargado de Sistemas | Ejecutar optimización | W | Configuración genética | Guarda parámetros recibidos antes de ejecutar. | [save_optimization_config()](../DATALAN/DATALAN/optimization_service.py#L142) |
| 4 | HU-09 | I4-P03 | Encargado de Sistemas | Resultado AG general | X | Recomendaciones | Muestra alternativas; no confirma asignación. | [run_genetic_optimization()](../DATALAN/DATALAN/optimization_service.py#L2426) |
| 4 | HU-10 | I4-P04 | Soporte / Sistemas | Generar equipos por etapa | E | Solicitud, etapa y horario | Recibe CITE, etapa y fechas/horas candidatas. | [generate_operational_team_proposals()](../DATALAN/DATALAN/views.py#L3165) |
| 4 | HU-10 | I4-P04 | Soporte / Sistemas | Generar propuestas | R | Solicitud y cronograma | Recupera puntos, estado y fecha límite. | [generate_operational_team_proposals()](../DATALAN/DATALAN/views.py#L3165) |
| 4 | HU-10 | I4-P04 | Soporte / Sistemas | Generar propuestas | R | Perfiles técnicos | Recupera capacidades, jornadas y ausencias. | [get_technicians()](../DATALAN/DATALAN/optimization_service.py#L1119) |
| 4 | HU-10 | I4-P04 | Soporte / Sistemas | Generar propuestas | R | Configuración y disponibilidad | Lee configuración AG y ocupaciones para evaluar candidatos. | [generate_operational_team_proposals()](../DATALAN/DATALAN/views.py#L3240) |
| 4 | HU-10 | I4-P04 | Soporte / Sistemas | Generar propuestas | W | Propuestas de equipo | Guarda alternativas y firma de horario en la solicitud. | [generate_operational_team_proposals()](../DATALAN/DATALAN/views.py#L3309) |
| 4 | HU-10 | I4-P04 | Soporte / Sistemas | Resultado de generación | X | Alternativas de equipo | Devuelve propuestas o error de disponibilidad/validación. | [run_genetic_team_optimization()](../DATALAN/DATALAN/optimization_service.py#L582) |
| 4 | HU-10? | I4-P05 | Encargado de Sistemas | Consultar registro de propuestas operativas | E | Consulta del registro | Solicita ver propuestas guardadas. | [urls.py](../DATALAN/DATALAN/urls.py#L87) |
| 4 | HU-10? | I4-P05 | Encargado de Sistemas | Consultar registro | R | Solicitud | Recupera cliente, tipo, etapa y estado del caso. | [workflow()](../DATALAN/DATALAN/views.py#L3917) |
| 4 | HU-10? | I4-P05 | Encargado de Sistemas | Consultar registro | R | Propuestas de equipo | Recupera alternativas y equipo seleccionado. | [prepare_support_ag_register_records()](../DATALAN/DATALAN/views.py#L3514) |
| 4 | HU-10? | I4-P05 | Encargado de Sistemas | Mostrar registro | X | Registro de propuestas | Presenta alternativas, horario y estado de selección. | [prepare_support_ag_register_records()](../DATALAN/DATALAN/views.py#L3514) |
| 4 | HU-13 | I4-P06 | Encargado de Sistemas | Ejecutar NSGA-II general de incidencias | E | Parámetros de ejecución | Recibe configuración y acción de ejecutar. | [workflow()](../DATALAN/DATALAN/views.py#L4292) |
| 4 | HU-13 | I4-P06 | Encargado de Sistemas | Ejecutar NSGA-II | R | Incidencias | Recupera reportes abiertos y sus estados. | [flatten_service_incidents()](../DATALAN/DATALAN/views.py#L1045) |
| 4 | HU-13 | I4-P06 | Encargado de Sistemas | Ejecutar NSGA-II | R | Perfiles y cargas | Recupera perfiles y carga activa de técnicos. | [workflow()](../DATALAN/DATALAN/views.py#L4292) |
| 4 | HU-13 | I4-P06 | Encargado de Sistemas | Ejecutar NSGA-II | R | Asignaciones/ocupaciones | Usa asignaciones activas para proyectar carga. | [prepare_technician_assignment_summaries()](../DATALAN/DATALAN/views.py) |
| 4 | HU-13/15 | I4-P06 | Encargado de Sistemas | Ejecutar NSGA-II | W | Configuración NSGA-II | Persiste parámetros enviados. | [save_incident_nsga2_config()](../DATALAN/DATALAN/optimization_service.py#L187) |
| 4 | HU-13 | I4-P06 | Encargado de Sistemas | Ejecutar NSGA-II | W | Historial de ejecuciones | Guarda run ID, parámetros y resultados. | [save_incident_nsga2_run()](../DATALAN/DATALAN/optimization_service.py#L226) |
| 4 | HU-13 | I4-P06 | Encargado de Sistemas | Resultado NSGA-II | X | Alternativas Pareto | Devuelve recomendaciones; no cambia asignaciones. | [workflow()](../DATALAN/DATALAN/views.py#L4312) |
| 4 | HU-14 | I4-P07 | Soporte / Sistemas | Generar equipo para una incidencia | E | Incidencia y horario | Recibe incidente, etapa y horario tentativo. | [generate_service_incident_team_proposals()](../DATALAN/DATALAN/views.py#L3317) |
| 4 | HU-14 | I4-P07 | Soporte / Sistemas | Generar equipo NSGA-II | R | Incidencia objetivo | Recupera reporte y estado de la incidencia. | [generate_service_incident_team_proposals()](../DATALAN/DATALAN/views.py#L3317) |
| 4 | HU-14 | I4-P07 | Soporte / Sistemas | Generar equipo NSGA-II | R | Perfiles/capacidades | Recupera técnicos y perfiles pertinentes. | [get_technicians()](../DATALAN/DATALAN/optimization_service.py#L1119) |
| 4 | HU-14 | I4-P07 | Soporte / Sistemas | Generar equipo NSGA-II | R | Carga y ocupación | Lee asignaciones e incidencias competidoras para ese horario. | [generate_service_incident_team_proposals()](../DATALAN/DATALAN/views.py#L3317) |
| 4 | HU-14/15 | I4-P07 | Soporte / Sistemas | Generar equipo NSGA-II | R | Configuración NSGA-II | Recupera parámetros usados por el algoritmo. | [get_incident_nsga2_config()](../DATALAN/DATALAN/optimization_service.py) |
| 4 | HU-14 | I4-P07 | Soporte / Sistemas | Generar equipo NSGA-II | W | Propuestas e historial de equipo | Guarda alternativas en la incidencia. | [generate_service_incident_team_proposals()](../DATALAN/DATALAN/views.py#L3317) |
| 4 | HU-14 | I4-P07 | Soporte / Sistemas | Resultado de generación | X | Alternativas de equipo | Devuelve propuestas o error de elegibilidad/horario. | [run_incident_team_nsga2()](../DATALAN/DATALAN/optimization_service.py#L1684) |
| 4 | HU-14? | I4-P08 | Encargado de Sistemas | Consultar propuestas de equipo de incidencias | E | Consulta del registro | Abre registro de propuestas guardadas. | [urls.py](../DATALAN/DATALAN/urls.py#L95) |
| 4 | HU-14? | I4-P08 | Encargado de Sistemas | Consultar registro | R | Incidencias | Recupera reporte/estado de las incidencias listadas. | [workflow()](../DATALAN/DATALAN/views.py#L3931) |
| 4 | HU-14? | I4-P08 | Encargado de Sistemas | Consultar registro | R | Propuestas de equipo | Recupera alternativas guardadas y selección aplicada. | [prepare_incident_team_proposal_register()](../DATALAN/DATALAN/views.py) |
| 4 | HU-14? | I4-P08 | Encargado de Sistemas | Mostrar registro | X | Propuestas/selección | Muestra propuestas y estados disponibles. | [prepare_incident_team_proposal_register()](../DATALAN/DATALAN/views.py) |
| 4 | HU-14 | I4-P09 | Soporte / Sistemas autorizado | Seleccionar equipo y aprobar atención | E | Propuesta elegida y horario | Recibe ID de propuesta y fecha/hora aprobadas. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1344) |
| 4 | HU-14 | I4-P09 | Soporte / Sistemas autorizado | Confirmar equipo | R | Incidencia | Comprueba reportante, estado y propuesta temporal de atención. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1344) |
| 4 | HU-14 | I4-P09 | Soporte / Sistemas autorizado | Confirmar equipo | R | Propuesta seleccionada | Valida alternativa, miembros, líder y horario generado. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1374) |
| 4 | HU-14 | I4-P09 | Soporte / Sistemas autorizado | Confirmar equipo | W | Incidencia/atención | Persiste equipo, líder, horario y aprobación. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1408) |
| 4 | HU-14 | I4-P09 | Soporte / Sistemas autorizado | Resultado de confirmación | X | Confirmación/error | Informa aprobación o rechazo de propuesta/fecha/permiso. | [handle_service_incident_workflow_post()](../DATALAN/DATALAN/views.py#L1344) |

## Asignaciones dudosas y operaciones compartidas

1. **HU-05–HU-10:** el informe local atribuye HU-05–HU-10 a Iteración 4, pero vincula HU-08 y retiro/conclusión a Iteración 2. El cuadro funcional local asigna HU-05 a responsable, HU-06 a perfiles, HU-07 a cronogramas y HU-08 a resultados. Las marcas `?` señalan esa discrepancia; cotejar con el catálogo oficial antes de cerrar trazabilidad. Véanse [auditoría ITIL, matriz de evidencias](auditoria_itil4_datalan.md#G-matriz-de-evidencias-para-la-defensa) e [INFORME_ACTUALIZADO_DATALAN.md, HU-01–HU-15](INFORME_ACTUALIZADO_DATALAN.md).
2. La selección/confirmación de equipo operativo se cuenta una sola vez en I2-P12/P15/P20: es la aprobación del cronograma que valida la propuesta guardada. P4-08 prueba la integración, pero no se duplica como W en Iteración 4.
3. La aprobación de equipo para una incidencia está en I4-P09 y es distinta de generar propuestas. La optimización general de incidencias genera alternativas, pero la vista indica que no modifica asignaciones.
4. El historial de solicitud/incidencia se agrupa con el trámite persistido; no se suma un W adicional por cada evento anidado. Si la medición autorizada modela el historial como grupo independiente, se debe recalcular cada escritura.
5. `get_incident_nsga2_history()` y un preparador de historial existen, pero no encontré conexión desde una vista a esa lectura. No se contó una consulta independiente del historial general NSGA-II. Sí se contó su W al generar, porque se persiste.
6. Existen servicios auxiliares de scheduler, pero no encontré ruta/llamada desde las vistas de la app; no se sumaron como proceso conectado al usuario ni se asignaron a Iteración 5.
7. Administración de cuentas tiene código/rutas, pero sin HU/iteración inequívoca en el cuadro local. Si se incluye en el alcance, el subtotal adicional candidato es **17 CFP**: consulta (E,R cuenta,R perfiles técnicos,X = 4); alta (E,R rol,W cuenta,W asociación de rol,X = 5); cambio de estado (E,R cuenta,W cuenta,X = 4); eliminación (E,R cuenta,W cuenta,X = 4). Hay W condicional adicional de perfil cuando la cuenta es técnica. Evidencia: [users()](../DATALAN/DATALAN/views.py#L2447), [user_create()](../DATALAN/DATALAN/views.py#L2529), [toggle_user()](../DATALAN/DATALAN/views.py#L2575), [user_delete()](../DATALAN/DATALAN/views.py#L2594).

## Subtotales respaldados

CFP = E + X + R + W. Son subtotales candidatos según los movimientos y agrupaciones anteriores, no una certificación COSMIC.

| Iteración | E | X | R | W | CFP |
|---|---:|---:|---:|---:|---:|
| 1 | 8 | 8 | 6 | 6 | **28** |
| 2 | 21 | 21 | 26 | 20 | **88** |
| 3 | 9 | 9 | 10 | 8 | **36** |
| 4 | 9 | 9 | 20 | 6 | **44** |
| **Subtotal I1–I4** | **47** | **47** | **62** | **40** | **196** |

El subtotal depende de aceptar las agrupaciones y el alcance I1–I4. La administración de cuentas añadiría 17 CFP candidatos sin asignación iterativa respaldada; scheduler e historial general NSGA-II quedan fuera por falta de conexión de usuario verificable.

## Evidencia de pruebas revisada

No se ejecutaron pruebas para preservar el modo de solo lectura. Los resultados son registros históricos:

- I1 documenta tres pruebas focalizadas aprobadas para login, permisos y persistencia de perfiles: [resultados I1](pruebas_iteracion_1/resultados.md).
- I2 documenta persistencia/recarga de solicitudes, cronogramas, conclusiones y retiro eventual: [resultados P2](pruebas_iteracion_2/resultados_p2_2026-10-31.md).
- I3 documenta reporte, asignación, atención, intentos y cierre; también aclara que no hay entidad/campo independiente de diagnóstico: [resultados P3](pruebas_iteracion_3/resultados_p3_2026-10-31.md).
- I4 documenta generación y confirmación para equipos operativos e incidencias: [reporte P4](../DATALAN/documentacion/iteracion_4/evaluacion/REPORTE_PRUEBAS_ITERACION_4.md).
- I5 no proporciona catálogo HU y reporta bloqueos; P5-15 señala un fallo al releer configuración real: [resultados I5](pruebas_iteracion_5/resultados.md). No se atribuyeron P5 a CFP adicionales.

## Despliegue y punto 3.5 de costos

- **Configuración de despliegue productivo:** no encontré manifiestos ni automatización de despliegue productivo. Hay un punto WSGI y configuración PostgreSQL, pero los ajustes generales siguen siendo de desarrollo por defecto; no demuestran despliegue productivo. Referencias: [settings.py](../DATALAN/DATALAN/settings.py#L27), [configuración WSGI/base](../DATALAN/DATALAN/settings.py#L88), [requirements.txt](../requirements.txt).
- **Recursos:** se identifican dependencias de software y PostgreSQL; no encontré dimensionamiento de CPU, RAM, almacenamiento, disponibilidad, licencias o costos de infraestructura.
- **Horas explícitas de desarrollo:** no localicé planillas, partes de horas ni una estimación trazable. No se dedujeron horas de commits ni fechas de pruebas.
- **Conclusión para el costo:** no se puede cerrar una cifra monetaria verificable para el punto 3.5 con la evidencia del repositorio. Faltan, como mínimo, horas/esfuerzo aprobados, tarifas por perfil y costos de infraestructura/licencias con fuente. No se asignan precios ni horas supuestas.
