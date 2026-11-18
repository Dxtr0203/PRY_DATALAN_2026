# Iteración 4: algoritmo genético con codificación permutacional

## Propósito y alcance

Este documento describe el algoritmo genético que recomienda un orden de atención y una asignación de técnicos para las solicitudes aprobadas. Es la optimización disponible en **Sistemas → Optimización**. El algoritmo no decide la aprobación comercial, no confirma una asignación y no modifica por sí solo el estado de una solicitud: entrega alternativas para que el encargado las revise y continúe con el flujo operativo.

La estructura se organiza siguiendo las fases de **CRISP-DM**. Si el formato académico del proyecto denomina su marco «CRISP-DN», se puede conservar esa denominación en la portada, pero las fases descritas aquí corresponden a la secuencia habitual de CRISP-DM.

La implementación principal se encuentra en `DATALAN/optimization_service.py`: `prepare_request`, `_prepare_operational_team_candidates`, `_decode`, `_order_crossover` y `run_genetic_optimization`. La vista que la ejecuta está en `DATALAN/views.py`.

## 1. Comprensión del negocio

### Problema

Una vez que Comercial aprueba solicitudes, Sistemas necesita ordenar su atención y proponer personal que pueda realizar los trabajos. Si se atienden primero solicitudes de menor urgencia, se incrementan las esperas ponderadas de las solicitudes prioritarias. Si se concentra el trabajo en pocas personas, se produce una distribución desequilibrada.

El problema se formula como una búsqueda de un orden de solicitudes que permita obtener una recomendación de asignación de buena calidad, considerando prioridad, tiempo estimado, traslado, carga de trabajo y, cuando se dispone de perfiles operativos, la calidad del equipo compatible.

### Objetivo de la iteración

Generar hasta tres órdenes candidatos, compararlos mediante una función de aptitud común y mostrar el mejor puntaje junto con las asignaciones decodificadas. El encargado conserva la decisión final.

### Criterios de éxito funcional

- Cada cromosoma contiene todas las solicitudes elegibles exactamente una vez.
- El cruce y la mutación conservan una permutación válida.
- No se recomienda un técnico que esté marcado como no disponible o que no cumpla las capacidades exigidas.
- Una solicitud sin una alternativa compatible aparece como **SIN TÉCNICO COMPATIBLE** y reduce la cobertura.
- Las alternativas se ordenan de mayor a menor fitness y no se repite el mismo cromosoma en la lista final.
- Ejecutar la optimización produce una recomendación, no una asignación automática.

## 2. Comprensión de los datos

### Solicitudes de entrada

La vista entrega solicitudes que satisfacen simultáneamente estas condiciones:

1. Su estado es `APROBADA`.
2. Su decisión comercial final es `APROBADO`.
3. No tienen una asignación existente.

Por tanto, una decisión previa negativa de otra área no reemplaza la aprobación final de Comercial para el filtro de entrada. Cada solicitud aporta, entre otros datos:

- CITE y tipo de instalación.
- Prioridad (`Alta`, `Media` o `Baja`).
- Requisitos, detalles multipunto, equipamiento y velocidad.
- Evaluación de Planta Técnica, distancia y ubicación.
- Horas estimadas, si están registradas.

### Técnicos y perfiles

En la ruta actual, el algoritmo utiliza técnicos disponibles con estado operativo activo. Sus perfiles guardan capacidades, experiencia, liderazgo, ubicación, distancia estimada y carga. Si los técnicos incluyen perfiles operativos, el decodificador emplea equipos compatibles; el código conserva también una ruta de compatibilidad heredada para datos de técnicos sin perfil operativo.

### Interpretación automática de requisitos

`prepare_request` busca expresiones en campos textuales de la solicitud para inferir capacidades:

| Expresión o dato detectado | Capacidad requerida |
|---|---|
| Aéreo, poste o altura | Trabajo aéreo |
| Subterráneo, ducto o canalización | Trabajo subterráneo |
| Fusionadora o fusión | Fusionadora |
| OTDR | OTDR |
| Instalación/montaje de equipos, o `equipment_enabled` | Instalación de equipos |

En el perfil operativo, los requisitos se traducen a capacidades concretas: aéreo y subterráneo requieren tender cable; fusionadora requiere realizar fusiones; OTDR requiere utilizarlo e interpretar mediciones; equipo requiere instalar y conectar equipos. En un equipo, la capacidad puede estar cubierta por uno de sus miembros; no se exige que cada integrante tenga todas las capacidades.

La inferencia textual es heurística. Si la descripción no usa expresiones reconocibles, el sistema podría no detectar un requisito; por ello conviene revisar los datos y las capacidades registradas.

### Estimación de duración y distancia

