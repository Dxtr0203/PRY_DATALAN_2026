# DATALAN: PostgreSQL y algoritmo genetico

## 1. Situacion actual

DATALAN actualmente mantiene las solicitudes en `workflow_service.py`, dentro de una lista global (`REQUESTS`) formada por diccionarios. Eso sirve para una demostracion, pero no es suficiente para datos reales porque:

- los datos se pierden al reiniciar el proceso;
- evaluacion tecnica, verificacion de Sistemas, asignacion, reportes e historial estan anidados como diccionarios;
- no hay claves foraneas ni restricciones de integridad;
- usuarios, roles y permisos viven parcialmente en memoria o en la sesion;
- no se puede auditar correctamente quien cambio cada estado.

El script `docs/postgresql_schema.sql` separa esas responsabilidades en tablas relacionadas. La tabla central es `operational_request`.

## 2. Modelo normalizado

La relacion principal es:

`app_user -> user_role -> role -> role_module -> module`

`client -> operational_request <- service_type, priority, request_status`

`operational_request -> technical_evaluation`

`operational_request -> systems_verification -> verification_equipment -> equipment`

`operational_request -> work_assignment -> assignment_member -> app_user`

`work_assignment -> work_report`

`operational_request -> incident`

`genetic_run -> genetic_run_request -> operational_request`

`genetic_run -> genetic_candidate -> genetic_solution_gene`

Esta separacion evita repetir nombres de clientes, estados, prioridades, equipos y usuarios en cada solicitud.

## 3. Donde se recaban los datos actualmente

### Comercial: registro de solicitud

La captura esta en `DATALAN/templates/workflow.html`, en la rama `screen == 'new_request'`. Los campos actuales son:

- solicitante, correo y empresa asociada;
- tipo de solicitud;
- prioridad;
- origen, destino e instalacion;
- coordenadas y ubicaciones;
- velocidad, equipos y requisitos.

El POST se procesa en `DATALAN/views.py`, dentro de `workflow()`, en la rama `screen == 'new_request'`. Hoy crea el diccionario `item` y lo agrega a `REQUESTS`. Con PostgreSQL debe crear, dentro de una transaccion:

1. cliente o entidad en `client`;
2. direcciones en `address`;
3. contacto en `request_contact`;
4. solicitud en `operational_request`;
5. estado inicial en `request_status_history`.

### Comercial: derivacion y rechazo

Las ramas `forward_request` y `reject_request` de `workflow()` actualizan el estado y agregan historial. En PostgreSQL deben hacer un `UPDATE operational_request` y un `INSERT request_status_history` dentro de la misma transaccion.

### Encargado de Planta Tecnica: evaluacion

La captura esta en la rama `screen == 'plant_evaluate'` de `workflow.html`. Recaba:

- distancia;
- cobertura;
- infraestructura;
- tendido;
- tipo y cantidad de fibra;
- dificultad;
- materiales;
- observaciones;
- factibilidad.

Debe guardarse en `technical_evaluation`, sin sobrescribir evaluaciones anteriores. Si se permite reevaluar, cada evaluacion conserva su fecha y responsable, y la mas reciente aprobada se usa como resultado vigente.

### Encargado de Sistemas: verificacion

La captura esta en `screen == 'systems_verify'`. Recaba disponibilidad, compatibilidad, equipos, requerimientos adicionales, observaciones y resultado. Debe guardarse en `systems_verification` y sus equipos seleccionados en `verification_equipment`.

### Encargado de Sistemas: asignacion

La captura esta en `screen == 'assignment'`. Recaba tecnico lider, tecnicos adicionales y fecha programada. Debe crear `work_assignment` y sus integrantes en `assignment_member`. El lider debe ser un registro de `app_user` con rol tecnico o soporte valido.

### Tecnico y Soporte: reporte de trabajo

La captura esta en `screen == 'work_report'`. Recaba inicio, finalizacion, actividades, materiales usados, problemas y resultado. Debe insertarse en `work_report`; el estado de la solicitud se actualiza y se registra en `request_status_history`.

### Historial

Cada cambio de estado, evaluacion, asignacion y reporte debe producir una entrada en `request_status_history`. Ese historial es la fuente correcta para trazabilidad, auditoria y futuras metricas.

## 4. Donde se vera el funcionamiento

