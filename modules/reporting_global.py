# modules/reporting_global.py
import shlex  # Pour shlex.quote

# ─────────── Imports des sous-modules conservés ───────────
from modules.recon_global     import MODULE as _mod_recon
from modules.scanning_global  import MODULE as _mod_scan
from modules.vuln_global      import MODULE as _mod_vuln
from modules.exploit_global   import MODULE as _mod_exploit
# (cve_analysis supprimé)

# ─────────── Mapping section → module ───────────
MODULE_MAP = {
    "recon":   _mod_recon,
    "scan":    _mod_scan,
    "vuln":    _mod_vuln,
    "exploit": _mod_exploit,
}

MODULE = {
    "name":        "Rapport – Génération",
    "description": "génère le rapport PDF modulable et chiffré",
    "category":    "Reporting",
    "binary":      "rapport",
    "hidden":      False,
    "schema": [
        {
            "name":        "target",
            "type":        "string",
            "placeholder": "exemple.com ou 1.2.3.4",
            "required":    True,
        },
        {
            "name":    "sections",
            "type":    "multiselect",
            "choices": list(MODULE_MAP.keys()),   # ["recon","scan","vuln","exploit"]
        },
    ],
    "cmd": lambda p: _build_report_cmd(p),
}

# ───────────────────────────────────────────────────────────
def _build_report_cmd(p: dict) -> list[str]:
    """
    1) lance chaque module sélectionné en arrière-plan
    2) attend la fin des jobs
    3) concatène tous les /tmp/<section>.log dans stdout
    """
    parts_bg:  list[str] = []   # commandes parallèles
    parts_cat: list[str] = []   # concaténation finale

    for sec in p.get("sections", []):
        if sec not in MODULE_MAP:
            continue

        sub_params = {
            "target": p.get("target", ""),
            "mode":   p.get("mode", "quick"),
        }

        # transforme ["bash","-c","…"] → chaîne shell
        cmd_list   = MODULE_MAP[sec]["cmd"](sub_params)
        single_cmd = " ".join(shlex.quote(str(part)) for part in cmd_list)

        # exécution en tâche de fond + log dédié
        parts_bg.append(f"({single_cmd}) > /tmp/{sec}.log 2>&1 &")
        # marqueur + concaténation dans l’ordre
        parts_cat.append(
            f"echo '===== Début section {sec} =====' && cat /tmp/{sec}.log"
        )

    # rien de sélectionné
    if not parts_bg:
        return ["bash", "-c", "echo 'Aucune section sélectionnée'"]

    # pipeline final : exécute → attend → assemble
    cmd_parallel      = " && ".join(parts_bg)
    cmd_wait_and_cat  = "wait && " + " && ".join(parts_cat)
    final_shell_cmd   = f"{cmd_parallel} && {cmd_wait_and_cat}"

    return ["bash", "-c", final_shell_cmd]

