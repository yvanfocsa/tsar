# web/app/modules.py

"""
Chargement dynamique des modules “outils” depuis ../modules
Les MODULES marqués hidden=True sont ignorés,
et les doublons de nom sont automatiquement filtrés.
"""

import importlib.util as iutil
import logging
import sys
import os
from typing import Dict, List
import pathlib

MODULES: List[dict] = []  # utilisé par routes.py/get_categories()

def load_modules() -> None:
    """
    Parcourt ../modules/*.py, importe chaque module, récupère sa variable MODULE (dict),
    et l’ajoute à MODULES si elle n’est pas cachée et n’existe pas déjà.
    """
    # Chemin vers ../modules (au même niveau que web/)
    root = pathlib.Path(__file__).resolve().parents[1] / "modules"
    if not root.exists():
        logging.warning("Dossier modules introuvable : %s", root)
        return

    # S’assurer que le dossier parent (par ex. /app) est dans sys.path
    parent_dir = str(root.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    for file in root.rglob("*.py"):
        name = file.stem
        # On définit le nom de module comme modules.<nom_de_fichier>
        full_module_name = f"modules.{name}"
        spec = iutil.spec_from_file_location(full_module_name, str(file))
        if spec is None or spec.loader is None:
            continue

        # S’assurer que le dossier modules est dans sys.path
        modules_dir = str(root)
        if modules_dir not in sys.path:
            sys.path.insert(0, modules_dir)

        mod = iutil.module_from_spec(spec)
        # Fix du package pour que les imports internes “modules.xxx” fonctionnent
        mod.__package__ = full_module_name
        try:
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        except Exception as err:
            logging.error("Erreur import %s : %s", file.name, err, exc_info=True)
            continue

        meta = getattr(mod, "MODULE", None)
        if not isinstance(meta, dict):
            continue

        # ignore les modules cachés
        if meta.get("hidden", False):
            continue

        # filtre les doublons de nom
        if any(m["name"] == meta["name"] for m in MODULES):
            logging.warning("Module %s déjà chargé, on l’ignore", meta["name"])
            continue

        MODULES.append(meta)

def get_categories() -> Dict[str, List[dict]]:
    """
    Retourne { catégorie: [MODULES triés par name] } pour affichage.
    """
    cats: Dict[str, List[dict]] = {}
    for mod in MODULES:
        cats.setdefault(mod["category"], []).append(mod)

    # tri alphabétique dans chaque catégorie
    for lst in cats.values():
        lst.sort(key=lambda x: x["name"].lower())
    return cats

