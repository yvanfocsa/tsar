# modules/scanning_global.py
import shlex

MODULE = {
    "name":        "Scanning – Service & Web",
    "description": "nmap, whatweb, gobuster et testssl.sh",
    "category":    "Recon",
    "hidden":      False,
    "schema": [
        {"name": "target", "type": "string", "placeholder": "exemple.com ou 1.2.3.4", "required": True},
        {"name": "mode",   "type": "select", "choices": ["quick", "full"], "default": "quick"},
    ],
    "cmd": lambda p: {
        "quick": [
            "bash", "-c",
            " && ".join([
                # scan SYN top-100
                "nmap -sS -T4 --top-ports 100 " + shlex.quote(p["target"]),
                # fingerprint web léger
                "whatweb " + shlex.quote(p["target"]) + " || true",
            ])
        ],
        "full": [
            "bash", "-c",
            " && ".join([
                # scan complet + scripts
                "nmap -sS -sV -sC -O -T4 -Pn --version-intensity 9 " + shlex.quote(p["target"]),
                # brute force répertoires
                "gobuster dir -u " + shlex.quote(f"http://{p['target']}") + " -w /usr/share/wordlists/dirb/common.txt || true",
                # SSL/TLS
                "testssl.sh --quiet " + shlex.quote(p["target"]) + " || true",
            ])
        ],
    }[p["mode"]],
}

