# Iteración 4: NSGA-II para la optimización de incidencias

## Propósito y alcance

Este documento explica cómo el sistema aplica **NSGA-II** (*Non-dominated Sorting Genetic Algorithm II*) a las incidencias de servicio. Se organiza con las fases habituales de **CRISP-DM** para poder integrarlo en la documentación de la iteración. Si el formato académico del proyecto usa el acrónimo «CRISP-DN», se puede adaptar el encabezado institucional; las fases descritas aquí corresponden a CRISP-DM.

El código contiene dos usos relacionados de NSGA-II:

1. **Optimización global de incidencias**: asigna cada incidencia abierta a un técnico compatible y genera planes alternativos. La implementa `run_incident_nsga2`.
2. **Propuesta de equipo para una incidencia y horario concretos**: busca equipos de dos o tres técnicos para un horario tentativo. La implementa `run_incident_team_nsga2`.

La pantalla **Sistemas → Incidencias → Optimización** utiliza el primer modo. El flujo de etapas de atención/solución de una incidencia utiliza el segundo modo al solicitar una propuesta de equipo. Ambos leen la configuración NSGA-II independiente de la optimización genética de solicitudes.

La implementación se encuentra en `DATALAN/optimization_service.py`; las llamadas de interfaz y operación se encuentran en `DATALAN/views.py`.

## 1. Comprensión del negocio

### Problema

La asignación de incidencias tiene objetivos que compiten:

- Reducir la espera, dando más peso a las incidencias urgentes.
- Evitar que todas las nuevas incidencias se concentren en los técnicos que ya tienen más carga.

Un único puntaje ponderado obligaría a fijar por anticipado cuánto vale reducir la espera frente a equilibrar la carga. NSGA-II, en cambio, busca soluciones no dominadas para ofrecer planes con distintos compromisos entre esos objetivos. La persona encargada compara las alternativas y decide cómo proceder.

### Objetivos de la iteración

- Excluir personal que no cumple las condiciones operativas y de capacidad.
- Generar alternativas factibles para las incidencias abiertas.
- Identificar el frente de Pareto y conservar diversidad entre planes.
- Mostrar la espera estimada, la carga proyectada y las alternativas resultantes.
- No asignar automáticamente una incidencia ni reservar horarios al ejecutar la optimización.

## 2. Comprensión de los datos

### Entradas del modo global

Las incidencias se obtienen de las incidencias de servicio registradas en las solicitudes. El modo global excluye los estados `CERRADA` y `PENDIENTE DE VALIDACIÓN`; los demás estados entran en la optimización si están presentes en los datos recibidos.

Para cada incidencia se usan:

- Identificador y CITE asociado.
- Descripción de la falla.
- Estado y fecha/hora de reporte.
- Severidad o prioridad, si existe.
- Técnico responsable, cuando esté registrado.

Para cada técnico se usan:

- Tipo de usuario, estado operativo y disponibilidad.
- Capacidades para incidencias.
- Capacidades compartidas del perfil operativo (OTDR y fusiones).
- Días y horas de trabajo y ausencias.
- Carga de trabajos activos y cantidad de incidencias ya asignadas.

### Inferencia de capacidades requeridas

El texto de la incidencia se normaliza (minúsculas y eliminación de diacríticos) y se examina con patrones. Siempre se requieren diagnóstico y registro de resolución. Además:

| Texto detectado | Capacidad añadida |
|---|---|
| `otdr` | Usar OTDR e interpretar mediciones |
| Medición, pérdida de señal o potencia | Interpretar mediciones |
| Fusión o fusionar | Realizar fusiones |
| Cable, fibra, rotura o corte | Reparar/sustituir cable |
| Empalme, conexión o conector | Reparar empalmes y conexiones |
| Equipo, router, ONT o SFP | Revisar/sustituir equipos |

OTDR y fusiones se leen de la ficha operativa compartida. Las demás capacidades provienen del perfil de incidencias. Para ser elegible, cada capacidad requerida debe estar evaluada como `CON_APOYO` o `SIN_APOYO`; `SIN_EVALUAR` y `NO_REALIZA` no satisfacen el requisito.

### Urgencia

La severidad se convierte a un peso numérico:

- Crítica, urgente o alta: 4.
- Media o moderada: 2.
- Baja: 1.

Si no hay una severidad reconocible, se deriva de la antigüedad del reporte: comienza en 1, aumenta una unidad por cada dos días transcurridos y llega como máximo a 4. Si la fecha no puede interpretarse, el peso es 1.