- Administrador, `Inicio`: conteos por `request_status`, `service_type`, instalaciones, retiros e incidencias.
- Administrador, `Actividad reciente`: consulta ordenada de `request_status_history` y de solicitudes actualizadas.
- Comercial, `Inicio` y `Solicitudes`: solicitudes por estado comercial.
- Encargado de Planta Tecnica, `Solicitudes`, `Trabajos` e `Incidencias`: evaluaciones y resultados tecnicos.
- Encargado de Sistemas, `Solicitudes`, `Trabajos`, `Soporte` e `Incidencias`: verificaciones, asignaciones y disponibilidad.
- Tecnico y Soporte, `Mis trabajos`: asignaciones y reportes.
- Administrador, `Roles / Accesos`: relaciones `role`, `module` y `role_module`.

Cada dashboard debe leer consultas agregadas de PostgreSQL, no listas globales ni diccionarios de la sesion.

## 5. Idea del algoritmo genetico permutacional

El algoritmo no debe reemplazar el flujo de aprobacion. Debe ejecutarse cuando una solicitud ya sea factible, haya pasado la verificacion de Sistemas y este lista para asignacion/programacion.

### Cromosoma

Usa una permutacion de solicitudes elegibles:

`[R-104, R-101, R-109, R-103, R-107]`

Cada gen representa una solicitud y la posicion representa el orden de atencion. Una solucion extendida puede tener pares:

`[(solicitud, tecnico, fecha), ...]`

La permutacion debe conservar cada solicitud una sola vez. Para cruces usa un operador que conserve permutaciones, por ejemplo OX (Order Crossover) o PMX (Partially Mapped Crossover). Para mutacion usa intercambio de dos posiciones, insercion o inversion.

### Poblacion inicial

Se recaban desde PostgreSQL:

```sql
SELECT r.request_id, r.priority_id, p.weight, wa.scheduled_date,
       r.installation_address_id, r.service_type_id
FROM datalan.operational_request r
JOIN datalan.priority p ON p.priority_id = r.priority_id
LEFT JOIN datalan.work_assignment wa ON wa.request_id = r.request_id
JOIN datalan.request_status s ON s.status_id = r.current_status_id
WHERE s.status_key IN ('APROBADA', 'ASIGNADA')
  AND r.concluded_at IS NULL;
```

El algoritmo tambien necesita disponibilidad de tecnicos, carga diaria, distancia entre puntos, duracion estimada y materiales/equipos disponibles. Esas variables deben modelarse antes de buscar una solucion optima. Una futura ampliacion recomendable es agregar `technician_availability`, `technician_skill`, `service_duration_estimate` y `equipment_stock_movement`.

### Funcion de aptitud

Conviene minimizar un costo total:

$$
F = w_p C_{prioridad} + w_t C_{retraso} + w_d C_{distancia}
  + w_c C_{carga} + w_e C_{equipo} + w_v C_{violaciones}
$$

Donde:

- `C_prioridad`: penaliza atender tarde solicitudes de prioridad Alta;
- `C_retraso`: diferencia entre fecha prometida y fecha programada;
- `C_distancia`: kilometros o tiempo de traslado;
- `C_carga`: penaliza sobrecargar al mismo tecnico;
- `C_equipo`: penaliza programar sin disponibilidad suficiente;
- `C_violaciones`: penalizacion grande para restricciones duras.

Las restricciones duras deben invalidar o penalizar fuertemente una solucion: no repetir solicitudes, tecnico no disponible, solicitud no factible, falta de equipo, fecha anterior a hoy o dos trabajos simultaneos para el mismo tecnico.

### Flujo recomendado

1. Sistemas marca una solicitud como `APROBADA`.
2. Encargado de Sistemas abre una pantalla nueva: `Optimizar asignacion`.
3. El backend selecciona solicitudes elegibles y tecnicos disponibles.
4. Crea un registro en `genetic_run` con poblacion, generaciones, tasas y pesos.
5. Guarda la entrada usada en `genetic_run_request` para que el resultado sea reproducible.
6. Ejecuta seleccion, cruce OX/PMX, mutacion por intercambio y elitismo.
7. Guarda los mejores candidatos en `genetic_candidate` y su detalle en `genetic_solution_gene`.
8. Muestra la mejor solucion con costo, penalizaciones, fecha, tecnico y solicitudes.
9. El encargado revisa y confirma. Solo entonces se crean o actualizan `work_assignment` y `assignment_member`.
10. La confirmacion se registra en `genetic_solution_application` y cada asignacion genera historial.

Nunca conviene aplicar automaticamente el mejor cromosoma sin una confirmacion humana: el algoritmo optimiza los datos disponibles, pero una restriccion operacional puede no estar registrada.

