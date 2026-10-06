"""
Pruebas unitarias de los archivos docker_scout_*.yaml (docs/) del
repositorio docker/scout-cli.

Qué se valida:
  1. Sintaxis:      cada YAML parsea correctamente y produce un dict.
  2. Esquema base:   campos obligatorios presentes y con el tipo correcto.
  3. Comandos "hoja": usage/options bien formados.
  4. Comandos "padre": cname/clink consistentes entre sí.
  5. Referencias cruzadas: plink/pname apuntan a un archivo/comando real
     y esa relación es recíproca (el padre lista al hijo y viceversa).
  6. Documentación:  existe un .md correspondiente a cada .yaml.
"""
import yaml

from conftest import (
    BOOL_FIELDS,
    KNOWN_VALUE_TYPES,
    REQUIRED_OPTION_FIELDS,
    REQUIRED_TOP_LEVEL_FIELDS,
    YAML_FILENAME_RE,
)


# ---------------------------------------------------------------------------
# 1. Sintaxis
# ---------------------------------------------------------------------------

def test_filename_matches_naming_convention(yaml_path):
    assert YAML_FILENAME_RE.match(yaml_path.name), (
        f"'{yaml_path.name}' no sigue la convención docker_scout(_subcomando)*.yaml"
    )


def test_yaml_parses_and_is_a_mapping(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as fh:
        content = yaml.safe_load(fh)
    assert isinstance(content, dict), f"{yaml_path.name} no produce un mapeo YAML válido"


# ---------------------------------------------------------------------------
# 2. Esquema base (todos los archivos)
# ---------------------------------------------------------------------------

def test_required_top_level_fields_present(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    missing = REQUIRED_TOP_LEVEL_FIELDS - doc.keys()
    assert not missing, f"{yaml_path.name}: faltan campos obligatorios {missing}"


def test_boolean_fields_have_bool_type(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    for field in BOOL_FIELDS:
        if field in doc:
            assert isinstance(doc[field], bool), (
                f"{yaml_path.name}: el campo '{field}' debería ser booleano, "
                f"se encontró {type(doc[field]).__name__}"
            )


def test_command_field_starts_with_docker_scout(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    assert doc["command"].startswith("docker scout"), (
        f"{yaml_path.name}: 'command' debería empezar con 'docker scout', "
        f"tiene '{doc['command']}'"
    )


def test_short_and_long_are_non_empty_strings(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    for field in ("short", "long"):
        value = doc.get(field, "")
        assert isinstance(value, str) and value.strip(), (
            f"{yaml_path.name}: '{field}' debe ser texto no vacío"
        )


def test_command_name_matches_filename(yaml_path, loaded_docs):
    """docker scout integration list  ->  docker_scout_integration_list.yaml"""
    doc = loaded_docs[yaml_path]
    expected_filename = doc["command"].replace(" ", "_") + ".yaml"
    assert yaml_path.name == expected_filename, (
        f"El nombre de archivo '{yaml_path.name}' no coincide con el comando "
        f"'{doc['command']}' (se esperaba '{expected_filename}')"
    )


# ---------------------------------------------------------------------------
# 3. Comandos "hoja" (los que tienen 'usage' / 'options' propias)
# ---------------------------------------------------------------------------

def _validate_option_entry(entry, context):
    missing = REQUIRED_OPTION_FIELDS - entry.keys()
    assert not missing, f"{context}: opción incompleta, faltan {missing}: {entry}"
    assert entry["value_type"] in KNOWN_VALUE_TYPES, (
        f"{context}: value_type desconocido '{entry['value_type']}' en opción "
        f"'{entry['option']}'"
    )
    if "shorthand" in entry and entry["shorthand"] is not None:
        assert len(entry["shorthand"]) == 1, (
            f"{context}: el shorthand de '{entry['option']}' debe ser un solo caracter"
        )
    for field in ("deprecated", "hidden", "experimental", "experimentalcli", "kubernetes", "swarm"):
        assert isinstance(entry[field], bool), (
            f"{context}: el campo '{field}' de la opción '{entry['option']}' debe ser booleano"
        )


def test_usage_present_when_command_is_leaf(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    if "options" in doc:
        assert "usage" in doc and doc["usage"].strip(), (
            f"{yaml_path.name}: tiene 'options' pero no define 'usage'"
        )
        assert doc["usage"].startswith(doc["command"]), (
            f"{yaml_path.name}: 'usage' debería iniciar con el propio comando"
        )


def test_options_are_well_formed(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    for entry in doc.get("options", []):
        _validate_option_entry(entry, f"{yaml_path.name} [options]")


def test_inherited_options_are_well_formed(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    for entry in doc.get("inherited_options", []):
        _validate_option_entry(entry, f"{yaml_path.name} [inherited_options]")


def test_option_names_are_unique_within_file(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    names = [e["option"] for e in doc.get("options", [])]
    duplicates = {n for n in names if names.count(n) > 1}
    assert not duplicates, f"{yaml_path.name}: opciones duplicadas en 'options': {duplicates}"


def test_options_and_inherited_options_do_not_collide(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    own = {e["option"] for e in doc.get("options", [])}
    inherited = {e["option"] for e in doc.get("inherited_options", [])}
    overlap = own & inherited
    assert not overlap, (
        f"{yaml_path.name}: las opciones {overlap} están tanto en 'options' "
        "como en 'inherited_options'"
    )


# ---------------------------------------------------------------------------
# 4. Comandos "padre" (los que tienen 'cname' / 'clink')
# ---------------------------------------------------------------------------

def test_cname_and_clink_have_same_length(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    if "cname" in doc or "clink" in doc:
        assert "cname" in doc and "clink" in doc, (
            f"{yaml_path.name}: debe tener tanto 'cname' como 'clink' o ninguno"
        )
        assert len(doc["cname"]) == len(doc["clink"]), (
            f"{yaml_path.name}: 'cname' ({len(doc['cname'])} items) y 'clink' "
            f"({len(doc['clink'])} items) tienen longitudes distintas"
        )


def test_clink_filenames_match_cname_entries(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    for cname, clink in zip(doc.get("cname", []), doc.get("clink", [])):
        expected = cname.replace(" ", "_") + ".yaml"
        assert clink == expected, (
            f"{yaml_path.name}: cname '{cname}' debería enlazar a '{expected}', "
            f"pero clink dice '{clink}'"
        )


def test_clink_files_exist(yaml_path, loaded_docs, docs_dir):
    doc = loaded_docs[yaml_path]
    for clink in doc.get("clink", []):
        target = docs_dir / clink
        assert target.exists(), f"{yaml_path.name}: clink '{clink}' no existe en {docs_dir}"


def test_a_leaf_command_has_no_children(yaml_path, loaded_docs):
    """Un comando no debería mezclar 'options' propias con 'cname' (hoja vs. padre)."""
    doc = loaded_docs[yaml_path]
    if "options" in doc:
        assert "cname" not in doc, (
            f"{yaml_path.name}: tiene 'options' y 'cname' a la vez; se esperaba "
            "que fuera un comando hoja o un comando padre, no ambos"
        )


# ---------------------------------------------------------------------------
# 5. Referencias cruzadas plink/pname (relación bidireccional padre-hijo)
# ---------------------------------------------------------------------------

def test_plink_file_exists(yaml_path, loaded_docs, docs_dir):
    doc = loaded_docs[yaml_path]
    if "plink" in doc:
        target = docs_dir / doc["plink"]
        assert target.exists(), f"{yaml_path.name}: plink '{doc['plink']}' no existe en {docs_dir}"


def test_pname_and_plink_are_consistent(yaml_path, loaded_docs):
    doc = loaded_docs[yaml_path]
    if "pname" in doc or "plink" in doc:
        assert "pname" in doc and "plink" in doc, (
            f"{yaml_path.name}: debe tener tanto 'pname' como 'plink' o ninguno"
        )
        expected_plink = doc["pname"].replace(" ", "_") + ".yaml"
        assert doc["plink"] == expected_plink, (
            f"{yaml_path.name}: pname '{doc['pname']}' debería enlazar a "
            f"'{expected_plink}', pero plink dice '{doc['plink']}'"
        )


def test_parent_actually_lists_this_command_as_child(yaml_path, loaded_docs, docs_dir):
    """Si A dice que su padre es B, entonces B debe listar a A en su cname/clink."""
    doc = loaded_docs[yaml_path]
    if "plink" not in doc:
        return  # es la raíz (docker_scout.yaml), no tiene padre
    parent_path = docs_dir / doc["plink"]
    with open(parent_path, "r", encoding="utf-8") as fh:
        parent_doc = yaml.safe_load(fh)
    assert doc["command"] in parent_doc.get("cname", []), (
        f"{yaml_path.name}: el padre '{doc['plink']}' no lista a "
        f"'{doc['command']}' en su 'cname'"
    )
    assert yaml_path.name in parent_doc.get("clink", []), (
        f"{yaml_path.name}: el padre '{doc['plink']}' no lista '{yaml_path.name}' "
        "en su 'clink'"
    )


# ---------------------------------------------------------------------------
# 6. Documentación asociada (.md)
# ---------------------------------------------------------------------------

def test_corresponding_md_file_exists(yaml_path, docs_dir):
    # docker_scout_cves.yaml -> scout_cves.md ; docker_scout.yaml -> scout.md
    md_name = yaml_path.stem.replace("docker_scout", "scout", 1) + ".md"
    if md_name == ".md":
        md_name = "scout.md"
    md_path = docs_dir / md_name
    assert md_path.exists(), (
        f"{yaml_path.name}: no se encontró la documentación correspondiente "
        f"'{md_name}' en {docs_dir}"
    )