### Disponibilidad temporal

En el modo global se determina para cada técnico elegible el siguiente inicio de jornada disponible, buscando hasta 366 días. El inicio puede ser la hora actual (si está dentro de la jornada) o el comienzo de un día laborable futuro. Una ausencia que cubre ese instante desplaza la búsqueda al final de la ausencia; si no se encuentra un inicio, el técnico no se considera elegible.

Esto es una estimación de **siguiente inicio disponible**, no un calendario completo de ocupación. El modo global no modela la duración de la reparación ni desplaza sucesivamente el inicio por cada incidencia del mismo plan.

## 3. Preparación de los datos

### Modo global

1. Se eliminan incidencias cerradas y pendientes de validación.
2. Se valida población, generaciones, mutación y cruce.
3. Se filtran técnicos de tipo `TÉCNICO`, activos, disponibles y con un siguiente inicio de jornada válido.
4. Para cada incidencia se identifican las capacidades requeridas y se construye su conjunto de técnicos compatibles.
5. Si no hay técnicos elegibles en general o una incidencia carece de candidatos compatibles, la ejecución se detiene con un error explicativo; no se genera un plan que viole las capacidades.
6. Se toma la carga base de los trabajos activos y se incorporan las incidencias existentes asignadas a cada técnico.

Cada incidencia debe tener al menos una opción; cada gen del individuo solo podrá elegir dentro de las opciones válidas para esa incidencia.

### Modo de propuesta de equipo

La propuesta para una etapa evalúa una incidencia concreta en una fecha/hora tentativa. Solo se consideran técnicos que:

- Sean de tipo `TÉCNICO`, activos y disponibles.
- Tengan jornada configurada y trabajen en el día y horario tentativos.
- No estén de ausencia en ese instante.
- No tengan una ocupación de trabajo o una hora de atención/solución incompatible en ese instante.

La propuesta requiere al menos dos técnicos disponibles. Se evalúan equipos de dos y tres miembros; todo equipo debe cubrir, colectivamente, todas las capacidades requeridas. El tamaño del equipo es un genotipo de ejecución separado: el algoritmo evoluciona por separado las poblaciones de tamaño 2 y de tamaño 3.

## 4. Modelado

### Configuración predeterminada

| Parámetro | Predeterminado | Rango permitido |
|---|---:|---:|
| Población | 48 | 2–200 |
| Generaciones | 80 | 1–500 |
| Mutación | 15 % | 0–100 % |
| Cruce | 85 % | 0–100 % |

La configuración se guarda bajo la clave `incident_nsga2`, separada de la clave `genetic` del algoritmo genético permutacional.

### A. NSGA-II global: asignar varias incidencias

#### Representación

Un individuo es una lista de longitud igual al número de incidencias abiertas. Cada posición representa una incidencia y el valor de esa posición es el índice del técnico asignado:

```text
Incidencias: [I-01, I-02, I-03]
Individuo:   [  1,    0,    1 ]
Asignación:  I-01 → técnico 1; I-02 → técnico 0; I-03 → técnico 1
```

No es una permutación: un técnico puede aparecer en varios genes, y cada incidencia dispone de su propio conjunto de candidatos compatibles.

#### Población inicial y evaluación

Se crean `population_size` individuos aleatorios. Para cada gen se elige al azar un técnico entre las opciones compatibles de su incidencia. La evaluación devuelve dos objetivos que se **minimizan**:

1. **Espera ponderada por urgencia**

   Para cada incidencia se calcula el tiempo, en minutos, entre el instante actual y el siguiente inicio de jornada del técnico asignado. La suma se pondera por la urgencia de cada incidencia:

   ```text
   espera_ponderada = Σ (minutos_de_espera × peso_de_urgencia)
   ```

   En una misma ejecución, todas las incidencias asignadas a un técnico usan el mismo siguiente inicio estimado. No se modela una secuencia de reparaciones con tiempos de duración.

2. **Desequilibrio de carga**

   Se suma 1 al contador de carga del técnico por cada incidencia propuesta. El segundo objetivo es la suma de las desviaciones cuadráticas de las cargas proyectadas respecto a su media:

   ```text
   desequilibrio = Σ (carga_proyectada_del_técnico − carga_media)²
   ```

   Un valor menor corresponde a una distribución más equilibrada.

