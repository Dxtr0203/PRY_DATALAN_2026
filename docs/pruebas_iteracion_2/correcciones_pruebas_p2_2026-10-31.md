# Registro de correcciones de pruebas — Iteracion 2

Fecha: 2026-10-31.

Se corrigieron fixtures y utilidades de las pruebas de integracion; no se modifico la logica de produccion:

1. La primera ejecucion de las siete pruebas PostgreSQL encontro que el esquema minimo omitio `updated_at`, columna que el `ON CONFLICT` de `save_requests()` actualiza. Se agrego la columna al esquema aislado de prueba.
2. La consulta SQL directa devolvio `extra_data` JSONB como texto en ese cursor; el helper de evidencia ahora decodifica JSON antes de comprobar los campos.
3. La fixture de conclusion permanente carecia de puntos de trabajo, precondicion real del manejador de etapas. Se agregaron origen y destino ficticios.
4. La primera ejecucion combinada encontro un nombre de variable residual al simplificar el helper de registro. Se elimino la referencia y se repitio la corrida.
5. Una asercion focalizada verifico que, despues de aprobar la conclusion permanente, el listado comercial mostraba `APROBADO` en vez de `ACTIVO`. Se corrigio `prepare_commercial_link_records()` para derivar `ACTIVO` solo si la instalacion y la conclusion estan aprobadas y la solicitud esta `FINALIZADA`. El test focalizado y la corrida completa posterior pasaron.

**Validacion final:** la corrida completa seleccionada esta registrada en [registro_ejecucion_completa_2026-10-31.txt](./registro_ejecucion_completa_2026-10-31.txt): 16 pruebas, `OK`, codigo de retorno `0`. El cambio se limita al estado derivado que presenta el listado; no se agrego una columna ni se altero el estado transaccional de PostgreSQL.
