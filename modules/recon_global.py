# modules/recon_passif.py
import shlex

MODULE = {
    "name":        "Reconnaissance (passif)",
    "description": "subfinder, whois et dnsenum",
    "category":    "Recon",
    "hidden":      False,
    "schema": [
        {"name": "target", "type": "string", "placeholder": "exemple.com ou 1.2.3.4", "required": True},
        {"name": "mode",   "type": "select", "choices": ["quick", "full"], "default": "quick"},
    ],
    "cmd": lambda p: [
        "bash", "-c",
        " && ".join([
            f"subfinder -d {shlex.quote(p['target'])} || true",
            f"whois {shlex.quote(p['target'])} || true",
            # dnsenum uniquement en full
            f"dnsenum {shlex.quote(p['target'])} || true" if p["mode"] == "full" else "echo 'dnsenum skipped en quick'"
        ])
    ],
}

