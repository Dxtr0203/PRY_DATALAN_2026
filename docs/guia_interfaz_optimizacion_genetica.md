# Guía de la interfaz de Optimización Genética

## Propósito

La pantalla **Optimización** pertenece al Encargado de Sistemas. Su función es mostrar las solicitudes que ya pasaron por Comercial, Planta Técnica y la verificación de Sistemas, para preparar una futura asignación optimizada.

Esta pantalla es una interfaz de demostración. Los ejemplos, valores y cromosomas mostrados no representan todavía una ejecución real del algoritmo.

## Configuración del algoritmo

### Población: 40

La población es la cantidad de soluciones candidatas que se generan en cada generación.

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

Con `100` generaciones, el sistema puede mejorar progresivamente las soluciones. El algoritmo no crea 100 solicitudes: intenta mejorar 100 veces el orden y la asignación de la población.

Más generaciones permiten mayor búsqueda, pero aumentan el tiempo de cálculo. Si el fitness deja de mejorar durante varias generaciones, se puede detener antes mediante una condición de convergencia.

### Mutación: 10%

La mutación introduce cambios pequeños para evitar que toda la población se vuelva igual.

En una permutación, un ejemplo de mutación por intercambio es:

```text
Antes:    [0142, 0150, 0154, 0160]
Después:  [0142, 0154, 0150, 0160]
```

Se intercambiaron las posiciones 2 y 3. Una tasa de `10%` significa que aproximadamente 1 de cada 10 oportunidades de mutación modifica un individuo.

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

La interfaz muestra estos pesos de ejemplo:

| Criterio | Peso | Qué representa |
|---|---:|---|
| Prioridad | 35% | Atiende antes solicitudes Alta que Media o Baja. |
| Retraso | 30% | Penaliza fechas que incumplen la programación esperada. |
| Distancia | 20% | Reduce traslados innecesarios entre trabajos. |
| Carga del técnico | 15% | Evita concentrar demasiados trabajos en una persona. |

Los pesos suman 100%. No son valores universales: Sistemas puede modificarlos según las reglas reales de DATALAN.

## Fitness

El fitness es una medida de qué tan buena es una solución. En este caso se recomienda minimizar un costo:

$$
F = 0.35C_{prioridad} + 0.30C_{retraso} + 0.20C_{distancia} + 0.15C_{carga}
$$

Una solución será mejor cuando tenga menor costo, siempre que cumpla las restricciones duras.

Restricciones duras sugeridas:

- No repetir una solicitud dentro del cromosoma.
- No asignar trabajos a un técnico no disponible.
- No programar dos trabajos simultáneos para el mismo técnico.
- No incluir solicitudes no factibles o no aprobadas por Sistemas.
- No programar una fecha anterior a la fecha actual.
- No superar la disponibilidad de equipos.

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

La interfaz puede representar una solución con columnas de posición, CITE, técnico, fecha, distancia y costo local. El algoritmo real calculará el fitness; la pantalla actual solo prepara y explica esa información.

## Qué significa cada área

- **Comercial:** aporta cliente, tipo, prioridad y requisitos.
- **Planta Técnica:** aporta factibilidad, distancia, dificultad, cobertura, infraestructura y materiales.
- **Sistemas:** aporta disponibilidad, compatibilidad, equipos, técnicos y parámetros del algoritmo.
- **Técnico y Soporte:** reciben la asignación final y reportan el trabajo.
- **Administrador:** puede consultar resultados y trazabilidad, pero no debería modificar una solución operativa sin autorización.

## Lectura de la pantalla

1. **Configuración del algoritmo:** valores de la futura ejecución.
2. **Solicitudes evaluadas:** entrada que el algoritmo puede considerar.
3. **Estado de la solución:** fitness y generación actual.
4. **Codificación permutacional:** orden de atención de las solicitudes.
5. **Relación operativa:** origen y destino de los datos entre áreas.

El botón de ejecución debe permanecer deshabilitado hasta que el motor real valide restricciones, guarde la ejecución y permita confirmar la solución antes de crear asignaciones definitivas.