## 6. Donde se recaban y donde se observa el algoritmo

### Captura

- Parametros del algoritmo: nueva pantalla para Encargado de Sistemas, asociada a `genetic_run`.
- Solicitudes de entrada: se seleccionan desde Trabajos/Solicitudes aprobadas.
- Disponibilidad: nueva pantalla o catalogo para tecnicos, fechas y equipos.
- Restricciones y pesos: formulario de configuracion del run.

### Resultado

- Resumen del run: estado, generaciones, mejor fitness y fecha de ejecucion.
- Tabla de solucion: posicion, CITE, cliente, tecnico, fecha y costo local.
- Comparacion: fitness por generacion y penalizaciones.
- Accion final: `Aplicar solucion`, que crea asignaciones reales.

La pantalla puede vivir en `sistemas_encargado` como `Optimización` y aparecer en `Roles / Accesos` como modulo controlable. El Administrador puede consultar resultados, pero la aplicacion de la solucion debe quedar restringida al Encargado de Sistemas.

## 7. Migracion de la aplicacion

Orden recomendado:

1. Crear una app Django, por ejemplo `operations`.
2. Configurar PostgreSQL en `settings.py` mediante variables de entorno.
3. Convertir las tablas del script en modelos Django y ejecutar migraciones.
4. Reemplazar `get_requests()` y `save_requests()` por servicios de consultas y transacciones.
5. Migrar los cuatro registros de demostracion a las tablas normalizadas.
6. Cambiar cada POST de `workflow()` para guardar en su tabla correspondiente.
7. Cambiar los dashboards para usar agregaciones SQL.
8. Crear un servicio separado, por ejemplo `genetic_service.py`, que solo lea solicitudes elegibles y escriba runs/candidatos.
9. Agregar pruebas de transiciones de estado, permisos, integridad y reproducibilidad del algoritmo.

### Inicializacion de tu base `datalan`

El proyecto ya esta configurado para `127.0.0.1:5432`, base `datalan` y usuario `postgres`. La contrasena se lee exclusivamente desde `DATALAN_DB_PASSWORD`.

En PowerShell, desde la carpeta del proyecto, escribe tu contrasena directamente en la terminal:

```powershell
$env:DATALAN_DB_NAME = 'datalan'
$env:DATALAN_DB_USER = 'postgres'
$env:DATALAN_DB_PASSWORD = 'TU_CONTRASENA_LOCAL'
$env:DATALAN_DB_HOST = '127.0.0.1'
$env:DATALAN_DB_PORT = '5432'
& .\venv\Scripts\python.exe .\scripts\init_postgresql.py
& .\venv\Scripts\python.exe .\DATALAN\manage.py migrate
```

El primer comando crea el esquema `datalan`, tablas, catalogos y usuarios demo. El segundo crea las tablas internas de Django en el mismo `search_path`. No pongas la contrasena en `settings.py`, `.env.example` ni en el repositorio.

En el estado actual, `workflow_service.py` usa PostgreSQL para leer solicitudes y guarda sus datos operativos en `operational_request.extra_data` mientras se termina el reemplazo de los diccionarios anidados por escrituras en `technical_evaluation`, `systems_verification`, `work_assignment` y `work_report`. La estructura normalizada ya esta creada para esa siguiente migracion; no se debe eliminar `extra_data` hasta comprobar que todos los formularios fueron trasladados.

Configuracion PostgreSQL de ejemplo:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DATALAN_DB_NAME'],
        'USER': os.environ['DATALAN_DB_USER'],
        'PASSWORD': os.environ['DATALAN_DB_PASSWORD'],
        'HOST': os.environ.get('DATALAN_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DATALAN_DB_PORT', '5432'),
        'OPTIONS': {'options': '-c search_path=datalan,public'},
    }
}
```

Dependencias:

```text
Django
psycopg[binary]
```

## 8. Nota sobre el documento adjunto

El archivo DOCX adjunto no queda disponible como archivo legible dentro del workspace en esta sesion. Por eso esta propuesta usa como fuente verificable el flujo existente de DATALAN: los formularios de `workflow.html`, el procesamiento de `views.py` y las estructuras de `workflow_service.py`. Cuando el contenido completo de la investigacion este disponible, sus restricciones, pesos y operadores pueden incorporarse en `objective_weights`, `genetic_run` y el servicio genetico sin cambiar el modelo operacional principal.