El resultado guarda en caché la evaluación de cada combinación de asignaciones para no repetir el cálculo cuando el mismo individuo aparece de nuevo.

#### Dominancia y clasificación no dominada

Una solución A domina a B si A no es peor en ninguno de los dos objetivos y es estrictamente mejor en al menos uno:

```text
A domina B si:
  espera(A) ≤ espera(B)
  y carga(A) ≤ carga(B)
  y al menos una de las dos desigualdades es estricta
```

El algoritmo compara los individuos por pares y construye frentes:

- **Frente 1:** soluciones no dominadas por ninguna otra.
- **Frente 2:** soluciones dominadas solo por miembros del frente 1.
- Los frentes siguientes se construyen sucesivamente.

Las soluciones del frente 1 representan compromisos entre rapidez y balance: una puede reducir la espera y otra distribuir mejor la carga sin que una sea mejor en ambos criterios.

#### Distancia de crowding

Cuando no cabe un frente completo en la población siguiente, se calcula la distancia de crowding por objetivo. Los individuos extremos de cada objetivo reciben distancia infinita para preservar los extremos del frente. Para los demás se acumulan las diferencias normalizadas entre sus vecinos ordenados por cada objetivo. Se prefieren distancias mayores para mantener diversidad.

#### Selección, cruce y mutación

- **Padres:** se seleccionan dos individuos al azar de la población. En este modo no se aplica torneo por rango.
- **Cruce:** con probabilidad 85 %, cada posición del hijo hereda el técnico del padre izquierdo o derecho con probabilidad 50/50. Sin cruce, se conserva una copia del primer padre.
- **Mutación:** cada gen tiene probabilidad 15 % de cambiarse a otro técnico compatible para esa incidencia. Si solo existe una opción, el gen no puede mutar a una alternativa distinta.

El cruce combina asignaciones por posición y la mutación solo selecciona candidatos válidos; por tanto, las capacidades se mantienen.

#### Reemplazo y criterio de parada

Se combinan padres y descendientes (hasta `2N` individuos), se vuelven a clasificar en frentes y se incorporan frentes completos desde el mejor rango. Si el último frente no cabe, se seleccionan sus miembros por mayor distancia de crowding. Así se conserva una población de tamaño `N` y se da preferencia a soluciones no dominadas, manteniendo diversidad.

La ejecución se detiene al completar el número configurado de generaciones. El historial registra para cada generación el tamaño del primer frente.

#### Selección de planes finales

Al finalizar, se recorren los frentes desde el primero. Dentro de cada frente, las soluciones se ordenan por menor espera ponderada y, en caso de empate, mayor distancia de crowding. Se eliminan planes duplicados y se muestran hasta tres. Es una selección para presentar alternativas, no una función que descarte el frente de Pareto y declare una solución universalmente óptima.

### B. NSGA-II de propuesta de equipo para horario tentativo

Este modo resuelve una pregunta diferente: para una incidencia y una hora ya elegidas, ¿qué equipo de 2 o 3 personas conviene proponer?

#### Cromosoma, factibilidad y objetivos

Un cromosoma es una combinación ordenada canónicamente de índices de técnicos distintos; no hay duplicados dentro del equipo. Un equipo es factible cuando, en conjunto, cubre todas las capacidades requeridas y sus miembros están disponibles para el horario.

Se calculan estos componentes:

- Capacidades cubiertas por el equipo: promedio de las puntuaciones de capacidad de cada requisito.
- Liderazgo: capacidad de dirigir incidencias del miembro elegido como líder.
- Experiencia: promedio normalizado respecto a 10 años.
- Carga: inverso de `1 + carga media proyectada` del equipo.
- Traslado: inverso de `1 + distancia media estimada`.

La puntuación es:

```text
fitness_equipo = 100 × (
    0,50 × capacidades
  + 0,20 × liderazgo
  + 0,15 × experiencia
  + 0,10 × carga
  + 0,05 × traslado
)
```

NSGA-II minimiza dos objetivos:

```text
(100 − fitness_equipo, carga_media_proyectada)
```

Así, el primer objetivo favorece más calidad de equipo y el segundo menos carga. Los miembros se presentan con el líder primero. La selección del líder prioriza aptitud para dirigir, experiencia y menor carga base; el requisito de liderazgo puede ser cero en equipos de instalación solo en la optimización genética general, pero para incidencias la puntuación de liderazgo forma parte de la calidad y no es un filtro de factibilidad aparte.

