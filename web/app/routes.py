"""
Routes principaux : dashboard, exécution de modules, génération + téléchargement
de rapports et flux RSS.

Stack 100 % locale (pas d'IA) + Celery :
  • aucune importation directe de .tasks (évite les boucles)
  • appel asynchrone via current_app.celery.send_task(...)
"""

from __future__ import annotations

import socket
import shlex                               # ← pour wrapper PID
from datetime import datetime, timedelta, time
from io import BytesIO
from typing import Any

import docker
import feedparser
import psutil
import requests
from bs4 import BeautifulSoup               # ← pour nettoyer le contenu RSS
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    stream_with_context,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from . import db
from .models import Report, ScanLog, UserProfile, ScheduledTask
from .modules import MODULES, get_categories
from .pdf_crypto import decrypt

# ─────────── Blueprint & LoginManager ───────────
bp = Blueprint("routes", __name__)
login_manager = LoginManager()
login_manager.login_view = "routes.login"

# ─────────── USER SESSION ───────────
class User(UserMixin):
    def __init__(self, sub: str, name: str):
        self.id   = sub
        self.sub  = sub
        self.name = name


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    data = session.get("user")
    if not data:
        return None
    return User(data["sub"], data.get("name", data.get("email", "")))

# ─────────── HELPERS ───────────
def _get_ips() -> tuple[str, str]:
    priv = socket.gethostbyname(socket.gethostname())
    try:
        pub = requests.get("https://api.ipify.org", timeout=2).text
    except requests.RequestException:
        pub = "n/a"
    return pub, priv

# ─────────── AUTH0 ───────────
@bp.route("/login")
def login():
    redirect_uri = url_for("routes.callback", _external=True)
    return current_app.oauth.auth0.authorize_redirect(
        redirect_uri=redirect_uri,
        audience=current_app.config["AUTH0_AUDIENCE"],
    )

@bp.route("/auth/callback")
def callback():
    token = current_app.oauth.auth0.authorize_access_token()
    user  = current_app.oauth.auth0.parse_id_token(token, nonce=token.get("nonce"))
    session["user"] = dict(user)
    login_user(User(user["sub"], user.get("name", user.get("email", ""))))
    return redirect(url_for("routes.index"))

@bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(
        f'https://{current_app.config["AUTH0_DOMAIN"]}/v2/logout?'
        f'returnTo={url_for("routes.index", _external=True)}&'
        f'client_id={current_app.config["AUTH0_CLIENT_ID"]}'
    )

# ─────────── SYSTEM METRICS ───────────
@bp.route("/metrics/ram")
@login_required
def metrics_ram():
    mem   = psutil.virtual_memory()
    used  = (mem.total - mem.available) // 1024**2
    total = mem.total // 1024**2
    return f"{used} MiB / {total} MiB"

@bp.route("/metrics/ram/json")
@login_required
def metrics_ram_json():
    mem   = psutil.virtual_memory()
    used  = (mem.total - mem.available) // 1024**2
    total = mem.total // 1024**2
    return jsonify({"used": used, "total": total})

@bp.route("/metrics/scans/json")
@login_required
def metrics_scans_json():
    """Nombre de scans par jour sur 30 jours glissants (utilisateur courant)."""
    since = datetime.utcnow() - timedelta(days=29)
    rows  = (
        db.session.query(ScanLog.created_at)
        .filter(ScanLog.user_sub == current_user.sub)
        .filter(ScanLog.created_at >= since)
        .all()
    )

    counts: dict[str, int] = {}
    for (dt,) in rows:
        day = dt.date().isoformat()
        counts[day] = counts.get(day, 0) + 1

    labels, data = zip(*sorted(counts.items())) if counts else ([], [])
    return jsonify({"labels": labels, "data": data})

