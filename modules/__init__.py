from importlib import import_module
__all__ = ["recon","scanning","exploit","osint","reporting","reverse_shell"]
for m in __all__:
    globals()[m] = import_module(f"modules.{m}")