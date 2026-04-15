from importlib.metadata import version

import pytimeslice


def test_package_version_is_exposed() -> None:
    assert pytimeslice.__version__ == version("pytimeslice")
