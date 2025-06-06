# web/app/tasks.py
from __future__ import annotations

import datetime
import os
import docker
import logging
from celery import Celery
from celery.signals import worker_process_init

from .modules import MODULES, load_modules

logging.basicConfig(level=logging.INFO)

celery = Celery("tsar")

@worker_process_init.connect
def init_modules_on_worker_start(**kwargs):
    logging.info("Celery worker process starting, loading modules...")
    load_modules()
    logging.info(f"Modules loaded in worker: {[m['name'] for m in MODULES]}")


@celery.task(name="tsar.run_job")
def run_job(module_name: str, params: dict, user_sub: str) -> int | None:
    """Exécute un module et génère un rapport PDF."""
    from . import create_app, db
    from .models import Report
    from .pdf import generate_report
    from .pdf_crypto import encrypt

    # On crée une app "nue" SANS routes NI context processors
    app = create_app(register_blueprints=False, register_context_processors=False)
    with app.app_context():
        logging.info(f"Début du job '{module_name}' pour l'utilisateur {user_sub}")

        mod = next((m for m in MODULES if m["name"] == module_name), None)
        if not mod:
            logging.error(f"FATAL: Module '{module_name}' introuvable dans le worker.")
            return None

        cmd = mod["cmd"](params)
        container_name = os.getenv("TOOLBOX_CONTAINER", "toolbox")
        try:
            client = docker.from_env()
            container = client.containers.get(container_name)
            exec_res = container.exec_run(cmd, stdout=True, stderr=True)
            output = exec_res.output.decode(errors="ignore")
            logging.info(f"Exécution de la commande pour '{module_name}' terminée.")
        except docker.errors.NotFound:
            output = f"ERREUR : Le conteneur Docker '{container_name}' est introuvable."
            logging.error(output)
        except Exception as exc:
            output = f"ERREUR : {exc!s}"
            logging.error(f"Erreur lors de l'exécution du job : {output}")

        try:
            # render_template n'essaiera plus d'exécuter le context_processor
            pdf_bytes = generate_report(
                "stdout_report.html",
                {
                    "module": mod,
                    "params": params,
                    "output": output,
                    "date": datetime.datetime.utcnow(),
                },
            )

            cipher = encrypt(pdf_bytes)
            pdf_name = f"{module_name.replace(' ', '_')}_{datetime.datetime.utcnow():%Y%m%d%H%M}.pdf"

            report = Report(user_sub=user_sub, filename=pdf_name, pdf_data=cipher)
            
            db.session.add(report)
            db.session.commit()

            logging.info(f"Rapport #{report.id} ('{pdf_name}') sauvegardé avec succès.")
            return report.id

        except Exception as e:
            logging.error(f"Erreur lors de la génération ou sauvegarde du PDF : {e}", exc_info=True)
            db.session.rollback()
            return None
