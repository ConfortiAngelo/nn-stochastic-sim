"""Test de humo: el paquete se importa desde src/ sin instalarlo."""

import nnsim


def test_s0_04_package_imports_with_version() -> None:
    """Dado src/ en el pythonpath, cuando importo nnsim, entonces expone __version__ == 0.0.1."""
    assert nnsim.__version__ == "0.0.1"
