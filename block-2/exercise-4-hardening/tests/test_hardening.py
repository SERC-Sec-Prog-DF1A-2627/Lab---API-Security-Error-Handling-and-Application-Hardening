from lab_client import sign_in


def test_headers_on_success_and_error(client, login):
    login()
    for path in ["/", "/api/notes/2", "/api/missing"]:
        response = client.get(path)
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("Referrer-Policy") == "no-referrer"
        csp = response.headers.get("Content-Security-Policy", "")
        for directive in ["default-src 'self'", "script-src 'none'", "object-src 'none'", "frame-ancestors 'none'", "form-action 'self'"]:
            assert directive in csp
        assert response.headers["Cache-Control"] == "no-store"


def test_sixth_request_limited_and_retry_header(client, login):
    login()
    responses = [client.get("/api/notes/2") for _ in range(6)]
    assert [r.status_code for r in responses] == [200,200,200,200,200,429]
    last = responses[-1]
    assert last.json["error"] == "Too many requests."
    assert 0 <= int(last.headers["Retry-After"]) <= 60
    assert last.headers["X-Content-Type-Options"] == "nosniff"


def test_budget_separate_by_authenticated_user(app):
    first = app.test_client(); second = app.test_client()
    sign_in(first,"editor"); sign_in(second,"other_editor")
    for _ in range(5):
        assert first.get("/api/notes/2").status_code == 200
    assert first.get("/api/notes/2").status_code == 429
    assert second.get("/api/notes/3").status_code == 200


def test_supplied_forwarded_address_does_not_reset_budget(client, login):
    login()
    for i in range(5):
        assert client.get("/api/notes/2",headers={"X-Forwarded-For":f"192.0.2.{i}"}).status_code == 200
    assert client.get("/api/notes/2",headers={"X-Forwarded-For":"192.0.2.99"}).status_code == 429


def test_config_and_cookie(client, login, app):
    login()
    assert app.config["DEBUG"] is False
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["MAX_CONTENT_LENGTH"] == 16384
    # Fresh login page sets a session token and therefore a session cookie.
    fresh = app.test_client().get("/login")
    cookie = fresh.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie


def test_oversize_body_rejected(client, login):
    token = login()
    assert client.patch("/api/notes/2",json={"content":"x"*20000},headers={"X-CSRF-Token":token}).status_code == 413
