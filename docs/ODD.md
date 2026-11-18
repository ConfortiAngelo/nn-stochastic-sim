# Descripción del modelo (protocolo ODD) — v0

> Protocolo ODD (*Overview, Design concepts, Details*; Grimm et al., 2006 y 2020), usado para
> documentar modelos de simulación. Complementa los 10 pasos del Cap. 1, no los reemplaza.
> **Versión 0 (Sprint 0):** esqueleto con la definición del sistema. Se completa al cerrar cada
> sprint.

| Versión | Sprint | Cambios |
|---|---|---|
| v0 | 0 | Esqueleto y tabla del sistema (sección 4 del plan). |

## 1. Overview

### 1.1 Propósito

Estudiar el entrenamiento de una red neuronal (MLP programado desde cero) como un
**experimento estocástico**. Se mide cómo las fuentes de azar (generador, inicialización,
orden de los datos, perturbaciones del recocido) afectan la pérdida, la precisión y la
trayectoria de los pesos, y se resume con media, IC 95 % y R réplicas.

### 1.2 Entidades, variables de estado y escalas

Definición del sistema según el Cap. 1 (sección 4 del plan):

| Elemento (Cap. 1) | En el proyecto |
|---|---|
| Sistema | El proceso de entrenamiento de la red neuronal sobre un conjunto de datos. |
| Entidades | Ejemplos de entrenamiento, agrupados en minibatches, que entran al sistema y cambian su estado. |
| Atributos | Características (x1, x2, …) y etiqueta de cada ejemplo. |
| Estado del sistema | Vector de pesos y sesgos θ en un instante. |
| Eventos | Cada actualización de θ: un paso de gradiente o una propuesta aceptada en el recocido. |
| Reloj de simulación | Contador de pasos y de épocas (reloj absoluto). |
| Variables de respuesta | Pérdida, precisión en test, norma de θ, MSD, tasa de aceptación. |
| Componentes aleatorios | Generador, distribución de inicialización, orden de los datos, perturbaciones del recocido. |
| Clasificación | Estocástico, dinámico, discreto, artificial. Terminante por número de épocas, con transitorio y régimen. |

**Escalas.** PENDIENTE (Sprint 1): tamaño de red (H = 8 o 16), tamaño del dataset (400 a 1000
puntos), épocas y tamaño de minibatch por experimento.

### 1.3 Secuencia del proceso (una réplica)

1. Fijar semilla y generador.
2. Generar el conjunto de datos con ese generador y dividir en entrenamiento y test (80/20).
3. Inicializar los pesos con la distribución elegida (transformada inversa o Box-Muller sobre
   el generador).
4. Entrenar: en cada época, mezclar los datos (Fisher-Yates), recorrer minibatches y actualizar θ.
5. Registrar por paso o por época: pérdida, precisión, θ (o una muestra) para el MSD.
6. Al terminar, guardar las métricas finales medidas en el régimen estable (promedio de las
   últimas k épocas).
7. Repetir con R semillas distintas y resumir con media e intervalo de confianza.

## 2. Design concepts

### 2.1 Estocasticidad

Todo el azar pasa por el puerto `RNG` (ADR-001). PENDIENTE (Sprint 1): generadores
implementados y su validación (E1).

### 2.2 Observación

PENDIENTE (Sprint 2): qué se registra, con qué frecuencia y en qué CSV de `results/`.

### 2.3 Emergencia

PENDIENTE (Sprint 3): comportamientos que emergen del entrenamiento (difusión de θ, MSD,
transición con η).

## 3. Details

### 3.1 Inicialización

PENDIENTE (Sprint 1): distribuciones de inicialización (ceros, uniforme, normal, Xavier, He).

### 3.2 Datos de entrada

PENDIENTE (Sprint 1): datasets sintéticos (blobs, XOR, espirales), split y normalización.
Solo se usan datos sintéticos.

### 3.3 Submodelos

PENDIENTE (Sprints 1 a 3): red neuronal, GD, SGD, recocido simulado y métricas.
