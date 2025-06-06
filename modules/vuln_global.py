# modules/vuln_global.py
import shlex

MODULE = {
    "name":        "Vuln Assessment – Complet",
    "description": "nuclei, nikto, openvas et wpscan",
    "category":    "Vulnerability",
    "hidden":      False,
    "schema": [
        {"name": "target", "type": "string", "placeholder": "exemple.com ou 1.2.3.4", "required": True},
        {"name": "mode",   "type": "select", "choices": ["quick", "full"], "default": "quick"},
    ],
    "cmd": lambda p: {
        "quick": [
            "bash", "-c",
            " && ".join([
                f"nuclei -u {shlex.quote(p['target'])} || true",
                f"nikto -h {shlex.quote(p['target'])} || true",
            ])
        ],
        "full": [
            "bash", "-c",
            " && ".join([
                f"nuclei -u {shlex.quote(p['target'])} || true",
                f"nikto -h {shlex.quote(p['target'])} || true",
                f"openvas-cli -h {shlex.quote(p['target'])} || true",
                f"wpscan --url {shlex.quote(p['target'])} --enumerate u || true",
            ])
        ],
    }[p["mode"]],
}