#### Inicialización y operadores

Para cada tamaño (2 y 3):

- Si el número de combinaciones posibles no supera 5.000, se enumeran las combinaciones factibles y se barajan para formar la población.
- Si supera 5.000, se muestrean equipos válidos al azar hasta completar la población o alcanzar el límite de intentos.
- Si hay menos equipos únicos válidos que el tamaño de población, se repiten equipos válidos para completar la población.

La selección de padres es un torneo binario que compara primero rango del frente y después distancia de crowding. Con la probabilidad de cruce, se toman integrantes de la unión de ambos padres hasta alcanzar el tamaño fijo del equipo. Con la probabilidad de mutación, se reemplaza un integrante por otro técnico que no pertenezca al equipo. Si el hijo no resulta factible, se intenta generar un equipo válido al azar y, si no se encuentra, se conserva el primer padre.

El reemplazo ambiental une padres e hijos y selecciona por frentes y crowding, como en el modo global. Se conserva un archivo de equipos evaluados y al final se toma el frente de Pareto del archivo para devolver hasta tres alternativas. La salida incluye fecha/hora tentativa, integrantes, líder, indicadores del equipo y número de técnicos elegibles.

## 5. Evaluación

Las pruebas automatizadas verifican, entre otros comportamientos:

- Que el modo global procese las generaciones configuradas y genere historial.
- Que técnicos inactivos o no cualificados queden excluidos.
- Que los equipos propuestos sean de dos o tres personas y satisfagan requisitos.
- Que un técnico con ausencia en el horario tentativo no sea incluido.
- Que la configuración se guarde de forma independiente y rechace valores fuera de rango.
- Que la vista de Sistemas coloque la optimización de incidencias bajo el módulo de Incidencias.

La evaluación operativa debe revisar, además, que los perfiles de capacidades, horarios, ausencias, urgencia y carga estén completos. Una alternativa Pareto puede ser válida y aun así no ser la preferida por el encargado: la elección depende de la política operativa del momento.

## 6. Despliegue y uso operativo

### Optimización global

1. Sistemas abre **Incidencias → Optimización**.
2. Ajusta parámetros de población, generaciones, mutación y cruce.
3. La aplicación obtiene incidencias abiertas, perfiles, capacidades y cargas.
4. NSGA-II genera hasta tres planes Pareto.
5. Sistemas revisa técnicos, fechas estimadas, espera y carga proyectada.
6. La asignación se realiza por el flujo normal; la optimización no modifica el asignado.

### Propuesta de equipo

1. Se parte de una incidencia y de un horario tentativo de la etapa.
2. El servicio filtra técnicos para ese horario y genera equipos factibles.
3. Se presentan hasta tres alternativas para revisión.
4. El usuario decide si confirma o modifica la propuesta mediante el flujo existente.

## Limitaciones y supuestos

- **No se escribe automáticamente la asignación** al ejecutar NSGA-II; las salidas son recomendaciones.
- La espera global usa el siguiente inicio de jornada y no una programación secuencial de tareas con duración.
- El balance de carga es un conteo de trabajos/incidencias y no una estimación de horas reales de reparación.
- La inferencia de capacidades por texto usa patrones; descripciones ambiguas pueden producir requisitos incompletos.
- El modelo de jornada no sustituye una agenda completa con duración, traslados, pausas y solapamientos futuros.
- La optimización de equipo sí considera el horario tentativo, ausencias y ocupaciones que el servicio conoce para ese instante, pero no predice toda la duración de la solución.
- Por ser metaheurístico y aleatorio, NSGA-II no garantiza el óptimo global. El resultado depende de los datos, la configuración y la aleatoriedad.
- Si una incidencia no tiene ningún candidato factible, el modo global informa el problema y no fabrica una asignación.
- La frontera de Pareto no expresa una preferencia única; la selección final debe considerar la urgencia y las reglas reales del área.

## Referencias de implementación

- `DATALAN/optimization_service.py`: `incident_required_capabilities`, `_incident_next_work_start`, `_incident_urgency_weight`, `_incident_nondominated_fronts`, `_incident_crowding_distance`, `run_incident_nsga2` y `run_incident_team_nsga2`.
- `DATALAN/views.py`: `flatten_service_incidents`, manejo POST de `systems_incident_optimization` y flujo de propuesta de equipos.
- `DATALAN/test_optimization_service.py`: pruebas de optimización global, equipos, restricciones de disponibilidad y configuración.
