"""Shared policy functions, CSRF validation and JSON input validation.
These functions are ordinary Python functions, not custom decorators.
"""
import secrets
from flask import abort, g, request, session


def can_read_notes(user):
    return user is not None and user["role"] in ("viewer", "editor", "admin")


def can_edit_notes(user):
    # Role decides the operation. It does not grant access to another owner.
    # TODO ROLE: implement the operation permission. Fail closed until then.
    return False


def owns_note(user, note):
    return note is not None and user is not None and note["owner_id"] == user["id"]


def require_user():
    if g.user is None:
        abort(401)
    return g.user


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def check_csrf():
    # Browser forms submit a hidden field. API clients send a header.
    # Neither a cookie nor a role is a substitute for this request token.
    supplied = request.headers.get("X-CSRF-Token") if request.is_json else request.form.get("csrf_token")
    # For malformed/wrong-type API bodies we still accept the header so the
    # content-type/JSON tests reach the intended validation control.
    supplied = request.headers.get("X-CSRF-Token") or supplied
    expected = session.get("csrf_token")
    if not isinstance(supplied, str) or not isinstance(expected, str):
        abort(403)
    if not secrets.compare_digest(supplied, expected):
        abort(403)


def read_json_object():
    if not request.is_json:
        abort(415)
    # Malformed JSON raises BadRequest (400). Do not silently turn it into {}.
    data = request.get_json()
    if not isinstance(data, dict) or not data:
        abort(400)
    return data


def validate_changes(data):
    allowed_fields = {"title", "content"}
    if set(data) - allowed_fields:
        abort(400)  # Reject the WHOLE request, including otherwise valid fields.
    for field, value in data.items():
        if not isinstance(value, str):
            abort(400)
        maximum = 80 if field == "title" else 2000
        if len(value) > maximum or (field == "title" and not value.strip()):
            abort(400)
    return data


def public_note(note):
    # Response allowlist: database columns are not automatically public fields.
    return {"id": note["id"], "title": note["title"], "content": note["content"]}
