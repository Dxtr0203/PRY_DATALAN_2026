# Correcciones realizadas — pruebas Iteración 3

Fecha: 2026-10-31.

- No se modificó lógica de producción.
- En la primera ejecución de integración, la prueba del reporte leyó la incidencia de preparación preexistente en vez de la nueva que se añadió al servicio. Se corrigió el fixture/assertion para validar el último reporte guardado; la ejecución posterior pasó.
- Se agregó una prueba PostgreSQL del flujo real de programación y registro de atención. Su primera ejecución falló porque el fixture usaba un reporte de Soporte, cuya aprobación de horario exige una propuesta de equipo. Se ajustó el fixture al rol de Encargado de Sistemas y se agregaron comprobaciones del estado persistido después de cada transición. La prueba focalizada pasó.
- La suite final contiene seis pruebas de integración PostgreSQL y tres pruebas unitarias reutilizadas (**nueve métodos**). La nueva prueba verifica persistencia SQL de trabajo programado y resultado de atención; las existentes cubren permisos, asignación, solución, revisión y cierre.
- La base configurada para la suite es exclusiva (`datalan_it3_test`) y cada prueba PostgreSQL verifica su nombre antes de ejecutar SQL directo.
- P3-08 y P3-13 se reportan como parciales: no hay campos independientes de diagnóstico u observación técnica para registrar o consultar. No se modificó el modelo ni se declaró aprobado ese alcance ausente.

La salida original de la última ejecución completa y el resultado están en [registro_ejecucion_completa_2026-10-31.txt](./registro_ejecucion_completa_2026-10-31.txt).
