# Evaluación controlada de recomendaciones de DATALAN

## Alcance y reproducibilidad

- Ejecución real: `2026-10-27T09:58:58-04:00`.
- Conjunto único: `DATALAN-SIM-20261027-A`; los datos son completamente ficticios y están guardados completos en [datos_ficticios.json](./datos_ficticios.json).
- Reproducir las 12 llamadas medidas: `python docs/evaluacion_recomendaciones/reproducir_evaluacion.py` desde la raíz del repositorio. El script usa exclusivamente las funciones de algoritmo del proyecto; no llama a las vistas, PostgreSQL, ni modifica código o registros.
- Semillas: `101, 202, 303`. Para cada modalidad se mantuvieron datos y configuración iguales; solo cambió `random_seed`.
- Configuraciones fijas: algoritmo general `{'population_size': 40, 'generations': 100, 'mutation_percent': 10, 'crossover_percent': 80}`; algoritmos NSGA-II `{'population_size': 48, 'generations': 80, 'mutation_percent': 15, 'crossover_percent': 85}`. Cruce y mutación en la tabla se expresan como porcentajes configurados.
- El horario simulado de la asignación de incidencias es `2026-10-27T08:30:00`; el horario fijo del caso de equipo es `2026-10-28T10:00:00`. No se cambió el reloj del sistema.
- El tiempo es `perf_counter` alrededor de la llamada Python al algoritmo y se expresa en segundos. No representa duración de atención ni tiempo del servicio.
- Resultados completos de cada llamada, semillas, configuración, tiempos, historial y alternativas: [ejecuciones.json](./ejecuciones.json).

## Definición verificada de las métricas y objetivos

1. **GA de solicitudes:** fitness de `0` a `100`, mayor es mejor. En el modo operativo del conjunto sintético, el fitness combina prioridad `25%`, tiempo ponderado `20%`, distancia `15%`, carga `15%` y fitness medio de equipos `25%`, multiplicados por la cobertura. La cobertura es porcentaje de solicitudes con técnico/equipo asignado. El gráfico registra el mejor fitness de la población por generación.
2. **NSGA-II de incidencias:** objetivo 1 = suma de minutos de espera hasta el siguiente inicio de jornada, multiplicada por el peso de urgencia, dividida entre 60 (`h ponderadas`, minimizar). Objetivo 2 = suma de `(carga proyectada - carga media)^2` entre técnicos (`asignaciones^2`, minimizar); carga proyectada incluye trabajos activos y asignaciones propuestas. Pesos de urgencia son factores adimensionales de la regla de severidad/antigüedad.
3. **NSGA-II de equipo para horario fijo:** el código minimiza `(100 - fitness, carga_media_proyectada)`. El fitness (puntos, 0-100) se calcula con capacidades 50%, liderazgo 20%, experiencia 15%, carga 10% y distancia 5%. La carga media es el promedio de carga activa más una asignación propuesta entre integrantes del equipo (`asignaciones/técnico`). Ambos objetivos se minimizan. El gráfico muestra alternativas devueltas por el algoritmo, no las rotula como un frente global: la salida puede tomar puntos de frentes posteriores si el primero contiene menos de tres.
4. **GA de equipo operativo:** el fitness es el puntaje ponderado de capacidades 50%, liderazgo 20%, experiencia 15%, carga 10% y distancia 5%; mayor es mejor. En esta modalidad la recomendación es un conjunto de hasta tres equipos archivados, no un frente de Pareto. Se informa cobertura de personal/déficit del equipo.

## Tabla de ejecuciones

Los campos “solicitudes/incidencias/técnicos” indican el tamaño del conjunto común completo, aunque una modalidad use solo una de esas colecciones. “Alternativas” es el número devuelto por la implementación en esa ejecución. “Fitness u objetivos” conserva el sentido de optimización; para NSGA se listan objetivos de cada alternativa devuelta, no se afirma que todas pertenezcan al frente global.

