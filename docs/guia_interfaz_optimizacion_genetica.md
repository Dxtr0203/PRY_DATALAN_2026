# Guía de la interfaz de Optimización Genética

## Propósito

La pantalla **Optimización** pertenece al Encargado de Sistemas. Usa solicitudes con decisión final **APROBADO** de Comercial que todavía no han sido asignadas. La aprobación final de Comercial prevalece aunque Planta Técnica o Sistemas hubiera rechazado la solicitud. Cada ejecución busca soluciones nuevas con el algoritmo genético; no entrena un modelo predictivo ni conserva aprendizaje entre ejecuciones. Cada cromosoma representa un orden diferente de las solicitudes aprobadas.

En la instancia de demostración se cargaron 20 solicitudes sintéticas aprobadas, identificadas por el prefijo `CITE-DEMO-GA-2026-` y por el nombre del cliente `DEMO`. Son datos de prueba, no solicitudes reales.

## Configuración del algoritmo

### Población: 40

La población es la cantidad de soluciones candidatas que se generan en cada generación. El valor inicial es 40 y se puede editar entre 2 y 200.

En una codificación permutacional, cada individuo puede ser un orden diferente de las solicitudes:

```text
Individuo A: [CITE-0142, CITE-0150, CITE-0154, CITE-0160]
Individuo B: [CITE-0154, CITE-0142, CITE-0160, CITE-0150]
Individuo C: [CITE-0160, CITE-0150, CITE-0142, CITE-0154]
```

El valor `40` significa que el algoritmo compara 40 órdenes posibles por generación. Una población pequeña es rápida, pero explora menos alternativas. Una población grande puede encontrar mejores soluciones, aunque tarda más.

Como punto de partida:

- 10 a 20: pruebas rápidas o pocas solicitudes.
- 40 a 80: operación mediana.
- 100 o más: muchos trabajos y restricciones complejas.

### Generaciones: 100

Una generación es una ronda de evolución. En cada ronda se evalúa la población, se conservan las mejores soluciones y se crean nuevas mediante cruce y mutación.

Con `100` generaciones, el sistema intenta mejorar 100 veces el orden y la asignación de la población. El valor se puede editar entre 1 y 500.

Más generaciones permiten mayor búsqueda, pero aumentan el tiempo de cálculo. Si el fitness deja de mejorar durante varias generaciones, se puede detener antes mediante una condición de convergencia.

### Mutación: 10%

La mutación introduce cambios pequeños para evitar que toda la población se vuelva igual.

En una permutación, un ejemplo de mutación por intercambio es:

```text
Antes:    [0142, 0150, 0154, 0160]
Después:  [0142, 0154, 0150, 0160]
```

Se intercambiaron las posiciones 2 y 3. Una tasa de `10%` significa que cada descendiente tiene 10% de probabilidad de mutar.

- Muy baja: puede quedarse atrapado en una solución mediocre.
- Muy alta: destruye buenas soluciones y vuelve inestable la búsqueda.
- 5% a 15%: rango inicial razonable para una permutación.

Operadores adecuados: intercambio, inserción e inversión. No se debe usar una mutación que repita solicitudes o elimine genes.

### Cruce: 80%

El cruce combina dos soluciones para producir descendientes. El `80%` indica que la mayoría de las parejas seleccionadas intentará reproducirse.

Para permutaciones se recomienda **Order Crossover (OX)** o **Partially Mapped Crossover (PMX)**, porque conservan todos los genes una sola vez.

Ejemplo conceptual:

```text
Padre A: [0142, 0150, 0154, 0160]
Padre B: [0154, 0160, 0142, 0150]
Hijo:    [0154, 0150, 0142, 0160]
```

El hijo mantiene las cuatro solicitudes sin duplicarlas.

## Pesos de evaluación

La función de aptitud usa estos pesos:

Comercial selecciona **Instalación Eventual** como tipo de solicitud para registrar el período **DE/HASTA**; para los demás tipos se usa una sola fecha de instalación con calendario. La prioridad se calcula automáticamente desde hoy hasta la fecha normal o la fecha **DE** del período eventual: 0–3 días es **Alta**, 4–7 días es **Media** y 8 días o más es **Baja**. El servidor vuelve a calcularla al guardar. Los datos existentes que no tengan fecha conservan su prioridad registrada hasta ser editados.

| Criterio | Peso | Qué representa |
|---|---:|---|
| Prioridad | 35% | Atiende antes solicitudes Alta que Media o Baja. |
| Tiempo de atención | 30% | Reduce el tiempo acumulado de atención, ponderado por prioridad. |
| Distancia estimada | 20% | Prefiere técnicos con menor distancia estimada de traslado. |
| Carga del técnico | 15% | Evita concentrar demasiados trabajos en una persona. |

Los pesos suman 100%. No son valores universales: Sistemas puede modificarlos según las reglas reales de DATALAN.

## Fitness

El fitness es una medida de qué tan buena es una solución. En este caso se recomienda minimizar un costo:

$$
Fitness = (0.35S_{prioridad} + 0.30S_{tiempo} + 0.20S_{distancia} + 0.15S_{carga}) \times cobertura
$$

Cada subpuntaje se normaliza entre 0 y 100; un fitness mayor es mejor. La cobertura reduce el fitness si alguna solicitud no encuentra una persona disponible y compatible. El orden de prioridad favorece solicitudes Alta antes de Media y Baja. El balance toma en cuenta la carga existente y los trabajos que se van recomendando.

Restricciones duras sugeridas:

- No repetir una solicitud dentro del cromosoma.
- No recomendar a una persona no disponible ni sin todas las capacidades requeridas.
- No incluir solicitudes sin aprobación final de Comercial ni solicitudes ya asignadas. Una evaluación negativa de Planta Técnica o Sistemas no invalida la decisión final de Comercial.
- Las solicitudes sin candidatos compatibles se marcan explícitamente como **SIN TÉCNICO COMPATIBLE**; no se fuerza una asignación.

## Personal de Planta Técnica

La vista **Planta Técnica → Técnicos** contiene al Encargado de Planta Técnica Rolando Aduviri y al personal técnico solicitado. La primera vez que se inicializa el padrón, sus capacidades, disponibilidad, carga, zona actual y distancia estimada se generan aleatoriamente y se guardan en PostgreSQL. Las visitas siguientes respetan los cambios guardados.

Al abrir la tarjeta se pueden editar capacidades de cableado aéreo/subterráneo, fusionadora, OTDR e instalación de equipos, además de disponibilidad, carga de trabajo, ubicación actual y distancia de traslado estimada. El encargado forma parte del mismo conjunto de candidatos que los técnicos, y puede excluirse del algoritmo marcándolo no disponible. Si la zona escrita para el técnico coincide con la ubicación del trabajo, sirve como desempate entre candidatos con igual costo de carga y traslado.

La solicitud actual almacena ubicación, prioridad, tipo, observaciones, equipamiento solicitado y distancia de Planta Técnica. Los requisitos de habilidades se infieren de las observaciones y del tipo de solicitud; el checkbox **Con equipo** exige la capacidad de instalación de equipos, pero seleccionar un tipo de equipo como WDM por sí solo no. El tiempo se estima por modalidad y cantidad de requisitos cuando no hay un tiempo explícito. El traslado por persona también es una estimación editable, no una ruta calculada por coordenadas.

## Ejemplo con varias solicitudes

Supongamos que Sistemas recibe seis solicitudes elegibles:

| CITE | Cliente | Prioridad | Distancia | Dificultad | Equipo | Técnico posible |
|---|---|---|---:|---|---|---|
| CITE-0142 | Redes del Sur | Alta | 2.5 km | Media | Disponible | Carlos Torres |
| CITE-0150 | Andina Logística | Alta | 8.0 km | Alta | Disponible | Luis Pérez |
| CITE-0154 | Clínica Norte | Media | 3.2 km | Baja | Disponible | Carlos Torres |
| CITE-0160 | Cooperativa Centro | Baja | 12.0 km | Media | Parcial | Sofía Rojas |
| CITE-0167 | Universidad Sur | Media | 5.4 km | Alta | Disponible | Luis Pérez |
| CITE-0171 | Planta Industrial | Alta | 6.1 km | Media | Disponible | Sofía Rojas |