# ─────────── DASHBOARD ───────────
@bp.route("/")
@login_required
def index():
    pub_ip, priv_ip = _get_ips()
    mem   = psutil.virtual_memory()
    ram   = f"{(mem.total - mem.available) // 1024**2} MiB / {mem.total // 1024**2} MiB"
    metrics = {
        "RAM utilisée": ram,
        "IP publique":  pub_ip,
        "IP privée":    priv_ip,
    }
    favoris = [m for m in MODULES if m["name"] in session.get("favorites", [])]
    logs    = (
        ScanLog.query.filter_by(user_sub=current_user.sub)
        .order_by(ScanLog.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template("dashboard.html", metrics=metrics, favoris=favoris, logs=logs)

# ─────────── MODULES LIST ───────────
@bp.route("/modules")
@login_required
def modules_home():
    return render_template("modules.html", cats=get_categories())

# ─────────── FAVORIS ───────────
@bp.route("/modules/<name>/favorite", methods=["POST"])
@login_required
def toggle_favorite(name: str):
    fav: list[str] = session.setdefault("favorites", [])
    if name in fav:
        fav.remove(name)
    else:
        fav.append(name)
    session.modified = True
    star = "★" if name in fav else "☆"
    return (
        f'<button hx-post="{url_for("routes.toggle_favorite", name=name)}" '
        'hx-swap="outerHTML" class="fav-btn text-2xl">'
        f"{star}</button>",
        200,
        {"Content-Type": "text/html"},
    )

# ─────────── LIVE TERMINAL (SSE) ───────────
@bp.route("/modules/<name>/terminal")
@login_required
def module_live(name: str):
    mod = next((m for m in MODULES if m["name"] == name), None)
    if not mod:
        abort(404)
    return render_template("module_live.html", mod=mod)

@bp.route("/modules/<name>/stream")
@login_required
def module_stream(name: str):
    mod = next((m for m in MODULES if m["name"] == name), None)
    if not mod:
        abort(404)

    target   = request.args.get("target", "").strip()
    mode     = request.args.get("mode", "quick")
    run_uuid = request.args.get("run_uuid", "")  # ← ID unique du front

    # --- commande de base générée par le module ---
    base_cmd = mod["cmd"]({"target": target, "mode": mode})

    # --- wrapper pour enregistrer le PID si run_uuid présent ---
    if run_uuid:
        pidfile   = f"/tmp/scan_{run_uuid}.pid"
        inner_cmd = " ".join(shlex.quote(x) for x in base_cmd)
        base_cmd  = [
            "bash", "-c",
            f'echo $$ > {pidfile}; exec {inner_cmd}'
        ]

    # --- exécution dans toolbox ---
    cli = docker.from_env()
    tbx = current_app.config.get("TOOLBOX_CONTAINER", "toolbox")
    try:
        container = cli.containers.get(tbx)
    except docker.errors.NotFound:
        return Response("data: ERREUR: conteneur toolbox introuvable\n\n",
                        mimetype="text/event-stream")

    exec_id = cli.api.exec_create(container.id, base_cmd, tty=False)["Id"]
    stream  = cli.api.exec_start(exec_id, stream=True, demux=True)

    db.session.add(
        ScanLog(user_sub=current_user.sub, module=name,
                target=target or None, mode=mode)
    )
    db.session.commit()

    @stream_with_context
    def events():
        yield f"data: ▶ Exécution : {' '.join(base_cmd)}\n\n"
        for out, err in stream:
            chunk = (out or err).decode(errors="ignore")
            for line in chunk.splitlines():
                yield f"data: {line}\n\n"
        yield "data: * Fin du flux.\n\n"
        # Nettoyage du pidfile terminé avec succès
        if run_uuid:
            cli.api.exec_create(container.id,
                                ["bash", "-c", f"rm -f /tmp/scan_{run_uuid}.pid"])

    return current_app.response_class(events(), mimetype="text/event-stream")

# ─────────── STOP MODULE ───────────
@bp.route("/modules/<name>/stop/<run_uuid>", methods=["POST"])
@login_required
def stop_module(name: str, run_uuid: str):
    """Interrompt immédiatement le scan identifié par run_uuid."""
    cli = docker.from_env()
    tbx = current_app.config.get("TOOLBOX_CONTAINER", "toolbox")
    try:
        container = cli.containers.get(tbx)
    except docker.errors.NotFound:
        return ("Conteneur toolbox introuvable", 404)

    pidfile  = f"/tmp/scan_{run_uuid}.pid"
    kill_cmd = (
        f'bash -c "[ -f {pidfile} ] && kill -9 -$(cat {pidfile}) && rm -f {pidfile}"'
    )
    exec_id = cli.api.exec_create(container.id, ["bash", "-c", kill_cmd], tty=False)
    cli.api.exec_start(exec_id["Id"])
    return ("Command KILLED", 200)

# ─────────── FORM / GÉNÉRATEUR DE RAPPORT ───────────
@bp.route("/modules/<name>")
@login_required
def module_form(name: str):
    mod = next((m for m in MODULES if m["name"] == name), None)
    if not mod:
        abort(404)

    if mod["name"] == "Rapport – Génération":
        targets = (
            ScanLog.query.filter_by(user_sub=current_user.sub)
            .filter(ScanLog.target.isnot(None))
            .with_entities(ScanLog.target)
            .distinct()
            .all()
        )
        return render_template("module_form.html", mod=mod,
                               target_list=[t[0] for t in targets])

    return render_template("module_form.html", mod=mod)

# ─────────── EXECUTE MODULE / GENERATE PDF ───────────
@bp.route("/modules/<name>/run", methods=["POST"])
@login_required
def module_run(name: str):
    mod = next((m for m in MODULES if m["name"] == name), None)
    if not mod:
        abort(404)

    if request.is_json:
        params: dict[str, Any] = request.get_json() or {}
    else:
        params = {
            field["name"]: (
                request.form.getlist(field["name"])
                if field["type"] == "multiselect"
                else request.form.get(field["name"], "")
            )
            for field in mod.get("schema", [])
        }

    job = current_app.celery.send_task("tsar.run_job",
                                       args=[name, params, current_user.sub])

    is_ajax = request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    return jsonify({"job_id": job.id}) if is_ajax else redirect(url_for("routes.reports"))

# ─────────── PDF REPORTS ───────────
@bp.route("/reports")
@login_required
def reports():
    reps = (
        Report.query.filter_by(user_sub=current_user.sub)
        .order_by(Report.created_at.desc())
        .all()
    )
    mod_report = next((m for m in MODULES if m["name"] == "Rapport – Génération"),
                      None)
    targets = (
        ScanLog.query.filter_by(user_sub=current_user.sub)
        .filter(ScanLog.target.isnot(None))
        .with_entities(ScanLog.target)
        .distinct()
        .all()
    )
    return render_template("reports.html",
                           reports=reps, mod_report=mod_report,
                           target_list=[t[0] for t in targets])

@bp.route("/reports/<int:rid>")
@login_required
def download_report(rid: int):
    rep = Report.query.get_or_404(rid)
    if rep.user_sub != current_user.sub:
        abort(403)
    pdf = decrypt(rep.pdf_data)
    return send_file(
        BytesIO(pdf),
        as_attachment=True,
        download_name=rep.filename,
        mimetype="application/pdf",
    )

# ─────────── PROFIL UTILISATEUR ───────────
@bp.route("/profile")
@login_required
def profile():
    """Page de paramètres du compte utilisateur."""
    # Le context_processor s'occupe de 'display_name' et 'email'.
    # On passe juste l'objet 'profile' pour ses autres attributs.
    profile = UserProfile.query.filter_by(user_sub=current_user.sub).first()
    return render_template("profile.html", profile=profile)

@bp.route("/profile", methods=["POST"])
@login_required
def update_profile():
    """Mise à jour du profil utilisateur."""
    profile = UserProfile.query.filter_by(user_sub=current_user.sub).first()
    if not profile:
        profile = UserProfile(user_sub=current_user.sub)
        db.session.add(profile)

    # Nom d'affichage
    display_name = request.form.get("display_name", "").strip()
    if display_name:
        profile.display_name = display_name

    # Photo de profil
    avatar_file = request.files.get("avatar")
    if avatar_file and avatar_file.filename:
        # Vérifier le type de fichier
        if avatar_file.mimetype and avatar_file.mimetype.startswith("image/"):
            # Limiter la taille (5MB max)
            avatar_file.seek(0, 2)  # Aller à la fin
            file_size = avatar_file.tell()
            avatar_file.seek(0)  # Revenir au début
            
            if file_size <= 5 * 1024 * 1024:  # 5MB max
                profile.avatar_data = avatar_file.read()
                profile.avatar_mime = avatar_file.mimetype

    db.session.commit()
    return redirect(url_for("routes.profile"))

@bp.route("/profile/avatar")
@login_required
def profile_avatar():
    """Retourne l'avatar de l'utilisateur courant."""
    profile = UserProfile.query.filter_by(user_sub=current_user.sub).first()
    if not profile or not profile.avatar_data:
        # Retourner un avatar par défaut (404 pour déclencher le fallback)
        abort(404)
    
    return Response(
        profile.avatar_data,
        mimetype=profile.avatar_mime or "image/jpeg"
    )

# ─────────── TÂCHES PLANIFIÉES ───────────
@bp.route("/scheduled")
@login_required
def scheduled_tasks():
    """Page de gestion des tâches planifiées."""
    tasks = (
        ScheduledTask.query.filter_by(user_sub=current_user.sub)
        .order_by(ScheduledTask.created_at.desc())
        .all()
    )
    return render_template("scheduled.html", tasks=tasks, modules=MODULES)

@bp.route("/scheduled/create", methods=["POST"])
@login_required
def create_scheduled_task():
    """Créer une nouvelle tâche planifiée."""
    name = request.form.get("name", "").strip()
    module_name = request.form.get("module_name", "").strip()
    target = request.form.get("target", "").strip()
    mode = request.form.get("mode", "quick")
    schedule_type = request.form.get("schedule_type", "daily")
    schedule_time_str = request.form.get("schedule_time", "09:00")
    schedule_day = request.form.get("schedule_day")

    if not name or not module_name:
        return redirect(url_for("routes.scheduled_tasks"))

    # Parser l'heure
    try:
        hour, minute = map(int, schedule_time_str.split(":"))
        schedule_time = time(hour, minute)
    except ValueError:
        schedule_time = time(9, 0)  # défaut 09:00

    # Calculer la prochaine exécution
    now = datetime.utcnow()
    next_run = _calculate_next_run(now, schedule_type, schedule_time, schedule_day)

    task = ScheduledTask(
        user_sub=current_user.sub,
        name=name,
        module_name=module_name,
        target=target or None,
        mode=mode,
        schedule_type=schedule_type,
        schedule_time=schedule_time,
        schedule_day=int(schedule_day) if schedule_day else None,
        next_run=next_run
    )

    db.session.add(task)
    db.session.commit()
    return redirect(url_for("routes.scheduled_tasks"))

@bp.route("/scheduled/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_scheduled_task(task_id: int):
    """Activer/désactiver une tâche planifiée."""
    task = ScheduledTask.query.get_or_404(task_id)
    if task.user_sub != current_user.sub:
        abort(403)
    
    task.is_active = not task.is_active
    db.session.commit()
    return redirect(url_for("routes.scheduled_tasks"))

@bp.route("/scheduled/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_scheduled_task(task_id: int):
    """Supprimer une tâche planifiée."""
    task = ScheduledTask.query.get_or_404(task_id)
    if task.user_sub != current_user.sub:
        abort(403)
    
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("routes.scheduled_tasks"))

def _calculate_next_run(now, schedule_type, schedule_time, schedule_day=None):
    """Calcule la prochaine exécution d'une tâche."""
    next_date = now.date()
    
    if schedule_type == "daily":
        # Si l'heure est déjà passée aujourd'hui, on passe au lendemain
        if now.time() >= schedule_time:
            next_date += timedelta(days=1)
    
    elif schedule_type == "weekly":
        # schedule_day = 0 (lundi) à 6 (dimanche)
        target_weekday = int(schedule_day) if schedule_day else 0
        days_ahead = target_weekday - now.weekday()
        if days_ahead <= 0:  # La cible est aujourd'hui ou dans le passé
            days_ahead += 7
        next_date += timedelta(days=days_ahead)
    
    elif schedule_type == "monthly":
        # schedule_day = jour du mois (1-31)
        target_day = int(schedule_day) if schedule_day else 1
        if now.day <= target_day and now.time() < schedule_time:
            # Ce mois-ci
            next_date = next_date.replace(day=target_day)
        else:
            # Mois prochain
            if now.month == 12:
                next_date = next_date.replace(year=now.year + 1, month=1, day=target_day)
            else:
                next_date = next_date.replace(month=now.month + 1, day=target_day)
    
    return datetime.combine(next_date, schedule_time)

# ─────────── FLUX RSS VEILLE ───────────
@bp.route("/veille")
@login_required
def veille():
    feed = feedparser.parse("https://cyberveille.curated.co/issues.rss")
    articles: list[dict[str, Any]] = []

    for entry in feed.entries[:20]:
        published = entry.get("published", "")
        soup = BeautifulSoup(entry.summary, "html.parser")

        # Supprimer tous les <h3> (titres de sections)
        for h3 in soup.find_all("h3"):
            h3.decompose()

        # Supprimer tout ce qui suit le premier <hr>
        hr = soup.find("hr")
        if hr:
            for sibling in hr.find_next_siblings():
                sibling.decompose()
            hr.decompose()

        # Pour chaque <h4>, créer un article distinct
        for h4 in soup.find_all("h4"):
            # Titre et lien
            a_tag = h4.find("a")
            if not a_tag:
                continue
            title = a_tag.get_text().strip()
            link = a_tag.get("href", "").strip()

            # Premier <p> après le <h4> → résumé texte
            summary_html = ""
            summary_p = h4.find_next_sibling("p")
            if summary_p:
                summary_html = str(summary_p)

            # Deuxième <p> après le <h4> → source (texte du <a>)
            source = ""
            if summary_p:
                source_p = summary_p.find_next_sibling("p")
                if source_p and source_p.find("a"):
                    source = source_p.get_text().strip()

            # Première balise <img> qui suit → vignette (si présente)
            img_url = ""
            next_a = h4.find_next_sibling("a")
            if next_a and next_a.find("img"):
                img_tag = next_a.find("img")
                img_url = img_tag.get("src", "").strip()

            articles.append({
                "title":     title,
                "link":      link,
                "published": published,
                "summary":   summary_html,
                "source":    source,
                "image_url": img_url,
            })

    return render_template("veille.html", articles=articles)
