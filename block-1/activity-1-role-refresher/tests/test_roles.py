import pytest
from security import can_edit_notes, owns_note


@pytest.mark.parametrize("role,expected", [("viewer",False),("editor",True),("admin",True),("unknown",False)])
def test_role_helper(role, expected):
    assert can_edit_notes({"role":role}) is expected


def test_no_user_denied():
    assert can_edit_notes(None) is False


def test_admin_does_not_override_owner():
    assert owns_note({"id":4,"role":"admin"},{"owner_id":2}) is False


def test_editor_web_and_api_agree(client, login):
    token = login()
    web = client.post("/notes/2/edit", data={"title":"Web", "content":"x", "csrf_token":token})
    api = client.patch("/api/notes/2", json={"title":"API"}, headers={"X-CSRF-Token":token})
    assert web.status_code == 302
    assert api.status_code == 200


def test_viewer_web_and_api_agree(client, login):
    token = login("reader")
    web = client.post("/notes/1/edit", data={"title":"Web", "content":"x", "csrf_token":token})
    api = client.patch("/api/notes/1", json={"title":"API"}, headers={"X-CSRF-Token":token})
    assert web.status_code == api.status_code == 403