Una población inicial podría contener estos cromosomas:

```text
P1 = [0142, 0150, 0154, 0160, 0167, 0171]
P2 = [0150, 0171, 0142, 0167, 0154, 0160]
P3 = [0160, 0154, 0171, 0142, 0150, 0167]
P4 = [0171, 0142, 0167, 0150, 0160, 0154]
```

La pantalla muestra el fitness por generación y las tres mejores permutaciones distintas encontradas, con su orden, técnicos compatibles, traslado estimado, tiempo acumulado y puntajes por criterio. Las alternativas son cromosomas diferentes; el técnico se calcula al decodificar cada orden. **Sistemas debe revisar y crear las asignaciones usando el flujo existente**; ejecutar el algoritmo por sí solo no cambia el estado de las solicitudes.

## Qué significa cada área

- **Comercial:** aporta cliente, tipo, prioridad y requisitos.
- **Planta Técnica:** aporta factibilidad, distancia, dificultad, cobertura, infraestructura y materiales.
- **Sistemas:** aporta disponibilidad, compatibilidad, equipos, técnicos y parámetros del algoritmo.
- **Técnico y Soporte:** reciben la asignación final y reportan el trabajo.
- **Administrador:** puede consultar resultados y trazabilidad, pero no debería modificar una solución operativa sin autorización.

## Lectura de la pantalla

1. **Configuración del algoritmo:** población, generaciones, mutación y cruce para la ejecución actual.
2. **Solicitudes elegibles:** trabajos cuya decisión final de Comercial sea APROBADO y aún no tengan asignación. Esa aprobación final prevalece aunque Planta Técnica o Sistemas haya rechazado la solicitud.
3. **Estado de la solución:** fitness, cobertura y evolución generacional.
4. **Tres mejores alternativas:** pestañas con los tres cromosomas distintos de mayor fitness encontrados durante la ejecución.
5. **Codificación permutacional:** cada CITE aparece exactamente una vez en cada orden recomendado.
6. **Asignación sugerida:** selección de personal disponible y compatible al decodificar cada cromosoma, considerando su carga y distancia estimada.

## Optimización de incidencias con NSGA-II

La pantalla **Sistemas → Incidencias → Optimización** usa una configuración independiente de la optimización de solicitudes. Población, generaciones, mutación y cruce controlan la búsqueda; cambiar esos parámetros no modifica la valoración de técnicos ni asigna trabajos.

El algoritmo considera incidencias que no estén **CERRADAS** ni **PENDIENTE DE VALIDACIÓN**. Una persona solo puede ser candidata si es técnico, está activa y disponible, tiene una jornada configurada y satisface las capacidades inferidas de la descripción. Las capacidades de OTDR y fusión se leen del perfil operativo compartido. Las ausencias bloquean las horas que se superponen con ellas.

NSGA-II minimiza dos objetivos a la vez:

1. **Espera ponderada por urgencia:** estima el tiempo hasta el siguiente inicio de jornada disponible. Si el reporte no incluye severidad, la antigüedad incrementa su peso de urgencia.
2. **Desequilibrio de carga:** compara los trabajos activos registrados y suma las incidencias propuestas para evitar concentrar asignaciones.

El frente de Pareto muestra hasta tres planes distintos. Cada uno presenta el técnico sugerido, inicio estimado y carga proyectada para que el encargado compare rapidez y distribución. Son recomendaciones: seleccionar una alternativa no actualiza el asignado ni reemplaza el flujo de asignación de Planta Técnica.

La estimación no es un calendario de duración: el modelo de incidencias todavía no incluye duración de reparación ni intervalos completos de ocupación. Por eso el inicio informado representa el próximo comienzo de jornada compatible, no una reserva del horario.