| Código | Modalidad | Conjunto y cantidades | Población | Generaciones | Cruce | Mutación | Semilla | Alternativas | Cobertura o déficit | Fitness u objetivos y alternativas | Tiempo real (s) | Estado |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| IT2-EVAL-SOL-101 | GA solicitudes por permutación | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 40 | 100 | 80% | 10% | 101 | 3 | 100.0% / 0 sin asignar | Fitness mejor 72.41 (mayor es mejor); 1: fitness 72.41, cobertura 100.0%, sin asignar 0; 2: fitness 72.02, cobertura 100.0%, sin asignar 0; 3: fitness 71.63, cobertura 100.0%, sin asignar 0 | 7.773233 | OK |
| IT2-EVAL-INC-101 | NSGA-II asignación de incidencias | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 48 | 80 | 85% | 15% | 101 | 3 | 6/6 incidencias asignadas; 8 técnicos elegibles | Minimizar horas ponderadas por urgencia y suma de desviaciones cuadráticas de carga; A1: espera ponderada 0.0 h, desequilibrio 15.5; A2: espera ponderada 0.0 h, desequilibrio 15.5; A3: espera ponderada 0.0 h, desequilibrio 15.5 | 0.215340 | OK |
| IT2-EVAL-EQ-101 | NSGA-II equipo de incidencia, horario fijo | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 48 | 80 | 85% | 15% | 101 | 3 | 6 técnicos elegibles; alternativas de 2-3 personas sin déficit de capacidades | Minimizar 100 - fitness (puntos) y carga media proyectada (asignaciones por técnico); A1: fitness 89.3, objetivos (10.700000000000003, 1.5); A2: fitness 88.74, objetivos (11.260000000000005, 1.33); A3: fitness 76.58, objetivos (23.42, 1.0) | 0.457759 | OK |
| IT2-EVAL-TEAM-101 | GA equipo operativo para solicitud | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 40 | 100 | 80% | 10% | 101 | 3 | 6 técnicos compatibles; equipo 4/4, déficit 0 | Fitness mejor 90.51 (mayor es mejor); A1: fitness 90.51, equipo 4/4, déficit 0; A2: fitness 89.94, equipo 4/4, déficit 0; A3: fitness 89.13, equipo 4/4, déficit 0 | 0.953353 | OK |
| IT2-EVAL-SOL-202 | GA solicitudes por permutación | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 40 | 100 | 80% | 10% | 202 | 3 | 100.0% / 0 sin asignar | Fitness mejor 72.41 (mayor es mejor); 1: fitness 72.41, cobertura 100.0%, sin asignar 0; 2: fitness 72.02, cobertura 100.0%, sin asignar 0; 3: fitness 71.63, cobertura 100.0%, sin asignar 0 | 6.636766 | OK |
| IT2-EVAL-INC-202 | NSGA-II asignación de incidencias | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 48 | 80 | 85% | 15% | 202 | 3 | 6/6 incidencias asignadas; 8 técnicos elegibles | Minimizar horas ponderadas por urgencia y suma de desviaciones cuadráticas de carga; A1: espera ponderada 0.0 h, desequilibrio 15.5; A2: espera ponderada 0.0 h, desequilibrio 15.5; A3: espera ponderada 0.0 h, desequilibrio 15.5 | 0.159431 | OK |
| IT2-EVAL-EQ-202 | NSGA-II equipo de incidencia, horario fijo | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 48 | 80 | 85% | 15% | 202 | 3 | 6 técnicos elegibles; alternativas de 2-3 personas sin déficit de capacidades | Minimizar 100 - fitness (puntos) y carga media proyectada (asignaciones por técnico); A1: fitness 89.3, objetivos (10.700000000000003, 1.5); A2: fitness 88.74, objetivos (11.260000000000005, 1.33); A3: fitness 76.58, objetivos (23.42, 1.0) | 0.372150 | OK |
| IT2-EVAL-TEAM-202 | GA equipo operativo para solicitud | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 40 | 100 | 80% | 10% | 202 | 3 | 6 técnicos compatibles; equipo 4/4, déficit 0 | Fitness mejor 90.51 (mayor es mejor); A1: fitness 90.51, equipo 4/4, déficit 0; A2: fitness 89.94, equipo 4/4, déficit 0; A3: fitness 89.13, equipo 4/4, déficit 0 | 0.798557 | OK |
| IT2-EVAL-SOL-303 | GA solicitudes por permutación | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 40 | 100 | 80% | 10% | 303 | 3 | 100.0% / 0 sin asignar | Fitness mejor 72.41 (mayor es mejor); 1: fitness 72.41, cobertura 100.0%, sin asignar 0; 2: fitness 72.02, cobertura 100.0%, sin asignar 0; 3: fitness 71.63, cobertura 100.0%, sin asignar 0 | 6.706821 | OK |
| IT2-EVAL-INC-303 | NSGA-II asignación de incidencias | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 48 | 80 | 85% | 15% | 303 | 3 | 6/6 incidencias asignadas; 8 técnicos elegibles | Minimizar horas ponderadas por urgencia y suma de desviaciones cuadráticas de carga; A1: espera ponderada 0.0 h, desequilibrio 15.5; A2: espera ponderada 0.0 h, desequilibrio 15.5; A3: espera ponderada 0.0 h, desequilibrio 15.5 | 0.174324 | OK |
| IT2-EVAL-EQ-303 | NSGA-II equipo de incidencia, horario fijo | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 48 | 80 | 85% | 15% | 303 | 3 | 6 técnicos elegibles; alternativas de 2-3 personas sin déficit de capacidades | Minimizar 100 - fitness (puntos) y carga media proyectada (asignaciones por técnico); A1: fitness 89.3, objetivos (10.700000000000003, 1.5); A2: fitness 88.74, objetivos (11.260000000000005, 1.33); A3: fitness 76.58, objetivos (23.42, 1.0) | 0.413070 | OK |
| IT2-EVAL-TEAM-303 | GA equipo operativo para solicitud | DATALAN-SIM-20261027-A (6 solicitudes, 6 incidencias, 8 técnicos) | 40 | 100 | 80% | 10% | 303 | 3 | 6 técnicos compatibles; equipo 4/4, déficit 0 | Fitness mejor 90.51 (mayor es mejor); A1: fitness 90.51, equipo 4/4, déficit 0; A2: fitness 89.94, equipo 4/4, déficit 0; A3: fitness 89.13, equipo 4/4, déficit 0 | 0.902547 | OK |

