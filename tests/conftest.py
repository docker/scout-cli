"""
Fixtures compartidos para las pruebas de validación de los archivos
docker_scout_*.yaml del repositorio docker/scout-cli.

Estas pruebas NO prueban el binario de la CLI (closed-source), sino los
artefactos de documentación/configuración versionados en docs/: los YAML
que describen cada comando (y que generan los .md) y su consistencia
estructural y referencial.
"""
import pathlib
import re

import pytest
import yaml

# Carpeta docs/ del repo. Por defecto apunta a la carpeta de ejemplo
# incluida en este proyecto. Para correr las pruebas contra el repo
# real, exporta la variable de entorno SCOUT_DOCS_DIR, por ejemplo:
#
#   export SCOUT_DOCS_DIR=/ruta/a/scout-cli/docs
#   pytest
#
import os

DEFAULT_DOCS_DIR = pathlib.Path(__file__).parent.parent / "docs"
DOCS_DIR = pathlib.Path(os.environ.get("SCOUT_DOCS_DIR", DEFAULT_DOCS_DIR))

YAML_FILENAME_RE = re.compile(r"^docker_scout(_[a-z0-9-]+)*\.yaml$")

# value_type conocidos usados por los comandos de docker scout
KNOWN_VALUE_TYPES = {
    "bool",
    "string",
    "stringSlice",
    "stringArray",
    "int",
    "int64",
    "float32",
    "float64",
    "duration",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "command",
    "short",
    "long",
    "deprecated",
    "experimental",
    "experimentalcli",
    "kubernetes",
    "swarm",
}

REQUIRED_OPTION_FIELDS = {
    "option",
    "value_type",
    "description",
    "deprecated",
    "hidden",
    "experimental",
    "experimentalcli",
    "kubernetes",
    "swarm",
}

BOOL_FIELDS = {"deprecated", "experimental", "experimentalcli", "kubernetes", "swarm"}


def discover_yaml_files():
    if not DOCS_DIR.exists():
        return []
    return sorted(DOCS_DIR.glob("docker_scout*.yaml"))


@pytest.fixture(scope="session")
def docs_dir():
    return DOCS_DIR


@pytest.fixture(scope="session")
def all_yaml_paths():
    paths = discover_yaml_files()
    if not paths:
        pytest.fail(
            f"No se encontraron archivos docker_scout*.yaml en {DOCS_DIR}. "
            "Define SCOUT_DOCS_DIR apuntando a la carpeta docs/ del repo clonado."
        )
    return paths


@pytest.fixture(scope="session")
def loaded_docs(all_yaml_paths):
    """dict: {path -> contenido parseado del yaml}"""
    docs = {}
    for path in all_yaml_paths:
        with open(path, "r", encoding="utf-8") as fh:
            docs[path] = yaml.safe_load(fh)
    return docs


def pytest_generate_tests(metafunc):
    """Parametriza automáticamente cualquier test que pida 'yaml_path'."""
    if "yaml_path" in metafunc.fixturenames:
        paths = discover_yaml_files()
        ids = [p.name for p in paths]
        metafunc.parametrize("yaml_path", paths, ids=ids)
