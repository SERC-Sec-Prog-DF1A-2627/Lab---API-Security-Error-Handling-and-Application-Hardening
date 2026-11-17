"""Private Notes teaching application. Run: python app.py
A factory returns a fresh app for each test. Read from top to bottom:
configuration -> request setup -> web routes -> API routes -> error responses.
"""
from pathlib import Path
import os
import secrets
import uuid
import click
from flask import Flask, abort, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash
from db import close_db, find_note, find_user, get_db, init_db, legacy_update, notes_for, update_note, user_by_id
from security import can_edit_notes, can_read_notes, check_csrf, csrf_token, owns_note, public_note, read_json_object, require_user, validate_changes



# Messages describe the outcome without exposing library exception strings.
SAFE_MESSAGES = {400:"Invalid request.", 401:"Authentication required.",
                 403:"Request not permitted.", 404:"Not found.",
                 405:"Method not allowed.", 413:"Request too large.",
                 415:"JSON content type required.", 429:"Too many requests.",
                 500:"An unexpected error occurred.", 501:"Exercise endpoint not implemented."}


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=str(Path(__file__).parent / "instance" / "notes.sqlite"),
        DEBUG=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        # Codespaces browser forwarding uses HTTPS. Local HTTP uses False.
        SESSION_COOKIE_SECURE=bool(os.environ.get("CODESPACES")),
        MAX_CONTENT_LENGTH=16 * 1024,
        LAB_MODE=False,
    )
    if test_config:
        app.config.update(test_config)
    app.teardown_appcontext(close_db)
    app.jinja_env.globals["csrf_token"] = csrf_token
    app.jinja_env.globals["can_edit_notes"] = can_edit_notes
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    if not Path(app.config["DATABASE"]).exists():
        with app.app_context():
            init_db()

    @app.cli.command("reset-db")
    def reset_db_command():
        init_db()
        click.echo("Reset this exercise's fictional data.")

    @app.before_request
    def load_request():
        # Create the correlation ID before any database work can fail.
        g.request_id = uuid.uuid4().hex  # Do not trust a caller's request ID.
        # The role comes from the database every request, not a JSON field.
        g.user = user_by_id(session.get("user_id")) if session.get("user_id") else None



    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            check_csrf()
            user = find_user(request.form.get("username", ""))
            if user is None or not check_password_hash(user["password_hash"], request.form.get("password", "")):
                return render_template("login.html", error="Invalid username or password."), 401
            session.clear()  # Drop pre-login state; create a fresh CSRF token.
            session["user_id"] = user["id"]
            csrf_token()
            return redirect(url_for("notes_page"))
        return render_template("login.html", error=None)

    @app.post("/logout")
    def logout():
        check_csrf()
        session.clear()
        return redirect(url_for("login"))

    @app.get("/")
    def notes_page():
        if g.user is None:
            return redirect(url_for("login"))
        if not can_read_notes(g.user):
            abort(403)
        return render_template("notes.html", user=g.user, notes=notes_for(g.user["id"]))

    @app.post("/notes/<int:note_id>/edit")
    def edit_note_web(note_id):
        user = require_user()
        check_csrf()
        # WEB ROLE CHECK: same policy as the API update route.
        if not can_edit_notes(user):
            abort(403)
        note = find_note(note_id)
        if not owns_note(user, note):
            abort(404)
        data = validate_changes({"title": request.form.get("title", ""),
                                 "content": request.form.get("content", "")})
        update_note(note_id, user["id"], data["title"], data["content"])
        return redirect(url_for("notes_page"))

    @app.get("/api/notes/<int:note_id>")
    def get_note_api(note_id):
        # TODO GET: authenticate, check role and ownership, return public JSON.
        abort(501)

    @app.patch("/api/notes/<int:note_id>")
    def patch_note_api(note_id):
        # TODO PATCH: authenticate, CSRF, role, ownership, validate, update.
        abort(501)

    # This fault route exists ONLY when a test or lab_client explicitly enables
    # LAB_MODE. python app.py does not enable it. No submitted data causes it.
    if app.config["LAB_MODE"]:
        @app.get("/api/lab-fault")
        def lab_fault():
            require_user()
            raise RuntimeError("SYNTHETIC_SECRET in SQL SELECT * FROM private_table at /srv/internal/demo.py")

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        # Preserve protocol headers such as Allow (405) and Retry-After.
        response = error.get_response()
        response.data = app.json.dumps({"error": SAFE_MESSAGES.get(error.code, "Request failed."),
                                        "request_id": g.request_id})
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return jsonify(error=SAFE_MESSAGES[500], request_id=g.request_id), 500

    @app.after_request
    def finish_response(response):
        response.headers["X-Request-ID"] = g.request_id
        response.headers["Cache-Control"] = "no-store"


        return response

    return app


if __name__ == "__main__":
    # Development server only. Keep the forwarded port PRIVATE.
    create_app().run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
