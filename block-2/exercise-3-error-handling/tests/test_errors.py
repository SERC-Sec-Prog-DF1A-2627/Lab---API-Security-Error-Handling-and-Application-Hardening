import io
import json
import logging
from app import create_app
from lab_client import sign_in


def capture(app):
    stream = io.StringIO()
    app.extensions["security_logger"].handlers = [logging.StreamHandler(stream)]
    return stream


def test_http_errors_safe_and_correlated(client, login, app):
    login()
    stream = capture(app)
    response = client.get("/api/missing?password=DO_NOT_LOG", headers={"Authorization":"Bearer TOKEN_CANARY"})
    assert response.status_code == 404
    assert response.is_json and response.json["error"] == "Not found."
    assert response.json["request_id"] == response.headers["X-Request-ID"]
    lines = [json.loads(x) for x in stream.getvalue().splitlines()]
    assert any(x["event"] == "request_complete" and x["status"] == 404 and x["request_id"] == response.json["request_id"] for x in lines)
    assert "DO_NOT_LOG" not in stream.getvalue() and "TOKEN_CANARY" not in stream.getvalue()


def test_unexpected_failure_is_safe_and_logged(tmp_path):
    app = create_app({"DATABASE":str(tmp_path/"fault.sqlite"),"TESTING":True,"LAB_MODE":True,"SESSION_COOKIE_SECURE":False})
    client = app.test_client()
    sign_in(client,"editor")
    stream = capture(app)
    response = client.get("/api/lab-fault", headers={"X-Request-ID":"caller-supplied"})
    assert response.status_code == 500
    assert response.json["error"] == "An unexpected error occurred."
    assert response.json["request_id"] == response.headers["X-Request-ID"]
    assert response.json["request_id"] != "caller-supplied"
    combined = response.get_data(as_text=True) + stream.getvalue()
    for secret in ["SYNTHETIC_SECRET", "SELECT *", "/srv/internal", "Classroom-Only-314!"]:
        assert secret not in combined
    events = [json.loads(x) for x in stream.getvalue().splitlines()]
    failure = next(x for x in events if x["event"] == "unexpected_error")
    assert failure["status"] == 500 and failure["exception_type"] == "RuntimeError"
    assert failure["request_id"] == response.json["request_id"]
    assert failure["location"].startswith("lab_fault:")


def test_request_body_and_tokens_not_logged(client, login, app):
    token = login()
    stream = capture(app)
    response = client.patch("/api/notes/2", json={"content":"PRIVATE_NOTE_CANARY"}, headers={"X-CSRF-Token":token, "Authorization":"Bearer AUTH_CANARY"})
    assert response.status_code == 200
    log = stream.getvalue()
    assert log, "A request_complete event must be recorded."
    for value in ["PRIVATE_NOTE_CANARY", "AUTH_CANARY", token]:
        assert value not in log
    record = json.loads(log.splitlines()[-1])
    assert set(record) == {"timestamp","event","status","request_id","endpoint"}


def test_method_error_preserves_allow(client, login):
    login()
    response = client.delete("/api/notes/2")
    assert response.status_code == 405
    assert "GET" in response.headers["Allow"]
    assert response.json["error"] == "Method not allowed."


def test_request_setup_failure_keeps_safe_correlation(client, login, app, monkeypatch):
    # A database lookup can fail before a route starts. Correlation must
    # already exist so the failure handler can safely produce its response.
    import app as app_module
    login()
    stream = capture(app)
    def failed_lookup(user_id):
        raise RuntimeError("DATABASE_SECRET_CANARY")
    monkeypatch.setattr(app_module, "user_by_id", failed_lookup)
    response = client.get("/api/notes/2")
    assert response.status_code == 500
    assert response.json["error"] == "An unexpected error occurred."
    assert response.json["request_id"] == response.headers["X-Request-ID"]
    assert "DATABASE_SECRET_CANARY" not in response.get_data(as_text=True) + stream.getvalue()
    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    assert any(event["event"] == "unexpected_error" and event["request_id"] == response.json["request_id"] for event in events)
