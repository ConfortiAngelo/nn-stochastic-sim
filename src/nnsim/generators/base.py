"""Puerto RNG: interfaz común de todos los generadores (sección 6.1 del plan). Cap. 2.

La implementación concreta de cada generador vive en su propio adaptador (S1-01 en adelante).
"""

from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray


@runtime_checkable
class RNG(Protocol):
    """Generador de números pseudoaleatorios.

    Todo el azar del proyecto pasa por este puerto (ADR-001), así los experimentos pueden
    cambiar de generador sin tocar la red ni los entrenadores.
    """

    def seed(self, s: int) -> None:
        """Fija el estado inicial X_0 a partir de la semilla ``s``."""
        ...

    def next_int(self) -> int:
        """Avanza la recurrencia y devuelve el siguiente X_i."""
        ...

    def uniform(self, n: int) -> NDArray[np.float64]:
        """Devuelve ``n`` valores r_i en el intervalo abierto (0, 1)."""
        ...
