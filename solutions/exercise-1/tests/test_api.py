import pytest
from db import find_note


def test_get_own_note(client, login):
    login()
    response = client.get("/api/notes/2")
    assert response.status_code == 200
    assert response.json["id"] == 2
    assert set(response.json) == {"id","title","content"}


def test_get_anonymous(client):
    assert client.get("/api/notes/2").status_code == 401


@pytest.mark.parametrize("note_id", [3, 999])
def test_get_inaccessible(client, login, note_id):
    login()
    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 404
    assert response.json["error"] == "Not found."


def test_patch_success_persists_and_keeps_omitted_field(client, login, app):
    token = login()
    response = client.patch("/api/notes/2", json={"title":"Revised plan"}, headers={"X-CSRF-Token":token})
    assert response.status_code == 200
    with app.app_context():
        note = find_note(2)
        assert note["title"] == "Revised plan"
        assert note["content"] == "Draft for the teaching lab."
        assert note["owner_id"] == 2 and note["is_reviewed"] == 0


def test_patch_anonymous(client):
    assert client.patch("/api/notes/2", json={"title":"x"}).status_code == 401


@pytest.mark.parametrize("header", [{}, {"X-CSRF-Token":"wrong"}])
def test_patch_requires_csrf(client, login, app, header):
    login()
    assert client.patch("/api/notes/2", json={"title":"x"}, headers=header).status_code == 403
    with app.app_context():
        assert find_note(2)["title"] == "editor's plan"


def test_patch_viewer_denied(client, login, app):
    token = login("reader")
    response = client.patch("/api/notes/1", json={"title":"x"}, headers={"X-CSRF-Token":token})
    assert response.status_code == 403
    with app.app_context():
        assert find_note(1)["title"] == "reader's plan"


@pytest.mark.parametrize("note_id", [3,999])
def test_patch_inaccessible(client, login, app, note_id):
    token = login()
    assert client.patch(f"/api/notes/{note_id}", json={"title":"x"}, headers={"X-CSRF-Token":token}).status_code == 404
    with app.app_context():
        assert find_note(3)["title"] == "other_editor's plan"


@pytest.mark.parametrize("payload", [{"owner_id":3}, {"is_reviewed":1}, {"title":"Sneaky", "owner_id":3}, {"role":"admin"}])
def test_patch_rejects_protected_fields_atomically(client, login, app, payload):
    token = login()
    assert client.patch("/api/notes/2", json=payload, headers={"X-CSRF-Token":token}).status_code == 400
    with app.app_context():
        note = find_note(2)
        assert note["title"] == "editor's plan"
        assert note["owner_id"] == 2 and note["is_reviewed"] == 0


@pytest.mark.parametrize("payload", [[], ["x"], "x", 4, True, {}, {"title":42}, {"title":False}, {"title":None}, {"title":" "}, {"title":"x"*81}, {"content":"x"*2001}])
def test_patch_rejects_invalid_values(client, login, payload):
    token = login()
    assert client.patch("/api/notes/2", json=payload, headers={"X-CSRF-Token":token}).status_code == 400


@pytest.mark.parametrize("body,content_type,status", [('null','application/json',400), ('{broken','application/json',400), ('{"title":"x"}','text/plain',415)])
def test_patch_body_errors(client, login, body, content_type, status):
    token = login()
    response = client.patch("/api/notes/2", data=body, content_type=content_type, headers={"X-CSRF-Token":token})
    assert response.status_code == status


def test_admin_still_needs_ownership(client, login):
    token = login("admin")
    assert client.get("/api/notes/2").status_code == 404
    assert client.patch("/api/notes/2", json={"title":"x"}, headers={"X-CSRF-Token":token}).status_code == 404
    assert client.patch("/api/notes/4", json={"title":"OK"}, headers={"X-CSRF-Token":token}).status_code == 200


def test_unknown_role_api_denied(client, login, app):
    from db import get_db
    token = login()
    with app.app_context():
        get_db().execute("UPDATE users SET role='unknown' WHERE id=2")
        get_db().commit()
    assert client.get("/api/notes/2").status_code == 403
    assert client.patch("/api/notes/2", json={"title":"x"}, headers={"X-CSRF-Token":token}).status_code == 403
