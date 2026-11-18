# Comprobaciones de la Iteración 1

**Fecha de ejecución:** 31/10/2026  
**Base de pruebas:** PostgreSQL `datalan_it1_test` en `127.0.0.1:5432`. La configuración de prueba fija este nombre, y las pruebas confirman `current_database()` antes de crear datos. Django crea y elimina esa base de pruebas al ejecutar el conjunto; no se usa la base de la aplicación.

| Código | Comprobación | Fecha | Resultado obtenido | Estado | Evidencia |
|---|---|---|---|---|---|
| I1-01 | Inicio de sesión, rutas para los cinco roles y rechazo de credenciales incorrectas sin sesión autenticada | 31/10/2026 | Ejecución individual: `Ran 1 test`, `OK`, código de proceso 0 | Aprobado | `test_i1_01_login_role_destinations_and_rejected_credentials`; [I1-01_salida.txt](./I1-01_salida.txt) |
| I1-02 | Consulta y actualización de ambos perfiles por Planta Técnica; denegación de acceso directo a Técnico sin alterar los JSONB | 31/10/2026 | Ejecución individual: `Ran 1 test`, `OK`, código de proceso 0 | Aprobado | `test_i1_02_server_permission_for_profile_reads_and_updates`; [I1-02_salida.txt](./I1-02_salida.txt) |
| I1-03 | Actualización y nueva consulta PostgreSQL de datos generales, capacidades operativas y de incidencias; verificación de técnico seleccionado y capacidades compartidas OTDR/fusiones | 31/10/2026 | Ejecución individual: `Ran 1 test`, `OK`, código de proceso 0 | Aprobado | `test_i1_03_profile_jsonb_persists_and_shared_capabilities_match`; [I1-03_salida.txt](./I1-03_salida.txt) |

## Correcciones durante la preparación

La primera ejecución encontró que el cursor PostgreSQL devuelve los campos JSONB como texto en esta configuración. El arnés de prueba intentaba compararlos directamente con diccionarios; se corrigió la lectura de evidencia para decodificar el JSON antes de comparar. No fue un fallo de la aplicación ni se modificó su lógica. En la ejecución final conjunta, las tres comprobaciones terminaron `ok` (`Ran 3 tests`, `OK`, código de proceso 0).

## Evidencia individual en terminal

Las tres comprobaciones se ejecutaron también por separado el 31/10/2026. Cada salida individual está guardada en el TXT indicado en la tabla. Para reproducirlas y capturar cada resultado en tiempo real, abre PowerShell en la raíz del repositorio y ejecuta estos comandos **uno a la vez**:

**I1-01 — Inicio de sesión**

```powershell
& .\venv\Scripts\python.exe .\DATALAN\manage.py test DATALAN.test_iteration1.Iteration1PostgreSQLTests.test_i1_01_login_role_destinations_and_rejected_credentials --settings=DATALAN.settings_iteration1_test --verbosity 2
```

**I1-02 — Control de permisos**

```powershell
& .\venv\Scripts\python.exe .\DATALAN\manage.py test DATALAN.test_iteration1.Iteration1PostgreSQLTests.test_i1_02_server_permission_for_profile_reads_and_updates --settings=DATALAN.settings_iteration1_test --verbosity 2
```

**I1-03 — Guardado y consulta de perfiles**

```powershell
& .\venv\Scripts\python.exe .\DATALAN\manage.py test DATALAN.test_iteration1.Iteration1PostgreSQLTests.test_i1_03_profile_jsonb_persists_and_shared_capabilities_match --settings=DATALAN.settings_iteration1_test --verbosity 2
```

Para cada screenshot, encuadra el comando ejecutado, la línea larga con el nombre `test_i1_... ... ok` y el resumen `Ran 1 test` / `OK`. Puedes maximizar la terminal antes de ejecutar; espera a que el comando termine para que también se vea `System check identified no issues`.

## Repetir la ejecución en PowerShell

Desde la raíz del repositorio:

```powershell
& $env:ComSpec /c '"venv\Scripts\python.exe" "DATALAN\manage.py" test "DATALAN.test_iteration1" --settings="DATALAN.settings_iteration1_test" --verbosity 2 > "docs\pruebas_iteracion_1\salida_ultima_ejecucion.txt" 2>&1'; $testExitCode = $LASTEXITCODE; Get-Content 'docs\pruebas_iteracion_1\salida_ultima_ejecucion.txt'; if ($testExitCode -ne 0) { exit $testExitCode }
```

La configuración de prueba dirige las consultas SQL directas al mismo PostgreSQL aislado. Para la captura de terminal, incluye desde `Creating test database for alias 'default' ('datalan_it1_test')` hasta los tres nombres de prueba con `ok`, `Ran 3 tests`, `OK` y `System check identified no issues`.
