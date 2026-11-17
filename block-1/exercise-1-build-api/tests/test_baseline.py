from db import find_note


def test_login_and_web_page(client, login):
    login()
    response = client.get("/")
    assert response.status_code == 200
    assert b"editor's plan" in response.data or b"editor&#39;s plan" in response.data


def test_login_requires_csrf(client):
    assert client.post("/login", data={"username":"editor", "password":"Classroom-Only-314!"}).status_code == 403


def test_viewer_web_update_denied(client, login, app):
    token = login("reader")
    response = client.post("/notes/1/edit", data={"title":"Changed", "content":"x", "csrf_token":token})
    assert response.status_code == 403
    with app.app_context():
        assert find_note(1)["title"] == "reader's plan"


def test_unknown_role_is_denied(client, login, app):
    from db import get_db
    token = login()
    with app.app_context():
        get_db().execute("UPDATE users SET role='unknown' WHERE id=2")
        get_db().commit()
    assert client.get("/").status_code == 403


def test_fault_route_disabled(client, login):
    login()
    assert client.get("/api/lab-fault").status_code == 404