- Se usa `estimated_hours` de la solicitud o de la evaluación de Planta Técnica cuando es un número positivo válido.
- Si falta o no es válida, se estima una base de 4 horas para multipunto o 2,5 horas para otros tipos, más 0,75 horas por cada capacidad requerida.
- La distancia procede de la evaluación de Planta Técnica. Si falta, es inválida o negativa, se normaliza a cero.
- La ubicación se toma, en orden, de destino, instalación u origen, usando «Ubicación no detallada» como último recurso.

Estas duraciones y distancias son datos de evaluación, no una ruta geográfica calculada por el algoritmo.

## 3. Preparación de los datos

Antes de evolucionar la población, el sistema:

1. Filtra las solicitudes aprobadas y pendientes de asignación.
2. Convierte cada solicitud al formato de optimización y normaliza requisitos, duración, distancia y ubicación.
3. Prepara la lista de técnicos activos y disponibles.
4. Calcula la carga inicial a partir de trabajos activos existentes.
5. En el modo de perfiles operativos, precalcula las combinaciones de técnicos que pueden cubrir los requisitos y el tamaño de equipo requerido.
6. Valida los parámetros. La población permitida es de 2 a 200; las generaciones, de 1 a 500; cruce y mutación, de 0 % a 100 %.

El tamaño de equipo para instalación se calcula según prioridad y distancia:

- 5 integrantes si la prioridad es alta y la distancia supera 25 km.
- 4 integrantes si la prioridad es alta o la distancia supera 10 km.
- 3 integrantes en los demás casos.

El valor de distancia y los umbrales son reglas del código, no parámetros editables desde la configuración genética.

## 4. Modelado

### Representación del cromosoma

El cromosoma es una permutación de índices de solicitudes. Cada índice identifica un CITE en la lista de entrada. Por ejemplo, para las solicitudes `[CITE-01, CITE-02, CITE-03]`:

```text
Individuo A: [0, 1, 2]  → CITE-01, CITE-02, CITE-03
Individuo B: [2, 0, 1]  → CITE-03, CITE-01, CITE-02
```

Cada gen aparece una sola vez. El gen representa una solicitud y su posición representa su turno dentro del orden de atención. **El técnico no está codificado como gen**: se determina después, al decodificar el orden.

### Inicialización

La población inicial incluye:

- Un individuo de referencia ordenado por prioridad descendente y, a igual prioridad, por menor duración estimada.
- Los individuos restantes, generados al barajar aleatoriamente todos los índices de solicitudes.

La población predeterminada es de 40 individuos. El algoritmo puede recibir una semilla aleatoria para repetir una ejecución en pruebas; en el uso normal no se proporciona una semilla fija.

### Decodificación y asignación

Para cada cromosoma se recorren sus solicitudes en orden. En ese recorrido se actualizan las cargas para que las decisiones posteriores consideren los trabajos ya recomendados en el mismo cromosoma.

**Con perfiles operativos**, para cada solicitud se evalúan los equipos precalculados que cumplen las capacidades y el tamaño requerido. Se elige el equipo con mayor puntuación considerando:

- Cobertura de capacidades: 50 %.
- Liderazgo: 20 %.
- Experiencia: 15 %.
- Menor carga media: 10 %.
- Menor distancia media de traslado: 5 %.

La experiencia se normaliza respecto a 10 años y se limita a 100 %. Las puntuaciones de carga y distancia usan la forma `1 / (1 + valor)`. El líder se determina por la capacidad de liderazgo y experiencia; el equipo se presenta con el líder primero.

**En la ruta heredada sin perfiles operativos**, se filtra por disponibilidad y habilidades booleanas. Entre técnicos compatibles se minimiza una combinación de carga y distancia, usando la coincidencia de ubicación como desempate.

Si no existe equipo o técnico compatible, la solicitud se conserva en el orden, se marca **SIN TÉCNICO COMPATIBLE** y no incrementa ninguna carga de técnico.

### Función de evaluación

El decodificador calcula subpuntajes entre 0 y 100:

1. **Prioridad.** Penaliza el costo de la posición de cada solicitud: `peso_prioridad × posición`, con pesos 3 para Alta, 2 para Media y 1 para Baja. Se normaliza entre el orden de referencia más favorable y el más desfavorable.
2. **Tiempo.** Suma el tiempo acumulado de finalización ponderado por prioridad. Se normaliza frente a un orden favorable por prioridad y duración y a su orden inverso.
3. **Distancia.** Compara la distancia promedio de los equipos asignados con la distancia máxima entre los técnicos disponibles.
4. **Carga.** Mide la varianza de las cargas finales de los técnicos disponibles; una menor varianza produce un puntaje mayor.
5. **Equipo.** En el modo operativo, es el promedio de las puntuaciones de equipo elegidas para las solicitudes asignadas.
6. **Cobertura.** Proporción de solicitudes que recibieron una recomendación compatible.

Con perfiles operativos, el fitness usado para ordenar soluciones es:

