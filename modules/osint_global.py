# modules/osint_global.py
"""OSINT – Collecte passive / active d'informations publiques sur une cible.

Outils rapides :
  • subfinder
  • theHarvester

Mode *full* (plus complet) :
  • subfinder          (passif + actif)
  • amass enum -active
  • theHarvester
  • Shodan : si une clé API est fournie

Le module suit la même convention que les autres :
champ *target*, sélecteur *mode* et champ facultatif *shodan_api*.
"""
import shlex, os

def _build_cmd(p: dict) -> list[str]:
    target = shlex.quote(p["target"])
    mode: str = p.get("mode", "quick")
    shodan_api: str = p.get("shodan_api", "").strip()

    parts: list[str] = [
        f"subfinder -d {target} || true",
        f"theHarvester -d {target} -b bing,google,pastebin || true",
    ]

    if mode == "full":
        parts.insert(1, f"amass enum -d {target} -o - || true")

    if shodan_api:
        # Initialise Shodan (si pas déjà fait) et lance la recherche
        parts.append(
            f"shodan init {shlex.quote(shodan_api)} && "
            f"shodan host {target} || true"
        )

    return ["bash", "-c", " && ".join(parts)]

MODULE = {
    "name": "OSINT – Collecte",
    "description": "subfinder, amass, theHarvester et Shodan",
    "category": "Recon",
    "hidden": False,
    "schema": [
        {"name": "target",      "type": "string", "placeholder": "exemple.com", "required": True},
        {"name": "mode",        "type": "select",  "choices": ["quick", "full"], "default": "quick"},
        {"name": "shodan_api",  "type": "string",  "placeholder": "clé API Shodan (optionnel)", "required": False},
    ],
    "cmd": _build_cmd,
}