## Variación observada por modalidad

Los rangos siguientes comparan únicamente las tres semillas de la misma modalidad. No se comparan escalas de fitness entre modalidades ni se infiere una mejora del servicio real:

- **IT2-EVAL-SOL:** fitness final: mín. 72.41; máx. 72.41; rango 0.00; 1 valor(es) distinto(s) en 3 corrida(s).
- **IT2-EVAL-INC:** horas ponderadas de la primera alternativa devuelta: mín. 0.00; máx. 0.00; rango 0.00; 1 valor(es) distinto(s) en 3 corrida(s).
- **IT2-EVAL-EQ:** 100 - fitness de la primera alternativa devuelta: mín. 10.70; máx. 10.70; rango 0.00; 1 valor(es) distinto(s) en 3 corrida(s).
- **IT2-EVAL-TEAM:** fitness de la primera propuesta devuelta: mín. 90.51; máx. 90.51; rango 0.00; 1 valor(es) distinto(s) en 3 corrida(s).

## Gráficos y alcance de interpretación

- [Fitness por generación — GA solicitudes](./fitness_generacional_solicitudes.png): líneas de las tres semillas; cada punto proviene del historial devuelto por esa ejecución.
- [Objetivos — NSGA-II incidencias](./objetivos_nsga2_incidencias.png): alternativas coincidentes se muestran con anillos concéntricos y su cantidad; ejes en unidades verificadas arriba.
- [Objetivos — NSGA-II equipos con horario fijo](./objetivos_nsga2_equipo_horario_fijo.png): alternativas coincidentes se muestran con anillos concéntricos y su cantidad; no se afirma que todas pertenezcan al frente global.
- Los tres PNG se generan con valores del JSON. El renderizador usa biblioteca estándar; no dibuja datos ilustrativos ni introduce puntos sintéticos.

## Errores e impedimentos

- No hubo corridas fallidas.

No se ejecutaron solicitudes a la aplicación ni accesos a la base operativa. Estos experimentos miden recomendaciones algorítmicas sobre fixtures ficticios, no calidad de atención, efectividad del servicio ni resultados en producción.