```text
fitness = cobertura × (
    0,25 × prioridad
  + 0,20 × tiempo
  + 0,15 × distancia
  + 0,15 × carga
  + 0,25 × equipo
)
```

Sin perfiles operativos, se usa:

```text
fitness = cobertura × (
    0,35 × prioridad
  + 0,30 × tiempo
  + 0,20 × distancia
  + 0,15 × carga
)
```

La cobertura se expresa como fracción al aplicar la fórmula (por ejemplo, 80 % se multiplica por 0,8). Por ello, una cobertura incompleta reduce el fitness total aun cuando los demás subpuntajes sean altos. El algoritmo **maximiza** el fitness.

### Selección de progenitores

Se usa selección por torneo de tamaño 3: se eligen hasta tres individuos evaluados al azar y se selecciona el de mayor fitness. Se repite el torneo para elegir el segundo progenitor.

### Cruce: Order Crossover (OX)

Con la probabilidad configurada (80 % por defecto), se eligen dos posiciones y se copia al hijo el segmento del primer progenitor. Las posiciones restantes se completan recorriendo el segundo progenitor de forma circular, omitiendo genes que ya están en el segmento. De esta manera se conserva la propiedad de permutación y el orden relativo heredado.

Si no ocurre el cruce, el hijo es una copia del primer progenitor.

### Mutación por intercambio

Con la probabilidad configurada (10 % por defecto) para cada hijo, se seleccionan dos posiciones y se intercambian sus genes. Esta operación cambia el orden sin añadir ni eliminar solicitudes.

### Reemplazo, elitismo y archivo de alternativas

El mejor individuo de cada generación se copia directamente a la siguiente población (elitismo de un individuo). Los demás lugares se completan con hijos de los torneos.

El algoritmo evalúa las generaciones desde la generación 0 hasta la generación indicada. En cada ronda conserva en un archivo los mejores cromosomas encontrados y recorta el archivo a las tres mejores soluciones distintas por secuencia de genes. Las soluciones finales se ordenan por fitness descendente.

### Parámetros predeterminados

| Parámetro | Predeterminado | Rango permitido |
|---|---:|---:|
| Población | 40 | 2–200 |
| Generaciones | 100 | 1–500 |
| Mutación | 10 % | 0–100 % |
| Cruce | 80 % | 0–100 % |

La configuración de esta optimización se guarda con la clave `genetic`, separada de la configuración NSGA-II de incidencias.

## 5. Evaluación

La evaluación se realiza a nivel de pruebas automatizadas y de revisión de las recomendaciones:

- Se verifica que el cruce OX conserve todos los genes una sola vez.
- Se verifica que cada CITE aparezca una vez en el orden recomendado.
- Se comprueba que un técnico no disponible o sin capacidad requerida no sea recomendado.
- Se comprueba el estado explícito y la cobertura cero cuando no hay técnico compatible.
- Se verifica que las tres alternativas sean cromosomas distintos y estén ordenadas por fitness.
- Se comprueba la selección de equipos en el modo operativo.

En operación, la evaluación debe observar el orden, las asignaciones, los subpuntajes, la cobertura y las cargas resultantes. Un fitness mayor compara soluciones dentro de la misma ejecución y con los mismos datos y parámetros; no garantiza por sí solo que la solución sea óptima en sentido matemático.

## 6. Despliegue y uso operativo

1. Sistemas abre **Optimización** y confirma población, generaciones, mutación y cruce.
2. La aplicación toma las solicitudes que cumplen los filtros de aprobación y no asignación.
3. El algoritmo evoluciona órdenes y devuelve una recomendación principal, el historial del mejor fitness y hasta tres alternativas.
4. Sistemas revisa resultados y compatibilidad.
5. La asignación final se realiza mediante el flujo normal de la aplicación. Ejecutar el algoritmo no cambia solicitudes ni crea asignaciones.

## Limitaciones y supuestos

- La optimización es estocástica: distintas ejecuciones pueden producir resultados diferentes.
- Es una búsqueda aproximada; alcanzar el límite de generaciones no demuestra que se haya encontrado el óptimo global.
- Los requisitos se infieren con patrones de texto y dependen de los datos disponibles.
- Las duraciones y distancias de respaldo son estimaciones, no mediciones de campo ni cálculos de rutas.
- El algoritmo trabaja con cargas y perfiles registrados; la calidad de la recomendación depende de su actualización.
- Los tres mejores cromosomas pueden representar recomendaciones de asignación similares aunque el orden sea distinto.
- La decisión y confirmación final permanecen bajo control del encargado.

## Referencias de implementación

- `DATALAN/optimization_service.py`: `prepare_request`, `_prepare_operational_team_candidates`, `_decode`, `_order_crossover`, `run_genetic_optimization`.
- `DATALAN/views.py`: `optimization_candidates` y manejo POST de `systems_optimization`.
- `DATALAN/test_optimization_service.py`: pruebas de requisitos, restricciones, cruce y alternativas.
